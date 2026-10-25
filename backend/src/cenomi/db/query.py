"""Reader-pool query execution with timeout mapping (CA-06)."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine

from cenomi.core.settings import Settings
from cenomi.db.engines import reader_engine
from cenomi.db.errors import QueryTimeout

try:
    from psycopg.errors import QueryCanceled
except ImportError:  # pragma: no cover
    QueryCanceled = Exception  # type: ignore[misc, assignment]


async def execute_reader_scalar(
    statement: str,
    *,
    settings: Settings | None = None,
    engine: AsyncEngine | None = None,
) -> object:
    eng = engine or reader_engine(settings)
    try:
        async with eng.connect() as conn:
            return (await conn.execute(text(statement))).scalar_one()
    except OperationalError as exc:
        if isinstance(exc.orig, QueryCanceled):
            raise QueryTimeout() from exc
        raise
    except QueryCanceled as exc:
        raise QueryTimeout() from exc
