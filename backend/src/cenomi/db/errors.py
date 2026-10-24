"""Database-layer errors (CA-06, QUERY_TIMEOUT)."""

from __future__ import annotations

from dataclasses import dataclass

from cenomi.core.errors import CenomiError


@dataclass
class QueryTimeout(CenomiError):
    """Raised when a reader-pool statement hits statement_timeout (CA-06)."""

    def __init__(self, message: str = "The query exceeded the statement timeout.") -> None:
        super().__init__(
            code="QUERY_TIMEOUT",
            message=message,
            retryable=True,
            http_status=504,
        )
