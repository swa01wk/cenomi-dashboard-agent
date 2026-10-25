"""principal.v1 — signed-in principal for presentation."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from cenomi.contracts.scope_types import Scope

Persona = Literal["admin", "tenant"]
Role = Literal[
    "PORTFOLIO_ADMIN",
    "REGIONAL_ADMIN",
    "MALL_MANAGER",
    "LEASING_MANAGER",
    "FITOUT_MANAGER",
    "TENANT_COMPANY_ADMIN",
    "TENANT_LEASE_CONTACT",
]

PermissionName = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*(:[a-zA-Z0-9_.-]+)+$")]


class Principal(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        json_schema_extra={
            "title": "Principal v1",
            "description": (
                "The signed-in principal returned by GET /api/v1/me and "
                "POST /api/v1/auth/dev/sign-in (ARCH-R077). The client uses it only for "
                "presentation; authorization is enforced server-side (ARCH-R046). Business "
                "keys in grants are provisional until CF-1 confirms them against the seed "
                "(ARCH-R078). Bootstrap contract, frozen by CF-0."
            ),
            "examples": [
                {
                    "principalId": "p_central_manager",
                    "displayName": "Central regional manager",
                    "persona": "admin",
                    "role": "REGIONAL_ADMIN",
                    "grants": [{"kind": "REGIONS", "regionKeys": ["central"]}],
                    "permissions": [],
                    "sessionExpiresAt": "2026-10-22T22:00:00Z",
                },
                {
                    "principalId": "p_tenant_t31206",
                    "displayName": "Lumen Home (lease T-31206)",
                    "persona": "tenant",
                    "role": "TENANT_LEASE_CONTACT",
                    "grants": [{"kind": "TENANT_LEASES", "leaseKeys": ["T-31206"]}],
                    "permissions": [],
                    "sessionExpiresAt": "2026-10-22T22:00:00Z",
                },
                {
                    "principalId": "p_no_grants",
                    "displayName": "No-access test principal",
                    "persona": "admin",
                    "role": "REGIONAL_ADMIN",
                    "grants": [],
                    "permissions": [],
                    "sessionExpiresAt": "2026-10-22T22:00:00Z",
                },
            ],
        },
    )

    principal_id: str = Field(pattern=r"^p_[a-z0-9_]{2,60}$")
    display_name: str = Field(min_length=1, max_length=120)
    persona: Persona = Field(description="Which dashboard family the principal lands on.")
    role: Role = Field(
        description=(
            "Fixture role (approved G0 access model; DR-019). Permissions per role are "
            "fixed in specs/authorization/permissions.yaml (PR-M1)."
        )
    )
    grants: list[Scope] = Field(
        max_length=20,
        description=(
            "Union of scope grants. Empty means no access (deny by default, ARCH-R079). "
            "ALL is only ever an explicit grant (ARCH-R080)."
        ),
    )
    permissions: list[PermissionName] = Field(
        max_length=200,
        description=(
            "Permission names from specs/authorization/permissions.yaml. "
            "Empty in M0 (the matrix arrives in PR-M1)."
        ),
    )
    session_expires_at: str = Field(json_schema_extra={"format": "date-time"})
