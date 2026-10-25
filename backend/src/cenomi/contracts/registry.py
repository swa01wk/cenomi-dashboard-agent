"""Built CF-0 contracts exported by the codegen pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel

from cenomi.contracts.dataset_descriptor import DatasetDescriptor
from cenomi.contracts.error_envelope import ErrorEnvelope
from cenomi.contracts.health_report import HealthReport
from cenomi.contracts.principal import Principal
from cenomi.contracts.scope_decision import ScopeDecision


@dataclass(frozen=True)
class BuiltContract:
    stem: str
    major: int
    model: type[BaseModel]
    dotted_path: str
    schema_id: str

    @property
    def filename(self) -> str:
        return f"{self.stem}.v{self.major}.schema.json"


BUILT_CONTRACTS: tuple[BuiltContract, ...] = (
    BuiltContract(
        "error_envelope",
        1,
        ErrorEnvelope,
        "cenomi.contracts.error_envelope.ErrorEnvelope",
        "https://cenomi.local/contracts/error_envelope.v1.schema.json",
    ),
    BuiltContract(
        "principal",
        1,
        Principal,
        "cenomi.contracts.principal.Principal",
        "https://cenomi.local/contracts/principal.v1.schema.json",
    ),
    BuiltContract(
        "scope_decision",
        1,
        ScopeDecision,
        "cenomi.contracts.scope_decision.ScopeDecision",
        "https://cenomi.local/contracts/scope_decision.v1.schema.json",
    ),
    BuiltContract(
        "health_report",
        1,
        HealthReport,
        "cenomi.contracts.health_report.HealthReport",
        "https://cenomi.local/contracts/health_report.v1.schema.json",
    ),
    BuiltContract(
        "dataset_descriptor",
        1,
        DatasetDescriptor,
        "cenomi.contracts.dataset_descriptor.DatasetDescriptor",
        "https://cenomi.local/contracts/dataset_descriptor.v1.schema.json",
    ),
)


def contract_by_stem(stem: str) -> BuiltContract:
    for item in BUILT_CONTRACTS:
        if item.stem == stem:
            return item
    raise KeyError(stem)
