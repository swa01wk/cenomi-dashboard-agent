"""specs-check sub-check tests (M0-T10, AT-M0-T10-01, -02, -06, -07)."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from scripts.specs.check import run_checks
from scripts.specs.check_lib import (
    SUB_CHECKS,
    check_banned_terms,
    check_ci_jobs,
    check_cursor_rules,
    check_engineering_schema,
    check_id_families,
    check_make_help,
    check_manual_results,
    check_markdown_links,
    check_renderer_drift,
    check_sha256sums,
    check_spec_requirement_uniqueness,
    check_task_cards,
    check_adr_headings,
    check_adr_index,
)
from scripts.trace.report import _load_at_specs

REPO = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _copy_engineering_tree(tmp_path: Path) -> None:
    for rel in (
        "specs/engineering/make_targets.yaml",
        "specs/engineering/ci_checks.yaml",
        "specs/engineering/spec_set.yaml",
        "specs/traceability/id_conventions.yaml",
        "specs/contracts/error_codes.v1.yaml",
        "specs/engineering/engineering.schema.json",
    ):
        src = REPO / rel
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dest)


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007", "DEVENV-R035"])
def test_specs_check_passes_on_repository() -> None:
    findings, _ = run_checks(REPO)
    assert findings == []


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
@pytest.mark.parametrize("name", list(SUB_CHECKS))
def test_subcheck_positive_on_repository(name: str) -> None:
    if name == "ci_jobs" and not (REPO / ".github/workflows/ci.yml").is_file():
        pytest.skip("ci.yml not on branch")
    assert SUB_CHECKS[name](REPO) == []


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_engineering_schema(tmp_path: Path) -> None:
    _copy_engineering_tree(tmp_path)
    shutil.copy(
        FIXTURES / "engineering_schema" / "bad_spec_set.yaml",
        tmp_path / "specs/engineering/spec_set.yaml",
    )
    assert any(
        f.code == "SCHEMA_INVALID" for f in check_engineering_schema(tmp_path)
    )


@pytest.mark.trace("AT-M0-T10-02", reqs=["ARCH-R092"])
def test_negative_sha256_mismatch(tmp_path: Path) -> None:
    ref = tmp_path / "docs/reference/fake.txt"
    ref.parent.mkdir(parents=True)
    ref.write_text("original\n", encoding="utf-8")
    digest = hashlib.sha256(ref.read_bytes()).hexdigest()
    sums = tmp_path / "docs/handoff/SHA256SUMS"
    sums.parent.mkdir(parents=True)
    sums.write_text(f"{digest}  docs/reference/fake.txt\n", encoding="utf-8")
    ref.write_text("tampered\n", encoding="utf-8")
    assert any(f.code == "SHA256_MISMATCH" for f in check_sha256sums(tmp_path))


@pytest.mark.trace("AT-M0-T10-02", reqs=["ARCH-R092"])
def test_negative_sha256_unlisted(tmp_path: Path) -> None:
    ref = tmp_path / "docs/reference/extra.txt"
    ref.parent.mkdir(parents=True)
    ref.write_text("data\n", encoding="utf-8")
    sums = tmp_path / "docs/handoff/SHA256SUMS"
    sums.parent.mkdir(parents=True)
    sums.write_text("# empty\n", encoding="utf-8")
    assert any(f.code == "SHA256SUMS_UNLISTED" for f in check_sha256sums(tmp_path))


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_adr_headings(tmp_path: Path) -> None:
    (tmp_path / "docs/adr").mkdir(parents=True)
    (tmp_path / "docs/adr/0001-test.md").write_text("# ADR\n", encoding="utf-8")
    assert check_adr_headings(tmp_path)


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_adr_index(tmp_path: Path) -> None:
    (tmp_path / "docs/adr").mkdir(parents=True)
    (tmp_path / "docs/adr/README.md").write_text("# index\n", encoding="utf-8")
    (tmp_path / "docs/adr/0001-test.md").write_text(
        "## Context\n## Decision\n## Consequences\n## Verification\n",
        encoding="utf-8",
    )
    assert check_adr_index(tmp_path)


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_spec_requirement_uniqueness(tmp_path: Path) -> None:
    doc = tmp_path / "docs/x.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("**ARCH-R001** and **ARCH-R001**\n")
    assert check_spec_requirement_uniqueness(tmp_path)


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_id_families_malformed(tmp_path: Path) -> None:
    dest = tmp_path / "specs/traceability/id_conventions.yaml"
    dest.parent.mkdir(parents=True)
    shutil.copy(REPO / "specs/traceability/id_conventions.yaml", dest)
    doc = tmp_path / "docs/x.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("See M0-T7 for details.\n")
    assert any(f.code == "ID_MALFORMED" for f in check_id_families(tmp_path))


@pytest.mark.trace("AT-M0-T10-06", reqs=["RMAP-R007"])
def test_negative_task_cards(tmp_path: Path) -> None:
    (tmp_path / "plans").mkdir()
    (tmp_path / "plans/M0_T99-fixture.md").write_text(
        (FIXTURES / "task_cards" / "bad_card.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    assert any(f.code == "TASK_CARD_ROWS" for f in check_task_cards(tmp_path))


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_markdown_links(tmp_path: Path) -> None:
    doc = tmp_path / "docs/x.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("[bad](./missing.md)\n")
    assert check_markdown_links(tmp_path)


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_make_help(tmp_path: Path) -> None:
    _copy_engineering_tree(tmp_path)
    (tmp_path / "Makefile").write_text("help:\n", encoding="utf-8")
    assert check_make_help(tmp_path, help_output="  wrong-target   summary\n")


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_ci_jobs(tmp_path: Path) -> None:
    _copy_engineering_tree(tmp_path)
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/ci.yml").write_text("name: ci/wrong\n")
    assert check_ci_jobs(tmp_path)


@pytest.mark.trace("AT-M0-T10-07", reqs=["DEVENV-R046"])
def test_negative_banned_terms(tmp_path: Path) -> None:
    path = tmp_path / "tests/fixtures/sample.py"
    path.parent.mkdir(parents=True)
    path.write_text("STATUS = 'overdue'\n", encoding="utf-8")
    assert any(f.code == "BANNED_TERM" for f in check_banned_terms(tmp_path))


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_manual_results(tmp_path: Path) -> None:
    _copy_engineering_tree(tmp_path)
    (tmp_path / "plans/gates").mkdir(parents=True)
    (tmp_path / "plans/gates/M0-manual-results.json").write_text(
        '{"schema":"wrong","results":[]}'
    )
    assert check_manual_results(tmp_path)


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_renderer_drift(tmp_path: Path) -> None:
    shutil.copytree(REPO / "docs", tmp_path / "docs")
    shutil.copytree(REPO / "specs/engineering", tmp_path / "specs/engineering")
    targets = tmp_path / "specs/engineering/make_targets.yaml"
    text = targets.read_text(encoding="utf-8")
    targets.write_text(text.replace("summary:", "summary: DRIFT", 1), encoding="utf-8")
    assert check_renderer_drift(tmp_path)


@pytest.mark.trace("AT-M0-T10-01", reqs=["RMAP-R007"])
def test_negative_cursor_rules(tmp_path: Path) -> None:
    assert check_cursor_rules(tmp_path)


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R083"])
def test_manual_at_ids_from_field_15() -> None:
    specs = _load_at_specs(REPO)
    manual = {at_id for at_id, spec in specs.items() if spec.manual}
    expected = {
        "AT-M0-T07-07",
        "AT-M0-T08-05",
        "AT-M0-T09-01",
        "AT-M0-T09-02",
        "AT-M0-T09-03",
    }
    assert expected <= manual
