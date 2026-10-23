#!/usr/bin/env python3
"""Dispatch Make targets for M0-T01 (orchestration only; logic lives in scripts/)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MAKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MAKE_DIR.parents[1]
BACKEND = REPO_ROOT / "backend"

if str(MAKE_DIR) not in sys.path:
    sys.path.insert(0, str(MAKE_DIR))

from doctor import run_doctor  # noqa: E402
from help_text import render_help  # noqa: E402
from report import (  # noqa: E402
    TargetRun,
    failed,
    milestone_index,
    not_applicable,
    not_implemented,
    passed,
    read_active_milestone,
)
from targets import TARGET_BY_NAME, TargetMeta  # noqa: E402

STUB_REASON = "implemented in a later M0 task card"


def _shell(cmd: str, *, cwd: Path | None = None) -> int:
    print(f"+ {cmd}", flush=True)
    return subprocess.run(cmd, shell=True, cwd=cwd or REPO_ROOT, check=False).returncode


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
            failed(name, "uv sync --locked failed (lockfile out of date?)", run, exit_code=1)
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
        for pkg in (REPO_ROOT / "packages").glob("*/dist"):
            paths.append(pkg)
        for path in paths:
            if path.is_dir():
                print(f"+ rm -rf {path}", flush=True)
                shutil.rmtree(path, ignore_errors=True)
            elif path.is_file():
                print(f"+ rm -f {path}", flush=True)
                path.unlink(missing_ok=True)
        passed(name, "removed build outputs and caches", run)
        return

    if name == "down":
        _resolve(meta, run)
        if not _guard_down(run):
            return
        _stub(meta, run)
        return

    if name == "db-downgrade":
        _resolve(meta, run)
        if not _guard_db_downgrade(run):
            return
        _stub(meta, run)
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
