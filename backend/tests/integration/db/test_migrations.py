"""Alembic migration integration tests (AT-M0-T02-08)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
HEAD = "0001_m0_schemas_and_grants"


def _run_make(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", *args],
        cwd=REPO_ROOT,
        env={**os.environ, "CENOMI_ENV": os.environ.get("CENOMI_ENV", "test"), "DB": "test"},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.trace("AT-M0-T02-08", reqs=["ARCH-R057", "ARCH-R061"])
def test_db_init_idempotent_and_db_check_passes() -> None:
    first = _run_make("db-init")
    assert first.returncode == 0, first.stderr
    second = _run_make("db-init")
    assert second.returncode == 0, second.stderr
    upgrade = _run_make("db-upgrade", "DB=test")
    assert upgrade.returncode == 0, upgrade.stderr
    check = _run_make("db-check", "DB=test")
    assert check.returncode == 0, check.stdout + check.stderr


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.trace("AT-M0-T02-08", reqs=["ARCH-R057"])
def test_alembic_current_reports_head() -> None:
    current = _run_make("db-current", "DB=test")
    assert current.returncode == 0, current.stderr
    assert HEAD in current.stdout
