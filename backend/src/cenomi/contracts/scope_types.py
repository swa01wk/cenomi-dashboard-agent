"""Shared scope shapes and key patterns (scope_decision.v1 $defs)."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

RegionKey = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{1,40}$")]
MallKey = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")]
TenantKey = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")]
LeaseKey = Annotated[str, Field(pattern=r"^[A-Z]{1,3}-[0-9]{3,8}$")]

_SCOPE_CONFIG = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    extra="forbid",
)


class ScopeAll(BaseModel):
    model_config = _SCOPE_CONFIG
    kind: Literal["ALL"]


class ScopeRegions(BaseModel):
    model_config = _SCOPE_CONFIG
    kind: Literal["REGIONS"]
    region_keys: list[RegionKey] = Field(min_length=1, max_length=3)


class ScopeMalls(BaseModel):
    model_config = _SCOPE_CONFIG
    kind: Literal["MALLS"]
    mall_keys: list[MallKey] = Field(min_length=1, max_length=50)


class ScopeTenant(BaseModel):
    model_config = _SCOPE_CONFIG
    kind: Literal["TENANT"]
    tenant_keys: list[TenantKey] = Field(min_length=1, max_length=10)


class ScopeTenantLeases(BaseModel):
    model_config = _SCOPE_CONFIG
    kind: Literal["TENANT_LEASES"]
    lease_keys: list[LeaseKey] = Field(min_length=1, max_length=100)


Scope = Annotated[
    ScopeAll | ScopeRegions | ScopeMalls | ScopeTenant | ScopeTenantLeases,
    Field(discriminator="kind"),
]

SCOPE_DEFS_MODELS: dict[str, type[BaseModel] | type] = {
    "regionKey": RegionKey,
    "mallKey": MallKey,
    "tenantKey": TenantKey,
    "leaseKey": LeaseKey,
}
