"""Database-only settings for CLI and Alembic (CI-safe)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from cenomi.db.settings import DbSettings, load_db_settings

REPO_ROOT = Path(__file__).resolve().parents[4]

_CI_URLS = {
    "CENOMI_ENV": "ci",
    "DATABASE_URL_ADMIN": "postgresql://postgres:postgres@localhost:5432/postgres",
    "DATABASE_URL_OWNER": "postgresql://cenomi_owner:change-me-dev-only-owner@localhost:5432/cenomi_test",
    "DATABASE_URL_SEED": "postgresql://cenomi_seed:change-me-dev-only-seed@localhost:5432/cenomi_test",
    "DATABASE_URL_READER": "postgresql://cenomi_reader:change-me-dev-only-reader@localhost:5432/cenomi_test",
    "DATABASE_URL_APP": "postgresql://cenomi_app:change-me-dev-only-app@localhost:5432/cenomi_test",
}

_APP_ONLY_VARS = (
    "CENOMI_DATASET_ID",
    "CENOMI_AS_OF",
    "CENOMI_TZ",
    "AUTH_MODE",
    "SESSION_SECRET",
    "API_INTERNAL_URL",
)

_RUNTIME_ENV_PREFIXES = (
    "PATH",
    "HOME",
    "USER",
    "SHELL",
    "TMPDIR",
    "LANG",
    "LC_",
    "UV_",
    "VIRTUAL_ENV",
    "SSL_CERT",
    "DYLD_",
    "XDG_",
)


def _minimal_runtime_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for key, value in os.environ.items():
        if any(key == prefix or key.startswith(prefix) for prefix in _RUNTIME_ENV_PREFIXES):
            env[key] = value
    env.update(_CI_URLS)
    for key in _APP_ONLY_VARS:
        env.pop(key, None)
    return env


@pytest.mark.unit
@pytest.mark.trace("AT-M0-T02-08", reqs=["DEVENV-R010"])
def test_load_db_settings_with_database_urls_only(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        monkeypatch.delenv(key, raising=False)
    for key, value in _CI_URLS.items():
        monkeypatch.setenv(key, value)
    for key in _APP_ONLY_VARS:
        monkeypatch.delenv(key, raising=False)

    settings = load_db_settings()
    assert isinstance(settings, DbSettings)
    assert settings.cenomi_env == "ci"
    assert "cenomi_owner" in settings.database_url_owner.get_secret_value()


@pytest.mark.unit
@pytest.mark.trace("AT-M0-T02-08", reqs=["DEVENV-R010"])
def test_cenomi_db_init_help_with_database_urls_only() -> None:
    env = _minimal_runtime_env()
    completed = subprocess.run(
        ["uv", "run", "--project", "backend", "cenomi", "db", "init", "--help"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "cenomi db init" in completed.stdout
