"""AT-M0-T05-01 — Pydantic exports match bootstrap schemas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

from cenomi.contracts.export import export_contract_schema
from cenomi.contracts.registry import BUILT_CONTRACTS
from scripts.codegen.normalize import first_diff_path, normalize_schema


@pytest.mark.trace("AT-M0-T05-01", reqs=["ARCH-R015", "ARCH-R092"])
@pytest.mark.parametrize("contract", BUILT_CONTRACTS, ids=lambda c: c.stem)
def test_export_matches_bootstrap(contract) -> None:
    exported = export_contract_schema(contract)
    bootstrap = json.loads(
        (REPO_ROOT / "tests/contract/fixtures/bootstrap" / contract.filename).read_text(
            encoding="utf-8"
        )
    )
    diff = first_diff_path(normalize_schema(bootstrap), normalize_schema(exported))
    assert diff is None, f"first difference at {diff}"


@pytest.mark.trace("AT-M0-T05-01", reqs=["ARCH-R093"])
def test_mismatch_reports_json_path() -> None:
    from cenomi.contracts.dataset_descriptor import DatasetDescriptor

    exported = export_contract_schema(BUILT_CONTRACTS[-1])
    exported["properties"]["datasetId"] = {"type": "string"}
    bootstrap = json.loads(
        (
            REPO_ROOT / "tests/contract/fixtures/bootstrap/dataset_descriptor.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    diff = first_diff_path(normalize_schema(bootstrap), normalize_schema(exported))
    assert diff is not None
    assert diff.startswith("$.properties")
