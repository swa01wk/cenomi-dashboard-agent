"""Database-only configuration for CLI and Alembic (no application Settings)."""

from __future__ import annotations

import sys
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

CenomiEnv = Literal["dev", "test", "ci"]


class DbSettings(BaseSettings):
    """Minimal settings for `cenomi db`, guards and migrations (CI-safe)."""

    model_config = SettingsConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    cenomi_env: CenomiEnv = Field(alias="CENOMI_ENV")
    database_url_admin: SecretStr = Field(alias="DATABASE_URL_ADMIN")
    database_url_owner: SecretStr = Field(alias="DATABASE_URL_OWNER")
    database_url_seed: SecretStr = Field(alias="DATABASE_URL_SEED")
    database_url_reader: SecretStr = Field(alias="DATABASE_URL_READER")
    database_url_app: SecretStr = Field(alias="DATABASE_URL_APP")


def _format_validation_error(exc: ValidationError) -> str:
    parts: list[str] = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", ()))
        msg = err.get("msg", "invalid")
        parts.append(f"{loc}: {msg}" if loc else msg)
    return "; ".join(parts) if parts else str(exc)


def load_db_settings() -> DbSettings:
    try:
        return DbSettings()
    except ValidationError as exc:
        print(f"Configuration error: {_format_validation_error(exc)}", file=sys.stderr)
        raise SystemExit(1) from exc


@lru_cache
def get_db_settings() -> DbSettings:
    return DbSettings()
