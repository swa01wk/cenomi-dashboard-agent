"""Settings startup validation tests."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND = REPO_ROOT / "backend"


def _valid_env(**overrides: str) -> dict[str, str]:
    base = {
        "CENOMI_ENV": "test",
        "DATABASE_URL_ADMIN": "postgresql://postgres:change-me-dev-only-admin@localhost:5432/postgres",
        "DATABASE_URL_OWNER": "postgresql://cenomi_owner:change-me-dev-only-owner@localhost:5432/cenomi_dev",
        "DATABASE_URL_SEED": "postgresql://cenomi_seed:change-me-dev-only-seed@localhost:5432/cenomi_dev",
        "DATABASE_URL_READER": "postgresql://cenomi_reader:change-me-dev-only-reader@localhost:5432/cenomi_dev",
        "DATABASE_URL_APP": "postgresql://cenomi_app:change-me-dev-only-app@localhost:5432/cenomi_dev",
        "CENOMI_DATASET_ID": "sd-2026.10.20-01",
        "CENOMI_AS_OF": "2026-10-20",
        "CENOMI_TZ": "Asia/Riyadh",
        "AUTH_MODE": "dev_fixture",
        "SESSION_SECRET": "change-me-dev-only-session-secret-32b",
        "API_INTERNAL_URL": "http://localhost:8000",
    }
    base.update(overrides)
    return base


def _load_settings_subprocess(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    code = """
from cenomi.core.settings import load_settings
load_settings()
print("ok")
"""
    merged = os.environ.copy()
    for key in list(merged.keys()):
        if key.startswith(
            ("CENOMI_", "DATABASE_", "AUTH_", "SESSION_", "API_INTERNAL", "LLM_", "OTEL_", "LOG_")
        ):
            merged.pop(key, None)
    merged.update(env)
    return subprocess.run(
        ["uv", "run", "--directory", str(BACKEND), "python", "-c", code],
        cwd=REPO_ROOT,
        env=merged,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("overrides", "expected_fragment"),
    [
        pytest.param({"CENOMI_ENV": ""}, "CENOMI_ENV", id="a-missing-cenomi-env"),
        pytest.param({"CENOMI_AS_OF": ""}, "CENOMI_AS_OF", id="a-missing-as-of"),
        pytest.param({"CENOMI_ENV": "production"}, "CENOMI_ENV must be one of", id="b-invalid-env"),
        pytest.param(
            {"CENOMI_AS_OF": "20-Oct-2026"},
            "CENOMI_AS_OF must be a calendar date",
            id="c-invalid-as-of",
        ),
        pytest.param(
            {"CENOMI_ENV": "production", "AUTH_MODE": "dev_fixture"},
            "CENOMI_ENV must be one of",
            id="e-dev-fixture-unsafe-env",
        ),
        pytest.param(
            {"SESSION_SECRET": "too-short"},
            "SESSION_SECRET must be at least 32 bytes",
            id="f-short-secret",
        ),
    ],
)
@pytest.mark.trace("AT-M0-T03-01", reqs=["ARCH-R026"])
def test_startup_refused_for_invalid_configuration(
    overrides: dict[str, str], expected_fragment: str
) -> None:
    env = _valid_env(**overrides)
    if overrides.get("CENOMI_ENV") == "":
        env.pop("CENOMI_ENV", None)
    if overrides.get("CENOMI_AS_OF") == "":
        env.pop("CENOMI_AS_OF", None)
    result = _load_settings_subprocess(env)
    assert result.returncode == 1
    assert expected_fragment in result.stderr
