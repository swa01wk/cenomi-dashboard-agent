"""Real-database health checks for GET /api/v1/health (ARCH-R031)."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from cenomi.api.services.health_types import DbCheckResult
from cenomi.core.settings import Settings, get_settings
from cenomi.db.engines import app_engine, reader_engine
from cenomi.db.urls import replace_database

SCHEMAS: tuple[str, ...] = ("core", "meta", "snap", "seed_meta", "agent", "insights")
HEAD_REVISION = "0001_m0_schemas_and_grants"


async def _timed(
    name: Literal[
        "db_reader",
        "db_app",
        "schemas_present",
        "role_isolation",
        "migrations_at_head",
    ],
    coro_factory: Callable[[], Awaitable[str | None]],
) -> DbCheckResult:
    started = time.perf_counter()
    try:
        detail = await coro_factory()
        elapsed = int((time.perf_counter() - started) * 1000)
        return DbCheckResult(
            name=name,
            required=True,
            status="pass",
            duration_ms=elapsed,
            detail=detail,
        )
    except Exception as exc:  # noqa: BLE001 — health must not raise
        elapsed = int((time.perf_counter() - started) * 1000)
        return DbCheckResult(
            name=name,
            required=True,
            status="fail",
            duration_ms=elapsed,
            detail=str(exc)[:200],
        )


async def check_database(settings: Settings | None = None) -> list[DbCheckResult]:
    resolved = settings or get_settings()
    dev_db = replace_database(
        resolved.database_url_reader.get_secret_value(),
        "cenomi_dev",
    )
    _ = dev_db  # health checks target the configured database name in URLs (dev in compose)
    reader = reader_engine(resolved)
    app = app_engine(resolved)
    results: list[DbCheckResult] = []
    results.append(await _timed("db_reader", lambda: _check_reader(reader)))
    results.append(await _timed("db_app", lambda: _check_app(app)))
    results.append(await _timed("schemas_present", lambda: _check_schemas(reader)))
    results.append(await _timed("role_isolation", lambda: _check_role_isolation(reader, app)))
    results.append(await _timed("migrations_at_head", lambda: _check_migrations(reader)))
    return results


async def _check_reader(engine: AsyncEngine) -> str | None:
    async with engine.connect() as conn:
        ro = (await conn.execute(text("SHOW transaction_read_only"))).scalar_one()
        if str(ro).lower() not in ("on", "true"):
            raise RuntimeError("reader session is not read-only")
    return None


async def _check_app(engine: AsyncEngine) -> str | None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return None


async def _check_schemas(engine: AsyncEngine) -> str | None:
    async with engine.connect() as conn:
        for schema in SCHEMAS:
            row = (
                await conn.execute(
                    text(
                        "SELECT EXISTS("
                        "SELECT 1 FROM pg_catalog.pg_namespace "
                        "WHERE nspname = :name)"
                    ),
                    {"name": schema},
                )
            ).scalar_one()
            if not row:
                raise RuntimeError(f"missing schema {schema}")
    return None


async def _check_role_isolation(
    reader: AsyncEngine,
    app: AsyncEngine,
) -> str | None:
    async with reader.connect() as conn:
        for schema in ("seed_meta", "agent", "insights"):
            usage = (
                await conn.execute(
                    text("SELECT has_schema_privilege(current_user, :s, 'USAGE')"),
                    {"s": schema},
                )
            ).scalar_one()
            if usage:
                raise RuntimeError(f"reader has USAGE on {schema}")
        for schema in SCHEMAS:
            create = (
                await conn.execute(
                    text("SELECT has_schema_privilege(current_user, :s, 'CREATE')"),
                    {"s": schema},
                )
            ).scalar_one()
            if create:
                raise RuntimeError(f"reader has CREATE on {schema}")
    async with app.connect() as conn:
        for schema in ("core", "meta", "snap", "seed_meta"):
            usage = (
                await conn.execute(
                    text("SELECT has_schema_privilege(current_user, :s, 'USAGE')"),
                    {"s": schema},
                )
            ).scalar_one()
            if usage:
                raise RuntimeError(f"app has USAGE on {schema}")
    return None


async def _check_migrations(engine: AsyncEngine) -> str | None:
    async with engine.connect() as conn:
        version = (
            await conn.execute(text("SELECT version_num FROM public.alembic_version LIMIT 1"))
        ).scalar_one_or_none()
        if version != HEAD_REVISION:
            raise RuntimeError(f"alembic_version is {version!r}, expected {HEAD_REVISION}")
    return None
