"""Database health provider binding (M0-T02 binds the real check_database)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from cenomi.api.services.health_types import DbCheckResult

DbHealthCheckFn = Callable[[], Awaitable[list[DbCheckResult]]]

_db_health_check: DbHealthCheckFn | None = None


def bind_db_health_check(fn: DbHealthCheckFn) -> None:
    """Register cenomi.db.health.check_database (composition point for M0-T02)."""
    global _db_health_check
    _db_health_check = fn


def get_db_health_check() -> DbHealthCheckFn | None:
    return _db_health_check


def clear_db_health_check() -> None:
    global _db_health_check
    _db_health_check = None
