"""Dispatch Make targets for M0-T01 (orchestration only; logic lives in scripts/)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

MAKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MAKE_DIR.parents[1]
BACKEND = REPO_ROOT / "backend"

if str(MAKE_DIR) not in sys.path:
    sys.path.insert(0, str(MAKE_DIR))

from doctor import run_doctor
from help_text import render_help
from report import (
    TargetRun,
    failed,
    milestone_index,
    not_applicable,
    not_implemented,
    passed,
    read_active_milestone,
)
from targets import TARGET_BY_NAME, TargetMeta

STUB_REASON = "implemented in a later M0 task card"
HEAD_REVISION = "0001_m0_schemas_and_grants"
COMPOSE_HEALTH_TIMEOUT_S = 120


def _shell(cmd: str, *, cwd: Path | None = None) -> int:
    print(f"+ {cmd}", flush=True)
    return subprocess.run(cmd, shell=True, cwd=cwd or REPO_ROOT, check=False).returncode


def _shell_with_repo_env(cmd: str, *, cwd: Path | None = None) -> int:
    """Load the repo-root `.env` before running database CLI commands."""
    wrapped = f"set -a; [ -f .env ] && . ./.env; set +a; {cmd}"
    print(f"+ {wrapped}", flush=True)
    return subprocess.run(
        wrapped,
        shell=True,
        executable="/bin/bash",
        cwd=cwd or REPO_ROOT,
        check=False,
    ).returncode


def _resolve(meta: TargetMeta, run: TargetRun) -> None:
    active = read_active_milestone()
    if milestone_index(meta.active_from) > milestone_index(active):
        reason = meta.reason_until_active or "milestone rule"
        not_applicable(meta.name, meta.active_from, reason, run)
        return


def _stub(meta: TargetMeta, run: TargetRun) -> None:
    _resolve(meta, run)
    not_implemented(meta.name, STUB_REASON, run, active_from=meta.active_from)


def _guard_down(run: TargetRun) -> bool:
    volumes = os.environ.get("VOLUMES", "0").strip()
    confirm = os.environ.get("CONFIRM", "").strip()
    if volumes == "1" and confirm != "yes":
        failed(
            "down",
            "refused: VOLUMES=1 requires CONFIRM=yes",
            run,
            exit_code=2,
        )
        return False
    return True


def _db_selector() -> str:
    db = os.environ.get("DB", "dev").strip().lower()
    if db not in ("dev", "test"):
        return db
    return db


def _alembic_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("DB", _db_selector())
    return env


def _run_alembic(subcmd: str, run: TargetRun, *, name: str) -> int:
    inner = f"uv run alembic {subcmd}"
    cmd = f"set -a; [ -f ../.env ] && . ../.env; set +a; {inner}"
    print(f"+ {cmd}", flush=True)
    completed = subprocess.run(
        cmd,
        shell=True,
        executable="/bin/bash",
        cwd=BACKEND,
        env=_alembic_env(),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.stdout:
        print(completed.stdout, end="", flush=True)
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr, flush=True)
    if completed.returncode != 0:
        failed(name, f"alembic {subcmd} failed", run, exit_code=completed.returncode)
        return completed.returncode
    return 0


def _compose(*args: str) -> int:
    quoted = " ".join(args)
    return _shell(f"docker compose {quoted}")


def _compose_service_health(service: str) -> str | None:
    completed = subprocess.run(
        ["docker", "compose", "ps", "--format", "json", service],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except json.JSONDecodeError:
        return None
    health = payload.get("Health")
    if isinstance(health, str):
        return health
    return None


def _wait_compose_healthy(
    service: str, timeout_s: int = COMPOSE_HEALTH_TIMEOUT_S
) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        status = _compose_service_health(service)
        if status == "healthy":
            return True
        time.sleep(2)
    return False


def _print_compose_logs(service: str, *, tail: int = 50) -> None:
    print(f"--- docker compose logs --tail {tail} {service} ---", flush=True)
    subprocess.run(
        ["docker", "compose", "logs", "--tail", str(tail), service],
        cwd=REPO_ROOT,
        check=False,
    )


def _print_compose_ps() -> None:
    print("--- docker compose ps ---", flush=True)
    subprocess.run(["docker", "compose", "ps"], cwd=REPO_ROOT, check=False)


def _print_compose_failure_diagnostics() -> None:
    _print_compose_logs("api")
    _print_compose_logs("db")
    _print_compose_ps()


def _wait_api_health_ok(timeout_s: int = COMPOSE_HEALTH_TIMEOUT_S) -> bool:
    deadline = time.monotonic() + timeout_s
    url = "http://127.0.0.1:8000/api/v1/health"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status == 200:
                    body = json.loads(response.read().decode("utf-8"))
                    if body.get("status") == "ok":
                        return True
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            pass
        time.sleep(2)
    return False


def _guard_db_downgrade(run: TargetRun) -> bool:
    rev = os.environ.get("REV", "").strip()
    confirm = os.environ.get("CONFIRM", "").strip()
    if not rev or confirm != "yes":
        failed(
            "db-downgrade",
            "refused: REV is required and CONFIRM must be yes",
            run,
            exit_code=2,
        )
        return False
    return True


def run_target(name: str) -> None:
    meta = TARGET_BY_NAME.get(name)
    if meta is None:
        print(f"Unknown target: {name}", file=sys.stderr)
        sys.exit(2)

    run = TargetRun(name)

    if name == "help":
        print(render_help(), end="")
        passed(name, "listed targets from Makefile summaries", run)
        return

    if name == "doctor":
        ok, mismatches = run_doctor()
        if ok:
            passed(name, "toolchain matches pinned versions", run)
        else:
            failed(name, f"mismatch: {', '.join(mismatches)}", run, exit_code=3)
        return

    if name == "setup":
        code = _shell("make doctor")
        if code != 0:
            failed(name, "doctor failed", run, exit_code=code)
            return
        env = REPO_ROOT / ".env"
        example = REPO_ROOT / ".env.example"
        if not env.is_file() and example.is_file():
            print(f"+ cp {example} {env}", flush=True)
            shutil.copyfile(example, env)
        code = _shell("make install")
        if code != 0:
            failed(name, "install failed", run, exit_code=code)
            return
        passed(name, "doctor, .env bootstrap and install completed", run)
        return

    if name == "install":
        browsers = os.environ.get("BROWSERS", "1").strip()
        code = _shell("uv sync --locked --directory backend --all-groups")
        if code != 0:
            failed(
                name,
                "uv sync --locked failed (lockfile out of date?)",
                run,
                exit_code=1,
            )
            return
        code = _shell("pnpm install --frozen-lockfile")
        if code != 0:
            failed(name, "pnpm install --frozen-lockfile failed", run, exit_code=1)
            return
        if browsers == "1":
            code = _shell("pnpm exec playwright install --with-deps chromium")
            if code != 0:
                failed(name, "playwright browser install failed", run, exit_code=1)
                return
        passed(name, "locked backend and web dependencies installed", run)
        return

    if name == "clean":
        paths = [
            REPO_ROOT / "apps/web/.next",
            REPO_ROOT / ".pytest_cache",
            REPO_ROOT / ".mypy_cache",
            REPO_ROOT / ".ruff_cache",
            REPO_ROOT / "tests/reports",
        ]
        paths.extend((REPO_ROOT / "packages").glob("*/dist"))
        for path in paths:
            if path.is_dir():
                print(f"+ rm -rf {path}", flush=True)
                shutil.rmtree(path, ignore_errors=True)
            elif path.is_file():
                print(f"+ rm -f {path}", flush=True)
                path.unlink(missing_ok=True)
        passed(name, "removed build outputs and caches", run)
        return

    if name == "up":
        _resolve(meta, run)
        for step in ("docker compose build db api migrate",):
            if _shell(step) != 0:
                failed(name, "docker compose build failed", run, exit_code=1)
                return
        if _compose("up", "-d", "db") != 0:
            failed(name, "failed to start db", run, exit_code=1)
            return
        if not _wait_compose_healthy("db"):
            _print_compose_logs("db")
            _print_compose_ps()
            failed(name, "db did not become healthy within 120s", run, exit_code=1)
            return
        if _shell("make db-init") != 0:
            failed(name, "db-init failed", run, exit_code=1)
            return
        if _compose("--profile", "setup", "run", "--rm", "migrate") != 0:
            _print_compose_logs("migrate")
            failed(name, "migrate service failed", run, exit_code=1)
            return
        if _compose("up", "-d", "api") != 0:
            failed(name, "failed to start api", run, exit_code=1)
            return
        if not _wait_compose_healthy("api") or not _wait_api_health_ok():
            _print_compose_failure_diagnostics()
            failed(name, "api did not become healthy within 120s", run, exit_code=1)
            return
        passed(name, "db and api healthy with migrations at head", run)
        return

    if name == "down":
        _resolve(meta, run)
        if not _guard_down(run):
            return
        volumes = os.environ.get("VOLUMES", "0").strip()
        if volumes == "1":
            code = _compose("down", "--volumes")
        else:
            code = _compose("down")
        if code != 0:
            failed(name, "docker compose down failed", run, exit_code=code)
            return
        passed(name, "stack stopped", run)
        return

    if name == "logs":
        _resolve(meta, run)
        service = os.environ.get("SERVICE", "").strip()
        follow = os.environ.get("FOLLOW", "1").strip()
        args = ["logs"]
        if follow == "1":
            args.append("-f")
        else:
            args.append("--no-log-prefix")
        if service:
            args.append(service)
        code = _compose(*args)
        if code != 0:
            failed(
                name,
                "docker compose logs failed (is the stack running?)",
                run,
                exit_code=3,
            )
            return
        passed(name, "container logs collected", run)
        return

    if name == "db-init":
        _resolve(meta, run)
        code = _shell_with_repo_env("uv run --project backend cenomi db init")
        if code == 2:
            failed(name, "refused by database guard", run, exit_code=2)
            return
        if code == 3:
            failed(name, "database unreachable", run, exit_code=3)
            return
        if code != 0:
            failed(name, "cenomi db init failed", run, exit_code=code)
            return
        passed(name, "roles and databases ensured", run)
        return

    if name == "db-upgrade":
        _resolve(meta, run)
        if _run_alembic("upgrade head", run, name=name) != 0:
            return
        passed(name, f"alembic upgrade head (DB={_db_selector()})", run)
        return

    if name == "db-current":
        _resolve(meta, run)
        inner = "uv run alembic current --verbose"
        cmd = f"set -a; [ -f ../.env ] && . ../.env; set +a; {inner}"
        print(f"+ {cmd}", flush=True)
        completed = subprocess.run(
            cmd,
            shell=True,
            executable="/bin/bash",
            cwd=BACKEND,
            env=_alembic_env(),
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.stdout:
            print(completed.stdout, end="", flush=True)
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr, flush=True)
        if completed.returncode != 0:
            failed(name, "alembic current failed", run, exit_code=1)
            return
        at_head = HEAD_REVISION in completed.stdout and "(head)" in completed.stdout
        if not at_head:
            failed(
                name,
                f"database is not at head ({HEAD_REVISION})",
                run,
                exit_code=1,
            )
            return
        passed(name, f"at head revision {HEAD_REVISION}", run)
        return

    if name == "db-check":
        _resolve(meta, run)
        if _run_alembic("check", run, name=name) != 0:
            return
        db = _db_selector()
        verify = _shell_with_repo_env(
            f"uv run --project backend cenomi db verify-roles --db {db}"
        )
        if verify != 0:
            failed(name, "verify-roles failed", run, exit_code=verify)
            return
        passed(name, "no drift and roles verified", run)
        return

    if name == "db-history":
        _resolve(meta, run)
        if _run_alembic("history --verbose", run, name=name) != 0:
            return
        passed(name, "migration history printed", run)
        return

    if name == "db-downgrade":
        _resolve(meta, run)
        if not _guard_db_downgrade(run):
            return
        rev = os.environ.get("REV", "").strip()
        if _run_alembic(f'downgrade "{rev}"', run, name=name) != 0:
            return
        passed(name, f"downgraded to {rev}", run)
        return

    if name == "backend-format":
        _resolve(meta, run)
        code = _shell("uv run ruff format backend scripts")
        if code != 0:
            failed(name, "ruff format failed", run, exit_code=code)
            return
        code = _shell("uv run ruff check --select I --fix backend scripts")
        if code != 0:
            failed(name, "ruff import fix failed", run, exit_code=code)
            return
        passed(name, "backend formatting applied", run)
        return

    if name == "backend-lint":
        _resolve(meta, run)
        for cmd in (
            "uv run ruff check backend scripts",
            "uv run ruff format --check backend scripts",
            "uv run --directory backend import-linter lint",
            "uv run python scripts/lint/sql_safety.py",
        ):
            code = _shell(cmd)
            if code != 0:
                failed(name, f"failed: {cmd}", run, exit_code=code)
                return
        passed(name, "backend static checks passed", run)
        return

    if name == "backend-typecheck":
        _resolve(meta, run)
        code = _shell(
            "uv run --directory backend mypy --strict --explicit-package-bases src ../scripts"
        )
        if code != 0:
            failed(name, "mypy failed", run, exit_code=code)
            return
        passed(name, "backend typecheck passed", run)
        return

    if name == "backend-test":
        _resolve(meta, run)
        suite = os.environ.get("SUITE", "all").strip()
        k_expr = os.environ.get("K", "").strip()
        reports = REPO_ROOT / "tests" / "reports" / "backend"
        reports.mkdir(parents=True, exist_ok=True)

        def _pytest(args: str, *, clear_makeflags: bool = False) -> int:
            cmd = f"uv run --directory backend pytest {args}"
            if not clear_makeflags:
                return _shell(cmd)
            env = os.environ.copy()
            env.pop("MAKEFLAGS", None)
            env.pop("MFLAGS", None)
            env["MAKELEVEL"] = "0"
            print(f"+ {cmd}", flush=True)
            return subprocess.run(
                cmd, shell=True, cwd=REPO_ROOT, env=env, check=False
            ).returncode

        if suite in ("unit", "all"):
            k_flag = f"-k {k_expr!r} " if k_expr else ""
            code = _pytest(
                f"tests/unit {k_flag}"
                f"--junitxml={reports / 'junit-unit.xml'} "
                f"--cov=cenomi --cov-report=xml:{reports / 'coverage.xml'}"
            )
            if code != 0:
                failed(name, "unit tests failed", run, exit_code=code)
                return
        if suite in ("integration", "all"):
            if suite == "integration" or suite == "all":
                code = _shell("make db-upgrade DB=test")
                if code not in (0,):
                    failed(
                        name,
                        "db-upgrade DB=test failed (database unreachable?)",
                        run,
                        exit_code=3,
                    )
                    return
            k_flag = f"-k {k_expr!r} " if k_expr else ""
            code = _pytest(
                f"tests/integration -m 'not agent_live' {k_flag}"
                f"--junitxml={reports / 'junit-integration.xml'}"
            )
            if code != 0:
                failed(name, "integration tests failed", run, exit_code=code)
                return
        if suite == "tooling":
            junit = reports / "junit-tooling.xml"
            code = _pytest(
                "-c pyproject.toml --rootdir=.. --confcutdir=.. "
                f"../tests/tooling --junitxml={junit}",
                clear_makeflags=True,
            )
            if code != 0:
                failed(name, "tooling tests failed", run, exit_code=code)
                return
            passed(name, "backend tests passed (SUITE=tooling)", run)
            return
        if suite not in ("unit", "integration", "all"):
            failed(name, f"unknown SUITE={suite!r}", run, exit_code=2)
            return
        passed(name, f"backend tests passed (SUITE={suite})", run)
        return

    if name == "specs-check":
        _resolve(meta, run)
        gate = os.environ.get("GATE", "").strip()
        env_prefix = f"GATE={gate} " if gate else ""
        code = _shell(
            f"{env_prefix}uv run --directory backend python ../scripts/specs/check.py"
        )
        if code != 0:
            failed(name, "specs-check reported findings", run, exit_code=code)
            return
        passed(name, "specifications and engineering metadata validated", run)
        return

    if name == "trace-report":
        _resolve(meta, run)
        card = os.environ.get("CARD", "").strip()
        gate = os.environ.get("GATE", "").strip()
        env_parts = []
        if card:
            env_parts.append(f"CARD={card}")
        if gate:
            env_parts.append(f"GATE={gate}")
        env_prefix = " ".join(env_parts)
        if env_prefix:
            env_prefix += " "
        code = _shell(
            f"{env_prefix}uv run --directory backend python ../scripts/trace/report.py"
        )
        if code != 0:
            failed(name, "trace-report failed", run, exit_code=code)
            return
        passed(name, "trace report generated", run)
        return

    if name == "security-check":
        _resolve(meta, run)
        code = _shell("uv run --directory backend python ../scripts/specs/security.py")
        if code != 0:
            failed(name, "security-check failed", run, exit_code=code)
            return
        passed(name, "security scan and audits passed", run)
        return

    if name == "ci":
        _resolve(meta, run)
        code = subprocess.run(
            [
                "uv",
                "run",
                "--project",
                "backend",
                "python",
                "scripts/ci/make_ci.py",
            ],
            cwd=REPO_ROOT,
            check=False,
        ).returncode
        job = os.environ.get("JOB", "").strip() or "all"
        if code == 0:
            passed(name, f"JOB={job} completed", run)
        else:
            failed(name, f"JOB={job} failed", run, exit_code=code)
        return

    if name == "check":
        _resolve(meta, run)
        steps = [
            "backend-lint",
            "backend-typecheck",
            "frontend-lint",
            "frontend-typecheck",
            "contracts-check",
            "specs-check",
            "backend-test SUITE=unit",
            "frontend-test",
        ]
        for step in steps:
            code = _shell(f"make {step}")
            if code != 0:
                failed(name, f"failed at {step}", run, exit_code=code)
                return
        passed(name, "all in-check targets completed", run)
        return

    if meta.implemented:
        _resolve(meta, run)

    _stub(meta, run)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: invoke.py <target>", file=sys.stderr)
        sys.exit(2)
    run_target(sys.argv[1])


if __name__ == "__main__":
    main()
