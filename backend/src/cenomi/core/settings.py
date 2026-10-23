"""Application settings (ARCH-R026, ARCH-R027)."""

from __future__ import annotations

import sys
from datetime import date
from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CenomiEnv = Literal["dev", "test", "ci"]
AuthMode = Literal["dev_fixture"]
LlmMode = Literal["off", "replay", "live"]
OtelExporter = Literal["console", "otlp", "none"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    cenomi_env: CenomiEnv = Field(alias="CENOMI_ENV")
    database_url_admin: SecretStr = Field(alias="DATABASE_URL_ADMIN")
    database_url_owner: SecretStr = Field(alias="DATABASE_URL_OWNER")
    database_url_seed: SecretStr = Field(alias="DATABASE_URL_SEED")
    database_url_reader: SecretStr = Field(alias="DATABASE_URL_READER")
    database_url_app: SecretStr = Field(alias="DATABASE_URL_APP")
    db_reader_pool_size: int = Field(default=10, alias="DB_READER_POOL_SIZE")
    db_app_pool_size: int = Field(default=5, alias="DB_APP_POOL_SIZE")
    db_reader_statement_timeout_ms: int = Field(
        default=5000, alias="DB_READER_STATEMENT_TIMEOUT_MS"
    )

    cenomi_dataset_id: str = Field(alias="CENOMI_DATASET_ID")
    cenomi_as_of: date = Field(alias="CENOMI_AS_OF")
    cenomi_tz: str = Field(alias="CENOMI_TZ")

    auth_mode: AuthMode = Field(alias="AUTH_MODE")
    session_secret: SecretStr = Field(alias="SESSION_SECRET")
    session_ttl_minutes: int = Field(default=480, alias="SESSION_TTL_MINUTES")

    llm_mode: LlmMode = Field(default="off", alias="LLM_MODE")
    llm_provider: str = Field(default="", alias="LLM_PROVIDER")
    llm_primary_model: str = Field(default="", alias="LLM_PRIMARY_MODEL")
    llm_fallback_model: str = Field(default="", alias="LLM_FALLBACK_MODEL")
    llm_api_key: SecretStr = Field(default=SecretStr(""), alias="LLM_API_KEY")
    llm_replay_dir: str = Field(default="tests/fixtures/llm-replay", alias="LLM_REPLAY_DIR")

    otel_exporter: OtelExporter = Field(default="console", alias="OTEL_EXPORTER")
    otel_exporter_otlp_endpoint: str = Field(default="", alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    api_internal_url: str = Field(alias="API_INTERNAL_URL")

    @field_validator("cenomi_env", mode="before")
    @classmethod
    def validate_cenomi_env(cls, value: object) -> CenomiEnv:
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError("CENOMI_ENV is required")
        if value not in ("dev", "test", "ci"):
            raise ValueError("CENOMI_ENV must be one of dev, test or ci")
        return value

    @field_validator("cenomi_as_of", mode="before")
    @classmethod
    def parse_as_of(cls, value: object) -> date:
        if isinstance(value, date):
            return value
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError("CENOMI_AS_OF is required")
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError(
                    f"CENOMI_AS_OF must be a calendar date (YYYY-MM-DD): {value!r}"
                ) from exc
        raise ValueError("CENOMI_AS_OF must be a calendar date")

    @model_validator(mode="after")
    def validate_startup_rules(self) -> Self:
        if self.auth_mode == "dev_fixture" and self.cenomi_env not in ("dev", "test", "ci"):
            raise ValueError(
                "AUTH_MODE=dev_fixture is only allowed when CENOMI_ENV is dev, test or ci"
            )
        secret = self.session_secret.get_secret_value()
        if len(secret.encode("utf-8")) < 32:
            raise ValueError("SESSION_SECRET must be at least 32 bytes")
        if self.llm_mode == "live" and not self.llm_api_key.get_secret_value().strip():
            raise ValueError("LLM_API_KEY is required when LLM_MODE=live")
        if self.cenomi_tz != "Asia/Riyadh":
            raise ValueError("CENOMI_TZ must be Asia/Riyadh")
        return self


class _EnvParseError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _settings_from_env() -> Settings:
    try:
        return Settings()
    except Exception as exc:  # pydantic ValidationError and others
        message = str(exc)
        if hasattr(exc, "errors"):
            from pydantic import ValidationError

            if isinstance(exc, ValidationError):
                errors = exc.errors()
            else:
                errors = []
            parts: list[str] = []
            for err in errors:
                loc = ".".join(str(x) for x in err.get("loc", ()))
                msg = err.get("msg", "invalid")
                parts.append(f"{loc}: {msg}" if loc else msg)
            if parts:
                message = "; ".join(parts)
        raise _EnvParseError(message) from exc


def load_settings() -> Settings:
    """Load settings or exit the process with a clear message (ARCH-R026)."""
    try:
        return _settings_from_env()
    except _EnvParseError as exc:
        print(f"Configuration error: {exc.message}", file=sys.stderr)
        raise SystemExit(1) from exc


@lru_cache
def get_settings() -> Settings:
    return _settings_from_env()
