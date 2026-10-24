"""Async SQLAlchemy engines for reader and app pools (ARCH-R032)."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from cenomi.core.settings import Settings, get_settings
from cenomi.db.urls import replace_database

READER_ROLE_STATEMENT_TIMEOUT_MS = 5000


def _to_async_dsn(url: str) -> str:
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    if url.startswith("postgresql+psycopg://"):
        return url
    raise ValueError("expected a postgresql:// or postgresql+psycopg:// URL")


def reader_statement_timeout_ms(settings: Settings) -> int:
    return min(settings.db_reader_statement_timeout_ms, READER_ROLE_STATEMENT_TIMEOUT_MS)


@lru_cache
def _reader_engine_for_dsn(dsn: str, pool_size: int, timeout_ms: int) -> AsyncEngine:
    return create_async_engine(
        dsn,
        pool_size=pool_size,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={
            "options": (f"-c default_transaction_read_only=on -c statement_timeout={timeout_ms}")
        },
    )


@lru_cache
def _app_engine_for_dsn(dsn: str, pool_size: int) -> AsyncEngine:
    return create_async_engine(
        dsn,
        pool_size=pool_size,
        max_overflow=0,
        pool_pre_ping=True,
    )


def reader_engine(
    settings: Settings | None = None,
    *,
    database: str | None = None,
) -> AsyncEngine:
    resolved = settings or get_settings()
    url = resolved.database_url_reader.get_secret_value()
    if database is not None:
        url = replace_database(url, database)
    timeout_ms = reader_statement_timeout_ms(resolved)
    return _reader_engine_for_dsn(
        _to_async_dsn(url),
        resolved.db_reader_pool_size,
        timeout_ms,
    )


def app_engine(
    settings: Settings | None = None,
    *,
    database: str | None = None,
) -> AsyncEngine:
    resolved = settings or get_settings()
    url = resolved.database_url_app.get_secret_value()
    if database is not None:
        url = replace_database(url, database)
    return _app_engine_for_dsn(_to_async_dsn(url), resolved.db_app_pool_size)


def clear_engine_caches() -> None:
    _reader_engine_for_dsn.cache_clear()
    _app_engine_for_dsn.cache_clear()
