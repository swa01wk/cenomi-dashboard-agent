"""Docker Compose stack tooling tests (AT-M0-T02-01, AT-M0-T02-10)."""

from __future__ import annotations

import json
import os
import re
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


def _compose_config() -> dict:
    _ensure_repo_env_file()
    completed = subprocess.run(
        ["docker", "compose", "config", "--format", "json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


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


@pytest.mark.trace("AT-M0-T02-10", reqs=["ARCH-R002"])
@pytest.mark.skipif(not _docker_available(), reason="Docker not available")
def test_api_container_runs_as_non_root() -> None:
    _ensure_repo_env_file()
    running = subprocess.run(
        ["docker", "compose", "ps", "--format", "json", "api"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if running.returncode != 0 or not running.stdout.strip():
        pytest.skip("api container is not running")
    payload = json.loads(running.stdout.strip().splitlines()[-1])
    container_id = payload.get("ID") or payload.get("Id")
    if not container_id:
        pytest.skip("could not resolve api container id")
    inspect = subprocess.run(
        ["docker", "inspect", container_id, "--format", "{{.Config.User}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert inspect.returncode == 0
    user = inspect.stdout.strip()
    assert user and user not in ("0", "root", "")


@pytest.mark.trace("AT-M0-T02-01", reqs=["DEVENV-R005", "ARCH-R057"])
@pytest.mark.skipif(not _docker_available(), reason="Docker not available")
def test_make_up_on_clean_volume() -> None:
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
