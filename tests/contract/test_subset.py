"""AT-M0-T05-04 — ADR-0004 subset checker."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.codegen.subset import validate_schema_file, validate_subset

FIXTURES = REPO_ROOT / "tests/contract/fixtures/subset"
CONTRACTS = REPO_ROOT / "specs/contracts"


@pytest.mark.trace("AT-M0-T05-04", reqs=["ARCH-R015"])
@pytest.mark.parametrize(
    "fixture,reason",
    [
        ("anyof.json", "anyOf"),
        ("open_object.json", "additionalProperties"),
        ("format_email.json", "format"),
    ],
)
def test_negative_subset_fixtures(fixture: str, reason: str) -> None:
    schema = json.loads((FIXTURES / fixture).read_text(encoding="utf-8"))
    violations = validate_subset(schema)
    assert violations, fixture
    assert any(reason in v.reason for v in violations)


@pytest.mark.trace("AT-M0-T05-04", reqs=["ARCH-R015"])
@pytest.mark.parametrize(
    "name",
    [
        "error_envelope.v1.schema.json",
        "principal.v1.schema.json",
        "scope_decision.v1.schema.json",
        "health_report.v1.schema.json",
        "dataset_descriptor.v1.schema.json",
    ],
)
def test_cf0_schemas_pass_subset(name: str) -> None:
    violations = validate_schema_file(CONTRACTS / name)
    assert not violations, violations
