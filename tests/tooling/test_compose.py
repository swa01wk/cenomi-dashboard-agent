"""Docker Compose stack tooling tests (AT-M0-T02-01, AT-M0-T02-10)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
HEAD_REVISION = "0001_m0_schemas_and_grants"


def _docker_available() -> bool:
    return shutil.which("docker") is not None


def _ensure_repo_env_file() -> None:
    env_path = REPO_ROOT / ".env"
    if env_path.is_file():
        return
    setup = subprocess.run(
        ["make", "setup"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert setup.returncode == 0, setup.stdout + setup.stderr
    assert env_path.is_file(), "make setup did not create .env"


def _run_make(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        ["make", *args],
        cwd=REPO_ROOT,
        env=merged,
        capture_output=True,
        text=True,
        check=False,
    )


def _compose_config(
    env: dict[str, str] | None = None, *, profiles: tuple[str, ...] = ()
) -> dict:
    _ensure_repo_env_file()
    merged = os.environ.copy()
    if env:
        merged.update(env)
    cmd = ["docker", "compose"]
    for profile in profiles:
        cmd.extend(["--profile", profile])
    cmd.extend(["config", "--format", "json"])
    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=merged,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def _service_environment(config: dict, service: str) -> dict[str, str]:
    raw = config.get("services", {}).get(service, {}).get("environment") or {}
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    parsed: dict[str, str] = {}
    for entry in raw:
        if isinstance(entry, str) and "=" in entry:
            key, value = entry.split("=", 1)
            parsed[key] = value
    return parsed


@pytest.mark.trace("AT-M0-T02-10", reqs=["DEVENV-R005", "ARCH-R002"])
def test_compose_in_container_database_urls_ignore_host_shell() -> None:
    bogus = {
        "CENOMI_ENV": "ci",
        "DATABASE_URL_READER": "postgresql://x:y@localhost:1/z",
        "DATABASE_URL_APP": "postgresql://x:y@localhost:1/z",
        "DATABASE_URL_OWNER": "postgresql://x:y@localhost:1/z",
    }
    api_env = _service_environment(_compose_config(bogus), "api")
    migrate_env = _service_environment(
        _compose_config(bogus, profiles=("setup",)),
        "migrate",
    )
    assert api_env.get("CENOMI_ENV") == "dev"
    for key in ("DATABASE_URL_READER", "DATABASE_URL_APP"):
        url = api_env.get(key, "")
        assert "@db:5432/" in url, f"{key} must target compose db service: {url!r}"
        assert "localhost" not in url
    for key in (
        "DATABASE_URL_ADMIN",
        "DATABASE_URL_OWNER",
        "DATABASE_URL_READER",
        "DATABASE_URL_APP",
    ):
        url = migrate_env.get(key, "")
        assert "@db:5432/" in url, f"migrate {key} must target compose db service: {url!r}"
        assert "localhost" not in url


@pytest.mark.trace("AT-M0-T02-10", reqs=["DEVENV-R005", "ARCH-R002"])
def test_compose_published_ports_bind_localhost_only() -> None:
    config = _compose_config()
    services = config.get("services", {})
    for name in ("db", "api"):
        service = services[name]
        ports = service.get("ports") or []
        assert ports, f"{name} must publish ports"
        for entry in ports:
            if isinstance(entry, dict):
                host = entry.get("host_ip") or entry.get("published")
            else:
                host = str(entry).split(":")[0]
            assert host in ("127.0.0.1", "::1"), f"{name} port must bind to loopback: {entry}"


@pytest.mark.trace("AT-M0-T02-01", reqs=["DEVENV-R005", "ARCH-R057"])
@pytest.mark.skipif(not _docker_available(), reason="Docker not available")
def test_01_make_up_on_clean_volume() -> None:
    _ensure_repo_env_file()
    down = _run_make("down", "VOLUMES=1", "CONFIRM=yes")
    assert down.returncode == 0, down.stderr
    up = _run_make("up")
    assert up.returncode == 0, up.stdout + up.stderr
    ps_db = subprocess.run(
        ["docker", "compose", "ps", "--format", "json", "db"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    ps_api = subprocess.run(
        ["docker", "compose", "ps", "--format", "json", "api"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    db_health = json.loads(ps_db.stdout.strip().splitlines()[-1]).get("Health")
    api_health = json.loads(ps_api.stdout.strip().splitlines()[-1]).get("Health")
    assert db_health == "healthy"
    assert api_health == "healthy"
    current = _run_make("db-current", "DB=dev")
    assert current.returncode == 0
    assert HEAD_REVISION in current.stdout


@pytest.mark.trace("AT-M0-T02-10", reqs=["ARCH-R002"])
@pytest.mark.skipif(not _docker_available(), reason="Docker not available")
def test_02_api_container_runs_as_non_root() -> None:
    _ensure_repo_env_file()
    running = subprocess.run(
        ["docker", "compose", "ps", "--format", "json", "api"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert running.returncode == 0 and running.stdout.strip(), (
        "api container must be running (run after test_01_make_up_on_clean_volume)"
    )
    payload = json.loads(running.stdout.strip().splitlines()[-1])
    container_id = payload.get("ID") or payload.get("Id")
    assert container_id, "could not resolve api container id"
    inspect = subprocess.run(
        ["docker", "inspect", container_id, "--format", "{{.Config.User}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert inspect.returncode == 0
    user = inspect.stdout.strip()
    assert user and user not in ("0", "root", "")


def test_compose_db_image_digest_pinned() -> None:
    text = COMPOSE_FILE.read_text(encoding="utf-8")
    assert (
        "postgres:16.15@sha256:9e2cf6287f25c3151f4c9421ccce2b17f3e60061c111a29165e0d2cdd9ff0a97"
        in text
    )


def test_compose_defines_seed_and_otel_profile() -> None:
    raw = yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))
    assert "seed" in raw["services"]
    assert "otel" in raw["services"]
    assert "observability" in raw["services"]["otel"].get("profiles", [])
