"""specs-check sub-check tests (M0-T10, AT-M0-T10-01, AT-M0-T10-02, AT-M0-T10-06, AT-M0-T10-07)."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from scripts.specs.check_lib import (
    check_banned_terms,
    check_sha256sums,
    check_task_cards,
    check_engineering_schema,
)
from scripts.specs.check_lib import SUB_CHECKS
from scripts.specs.check import run_checks

REPO = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007", "DEVENV-R035"])
def test_specs_check_passes_on_repository() -> None:
    findings, _ = run_checks(REPO)
    assert findings == []


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
@pytest.mark.parametrize("name", list(SUB_CHECKS))
def test_subcheck_has_negative_fixture(name: str) -> None:
    fixture_dir = FIXTURES / name
    assert fixture_dir.is_dir(), f"missing negative fixture dir for {name}"


@pytest.mark.trace("AT-M0-T10-02", reqs=["ARCH-R092"])
def test_sha256_detects_modified_reference(tmp_path: Path) -> None:
    ref = tmp_path / "docs/reference/fake.txt"
    ref.parent.mkdir(parents=True)
    ref.write_text("original\n", encoding="utf-8")
    digest = hashlib.sha256(ref.read_bytes()).hexdigest()
    sums = tmp_path / "docs/handoff/SHA256SUMS"
    sums.parent.mkdir(parents=True)
    sums.write_text(f"{digest}  docs/reference/fake.txt\n", encoding="utf-8")
    ref.write_text("tampered\n", encoding="utf-8")
    findings = check_sha256sums(tmp_path)
    assert any(f.code == "SHA256_MISMATCH" for f in findings)


@pytest.mark.trace("AT-M0-T10-06", reqs=["RMAP-R007"])
def test_task_card_missing_row_fixture(tmp_path: Path) -> None:
    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    bad = FIXTURES / "task_cards" / "bad_card.md"
    target = plan_dir / "M0_T99-fixture.md"
    target.write_text(bad.read_text(encoding="utf-8"), encoding="utf-8")
    findings = check_task_cards(tmp_path)
    assert any(f.code == "TASK_CARD_ROWS" for f in findings)


@pytest.mark.trace("AT-M0-T10-07", reqs=["DEVENV-R046"])
def test_banned_term_in_tmp_fixtures_tree(tmp_path: Path) -> None:
    tree = tmp_path / "tests/fixtures/sample.py"
    tree.parent.mkdir(parents=True)
    tree.write_text("STATUS = 'overdue'\n", encoding="utf-8")
    findings = check_banned_terms(tmp_path)
    assert any(f.code == "BANNED_TERM" for f in findings)


def test_engineering_schema_negative_fixture(tmp_path: Path) -> None:
    bad = FIXTURES / "engineering_schema" / "bad_spec_set.yaml"
    eng = tmp_path / "specs/engineering"
    eng.mkdir(parents=True)
    trace = tmp_path / "specs/traceability"
    trace.mkdir(parents=True)
    contracts = tmp_path / "specs/contracts"
    contracts.mkdir(parents=True)
    for name in (
        "make_targets.yaml",
        "ci_checks.yaml",
        "spec_set.yaml",
        "id_conventions.yaml",
        "error_codes.v1.yaml",
    ):
        src = REPO / "specs"
        if name == "spec_set.yaml":
            shutil.copy(bad, eng / name)
        elif name == "id_conventions.yaml":
            shutil.copy(src / "traceability" / name, trace / name)
        elif name.startswith("error"):
            shutil.copy(src / "contracts" / name, contracts / name)
        else:
            shutil.copy(src / "engineering" / name, eng / name)
    findings = check_engineering_schema(tmp_path)
    assert any(f.code == "SCHEMA_INVALID" for f in findings)
