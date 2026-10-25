"""scope_decision.v1 — AccessScope.authorize result."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from cenomi.contracts.scope_types import Scope

_MODEL_CONFIG = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    extra="forbid",
    json_schema_extra={
        "title": "ScopeDecision v1",
        "description": (
            "Result of AccessScope.authorize(principal, requestedScope) (ARCH-R079). "
            "Deny by default; an empty scope is never widened (DR-020, SEC-02); ALL only "
            "from an explicit grant (ARCH-R080). `effective` is present exactly when "
            "outcome is allow or narrowed. Defines the shared Scope type in $defs. "
            "Bootstrap contract, frozen by CF-0; the location-hierarchy resolution for "
            "cross-kind requests is added behind the same interface in M1 "
            "(ARCH-R081, ADR-0008)."
        ),
        "examples": [
            {
                "principalId": "p_central_manager",
                "outcome": "allow",
                "fingerprint": "sfp_0f3a9c1d2b4e5f60718293a4b5c6d7e8",
                "reasons": ["no_request_full_grant"],
                "effective": {"kind": "REGIONS", "regionKeys": ["central"]},
            },
            {
                "principalId": "p_central_manager",
                "outcome": "empty",
                "requested": {"kind": "REGIONS", "regionKeys": ["eastern"]},
                "fingerprint": "sfp_9d1e2f3a4b5c6d7e8f90a1b2c3d4e5f6",
                "reasons": ["requested_outside_grant"],
            },
            {
                "principalId": "p_no_grants",
                "outcome": "empty",
                "fingerprint": "sfp_9d1e2f3a4b5c6d7e8f90a1b2c3d4e5f6",
                "reasons": ["no_grants"],
            },
            {
                "principalId": "p_portfolio_admin",
                "outcome": "allow",
                "requested": {"kind": "REGIONS", "regionKeys": ["central"]},
                "effective": {"kind": "REGIONS", "regionKeys": ["central"]},
                "fingerprint": "sfp_0f3a9c1d2b4e5f60718293a4b5c6d7e8",
                "reasons": ["requested_within_grant"],
            },
        ],
    },
)

Outcome = Literal["allow", "narrowed", "empty", "deny"]
Reason = Literal[
    "requested_within_grant",
    "requested_outside_grant",
    "no_request_full_grant",
    "no_grants",
    "hierarchy_unresolved",
    "permission_missing",
]


class ScopeDecision(BaseModel):
    model_config = _MODEL_CONFIG

    principal_id: str = Field(pattern=r"^p_[a-z0-9_]{2,60}$")
    outcome: Outcome
    requested: Scope | None = Field(
        default=None,
        description="Absent when the caller made no scope request.",
    )
    effective: Scope | None = Field(
        default=None,
        description="Present only for allow and narrowed.",
    )
    fingerprint: str = Field(pattern=r"^sfp_[0-9a-f]{32}$")
    reasons: list[Reason] = Field(min_length=1, max_length=6)
