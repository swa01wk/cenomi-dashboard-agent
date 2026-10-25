"""dataset_descriptor.v1 — GET /api/v1/dataset response."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

Source = Literal["config", "database"]
State = Literal["declared", "seeded"]


class DatasetDescriptor(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        json_schema_extra={
            "title": "DatasetDescriptor v1",
            "description": (
                "Response of GET /api/v1/dataset (public). Drives the synthetic-data banner "
                "and the 'As of … · synthetic data' footers (DXD-09, DATA-07). In M0 the "
                "source is configuration and state is declared; from M1 the source is the meta "
                "schema and state is seeded (ARCH-R028). Bootstrap contract, frozen by CF-0."
            ),
            "examples": [
                {
                    "datasetId": "sd-2026.10.20-01",
                    "asOf": "2026-10-20",
                    "timezone": "Asia/Riyadh",
                    "synthetic": True,
                    "source": "config",
                    "state": "declared",
                }
            ],
        },
    )

    dataset_id: str = Field(pattern=r"^sd-[0-9]{4}\.[0-9]{2}\.[0-9]{2}-[0-9]{2}$")
    as_of: str = Field(
        description="Frozen reference date, an Asia/Riyadh calendar day (DR-003, DR-004).",
        json_schema_extra={"format": "date"},
    )
    timezone: Literal["Asia/Riyadh"]
    synthetic: Literal[True]
    source: Source
    state: State
    seed_hash: str | None = Field(
        default=None,
        pattern=r"^[0-9a-f]{16,64}$",
        description="Present when state is seeded.",
    )
    transactional_start: str | None = Field(
        default=None,
        description=(
            "First day of transactional history (2024-01-01, DR-004). Present when state is seeded."
        ),
        json_schema_extra={"format": "date"},
    )
