"""Reader pool timeout behaviour (AT-M0-T02-09, CA-06)."""

from __future__ import annotations

import pytest

from cenomi.db.errors import QueryTimeout
from cenomi.db.query import execute_reader_scalar


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T02-09", reqs=["ARCH-R032"])
async def test_reader_pool_cancels_long_query() -> None:
    with pytest.raises(QueryTimeout):
        await execute_reader_scalar("SELECT pg_sleep(6)")
