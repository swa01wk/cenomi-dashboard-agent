"""health_report.v1 — GET /api/v1/health response."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

_MODEL = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    extra="forbid",
)

HealthStatus = Literal["ok", "degraded", "fail"]
CheckStatus = Literal["pass", "fail", "skipped"]
CheckName = Literal[
    "process",
    "db_reader",
    "db_app",
    "schemas_present",
    "role_isolation",
    "migrations_at_head",
    "dataset",
]


class HealthCheck(BaseModel):
    model_config = _MODEL

    name: CheckName
    required: bool
    status: CheckStatus
    detail: str | None = Field(default=None, max_length=200)
    duration_ms: int = Field(ge=0, le=60000)


class HealthApp(BaseModel):
    model_config = _MODEL

    version: str = Field(
        max_length=40,
        description="Backend package version or git short SHA baked in at build.",
    )
    spec_set: str = Field(
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$",
        description="specs/engineering/spec_set.yaml version the build was made from.",
    )
    migration_head: str | None = Field(
        default=None,
        max_length=80,
        description="Head Alembic revision bundled with the build.",
    )


class HealthReport(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        json_schema_extra={
            "title": "HealthReport v1",
            "description": (
                "Response of GET /api/v1/health and GET /api/v1/health/live (ARCH-R031). "
                "status ok when all required checks pass; degraded when only non-required "
                "checks fail; fail (HTTP 503) when a required check fails. /health/live "
                "returns only the process check. Details never contain credentials or "
                "connection strings. Bootstrap contract, frozen by CF-0."
            ),
            "examples": [
                {
                    "status": "ok",
                    "checks": [
                        {"name": "process", "required": True, "status": "pass", "durationMs": 0},
                        {"name": "db_reader", "required": True, "status": "pass", "durationMs": 4},
                        {"name": "db_app", "required": True, "status": "pass", "durationMs": 3},
                        {
                            "name": "schemas_present",
                            "required": True,
                            "status": "pass",
                            "durationMs": 2,
                        },
                        {
                            "name": "role_isolation",
                            "required": True,
                            "status": "pass",
                            "durationMs": 6,
                        },
                        {
                            "name": "migrations_at_head",
                            "required": True,
                            "status": "pass",
                            "durationMs": 1,
                        },
                        {
                            "name": "dataset",
                            "required": False,
                            "status": "skipped",
                            "detail": "dataset not seeded until M1",
                            "durationMs": 0,
                        },
                    ],
                    "app": {
                        "version": "0.1.0+d5db7f3",
                        "specSet": "0.1.0",
                        "migrationHead": "0001_m0_schemas_and_grants",
                    },
                    "checkedAt": "2026-10-22T14:30:00Z",
                },
                {
                    "status": "fail",
                    "checks": [
                        {"name": "process", "required": True, "status": "pass", "durationMs": 0},
                        {
                            "name": "db_reader",
                            "required": True,
                            "status": "fail",
                            "detail": "connection refused",
                            "durationMs": 2000,
                        },
                    ],
                    "app": {"version": "0.1.0+d5db7f3", "specSet": "0.1.0"},
                    "checkedAt": "2026-10-22T14:31:00Z",
                },
            ],
        },
    )

    status: HealthStatus
    checks: list[HealthCheck] = Field(min_length=1, max_length=20)
    app: HealthApp
    checked_at: str = Field(json_schema_extra={"format": "date-time"})
