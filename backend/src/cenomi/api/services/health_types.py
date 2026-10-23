"""Health check result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CheckName = Literal[
    "process",
    "db_reader",
    "db_app",
    "schemas_present",
    "role_isolation",
    "migrations_at_head",
    "dataset",
]
CheckStatus = Literal["pass", "fail", "skipped"]


@dataclass(frozen=True)
class DbCheckResult:
    name: CheckName
    required: bool
    status: CheckStatus
    duration_ms: int
    detail: str | None = None
