"""Guard refusal tests (AT-M0-T02-07)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from cenomi.db.guards import DbOperation, GuardContext, GuardFailure, enforce_guards, refuse_guard

REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("url", "operation", "extra_env", "guard"),
    [
        (
            "postgresql://postgres:x@evil.example.com:5432/cenomi_dev",
            DbOperation.INIT,
            {},
            "DG-1",
        ),
        (
            "postgresql://cenomi_owner:x@localhost:5432/production_db",
            DbOperation.MIGRATE,
            {"CENOMI_ENV": "dev"},
            "DG-2",
        ),
        (
            "postgresql://cenomi_owner:x@localhost:5432/cenomi_dev",
            DbOperation.MIGRATE,
            {"CENOMI_ENV": "production"},
            "DG-3",
        ),
        (
            "postgresql://cenomi_reader:x@localhost:5432/cenomi_dev",
            DbOperation.MIGRATE,
            {"CENOMI_ENV": "dev"},
            "DG-5",
        ),
    ],
)
@pytest.mark.trace("AT-M0-T02-07", reqs=["ARCH-R064"])
def test_enforce_guards_refuses(
    url: str,
    operation: DbOperation,
    extra_env: dict[str, str],
    guard: str,
) -> None:
    ctx = GuardContext(url=url, operation=operation)
    with patch.dict(os.environ, extra_env, clear=False):
        with pytest.raises(GuardFailure) as exc_info:
            enforce_guards(ctx)
    assert exc_info.value.guard == guard


@pytest.mark.unit
@pytest.mark.trace("AT-M0-T02-07", reqs=["ARCH-R064"])
def test_dg4_refuses_without_confirm() -> None:
    ctx = GuardContext(
        url="postgresql://cenomi_owner:x@localhost:5432/cenomi_test",
        operation=DbOperation.DOWNGRADE,
        require_confirm=True,
    )
    with patch.dict(os.environ, {"CENOMI_ENV": "dev", "CONFIRM": ""}, clear=False):
        with patch.object(sys.stdin, "isatty", return_value=False):
            with pytest.raises(GuardFailure) as exc_info:
                enforce_guards(ctx)
    assert exc_info.value.guard == "DG-4"


@pytest.mark.unit
@pytest.mark.trace("AT-M0-T02-07", reqs=["ARCH-R064"])
def test_refuse_guard_exits_two() -> None:
    with pytest.raises(SystemExit) as exc_info:
        refuse_guard("DG-1", "host not allowed")
    assert exc_info.value.code == 2


@pytest.mark.unit
@pytest.mark.trace("AT-M0-T02-07", reqs=["ARCH-R064"])
def test_cli_db_init_exits_two_on_dg1() -> None:
    env = os.environ.copy()
    env["CENOMI_ENV"] = "dev"
    env["DATABASE_URL_ADMIN"] = (
        "postgresql://postgres:change-me-dev-only-admin@evil.example.com:5432/postgres"
    )
    env.setdefault(
        "DATABASE_URL_ADMIN",
        "postgresql://postgres:change-me-dev-only-admin@127.0.0.1:5432/postgres",
    )
    env.setdefault(
        "DATABASE_URL_OWNER",
        "postgresql://cenomi_owner:change-me-dev-only-owner@127.0.0.1:5432/cenomi_dev",
    )
    env.setdefault(
        "DATABASE_URL_SEED",
        "postgresql://cenomi_seed:change-me-dev-only-seed@127.0.0.1:5432/cenomi_dev",
    )
    env.setdefault(
        "DATABASE_URL_READER",
        "postgresql://cenomi_reader:change-me-dev-only-reader@127.0.0.1:5432/cenomi_dev",
    )
    env.setdefault(
        "DATABASE_URL_APP",
        "postgresql://cenomi_app:change-me-dev-only-app@127.0.0.1:5432/cenomi_dev",
    )
    env.setdefault("CENOMI_DATASET_ID", "sd-2026.10.20-01")
    env.setdefault("CENOMI_AS_OF", "2026-10-20")
    env.setdefault("CENOMI_TZ", "Asia/Riyadh")
    env.setdefault("AUTH_MODE", "dev_fixture")
    env.setdefault("SESSION_SECRET", "change-me-dev-only-session-secret-32b")
    env.setdefault("API_INTERNAL_URL", "http://localhost:8000")
    completed = subprocess.run(
        ["uv", "run", "--directory", "backend", "cenomi", "db", "init"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 2
