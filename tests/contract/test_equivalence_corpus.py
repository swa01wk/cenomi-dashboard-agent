"""AT-M0-T05-06 — equivalence corpus matches jsonschema verdicts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.codegen.equivalence_cases import build_corpus
from scripts.codegen.examples import FORMAT_CHECKER, _registry_for_contracts
from jsonschema import Draft202012Validator

CORPUS = (
    REPO_ROOT / "packages/contracts-ts/src/zod/__fixtures__/equivalence.cases.json"
)


@pytest.mark.trace("AT-M0-T05-06", reqs=["ARCH-R015", "ARCH-R093"])
def test_equivalence_corpus_is_current() -> None:
    assert CORPUS.is_file(), "run make codegen first"
    on_disk = json.loads(CORPUS.read_text(encoding="utf-8"))
    fresh = build_corpus()
    contracts_dir = REPO_ROOT / "specs" / "contracts"
    for stem, cases in fresh["schemas"].items():
        schema_path = contracts_dir / f"{stem}.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        registry = _registry_for_contracts(contracts_dir)
        validator = Draft202012Validator(
            schema, registry=registry, format_checker=FORMAT_CHECKER
        )
        recorded = on_disk["schemas"][stem]
        assert len(recorded) == len(cases)
        for rec, case in zip(recorded, cases, strict=True):
            assert rec["id"] == case["id"]
            try:
                validator.validate(case["payload"])
                valid = True
            except Exception:
                valid = False
            assert rec["jsonschemaValid"] == valid == case["jsonschemaValid"]
