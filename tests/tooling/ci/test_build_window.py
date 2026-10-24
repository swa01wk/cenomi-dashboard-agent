"""Build-window helpers for ci/summary live AT (ARCH-R103)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.build_window import (
    M0_T07_LIVE_AT,
    assert_build_window_targets,
    card_non_manual_all_passed,
    implemented_m0_cards,
)

MAKE_TARGETS = REPO_ROOT / "specs/engineering/make_targets.yaml"
TOOLING_JUNIT = REPO_ROOT / "tests/reports/backend/junit-tooling.xml"


def _target_rows() -> list[dict[str, str]]:
    data = yaml.safe_load(MAKE_TARGETS.read_text(encoding="utf-8"))
    return [
        {"name": str(t["name"]), "active_from": str(t["active_from"])}
        for t in data["targets"]
    ]


def _minimal_plan(card_id: str, field15: str) -> str:
    return f"""# Plan

### {card_id} — title

| # | Field | Content |
|---|---|---|
| 15 | Acceptance criteria | {field15} |
"""


def _seed_repo(tmp_path: Path, *, card: str, field15: str) -> None:
    (tmp_path / "plans").mkdir(parents=True)
    (tmp_path / "plans/M0_FOUNDATION.md").write_text(
        _minimal_plan(card, field15), encoding="utf-8"
    )
    id_conv = REPO_ROOT / "specs/traceability/id_conventions.yaml"
    dest = tmp_path / "specs/traceability/id_conventions.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(id_conv.read_text(encoding="utf-8"), encoding="utf-8")


def _junit(*at_ids: str) -> str:
    cases = "".join(
        f'<testcase classname="c" name="[{at_id}] x"/>' for at_id in at_ids
    )
    return (
        '<?xml version="1.0"?><testsuite name="s" tests="1" failures="0">'
        f"{cases}</testsuite>\n"
    )


def test_card_implemented_when_live_at_missing_other_passed(tmp_path: Path) -> None:
    _seed_repo(
        tmp_path,
        card="M0-T07",
        field15=(
            "**AT-M0-T07-01** one. **AT-M0-T07-02** live check. "
            "**AT-M0-T07-03** three."
        ),
    )
    junit = tmp_path / "junit.xml"
    junit.write_text(_junit("AT-M0-T07-01", "AT-M0-T07-03"), encoding="utf-8")
    assert card_non_manual_all_passed(
        tmp_path,
        [junit],
        "M0-T07",
        skip_at_ids=frozenset({M0_T07_LIVE_AT}),
    )


def test_card_not_implemented_when_other_at_not_passed(tmp_path: Path) -> None:
    _seed_repo(
        tmp_path,
        card="M0-T07",
        field15=(
            "**AT-M0-T07-01** one. **AT-M0-T07-02** live check. "
            "**AT-M0-T07-03** three."
        ),
    )
    junit = tmp_path / "junit.xml"
    junit.write_text(_junit("AT-M0-T07-01"), encoding="utf-8")
    assert not card_non_manual_all_passed(
        tmp_path,
        [junit],
        "M0-T07",
        skip_at_ids=frozenset({M0_T07_LIVE_AT}),
    )


def test_card_not_implemented_on_unknown_at_in_junit(tmp_path: Path) -> None:
    _seed_repo(
        tmp_path,
        card="M0-T07",
        field15="**AT-M0-T07-01** one. **AT-M0-T07-02** live check.",
    )
    junit = tmp_path / "junit.xml"
    junit.write_text(_junit("AT-M0-T07-01", "AT-M0-T99-99"), encoding="utf-8")
    assert not card_non_manual_all_passed(
        tmp_path,
        [junit],
        "M0-T07",
        skip_at_ids=frozenset({M0_T07_LIVE_AT}),
    )


def test_m0_t07_implemented_on_main_without_live_at() -> None:
    if not TOOLING_JUNIT.is_file():
        pytest.skip("run make backend-test SUITE=tooling to generate junit-tooling.xml")
    junit_paths = [TOOLING_JUNIT]
    assert "M0-T07" in implemented_m0_cards(
        REPO_ROOT, junit_paths=junit_paths, pr_card=None
    )

    errors = assert_build_window_targets(
        repo=REPO_ROOT,
        status_records=[{"item": "ci", "kind": "target", "result": "PASSED"}],
        junit_paths=junit_paths,
        pr_card=None,
        make_targets=_target_rows(),
    )
    ci_errors = [e for e in errors if e.startswith("ci:")]
    assert not ci_errors, ci_errors


def test_pr_card_counts_as_implemented_without_junit() -> None:
    implemented = implemented_m0_cards(
        REPO_ROOT, junit_paths=[], pr_card="M0-T07"
    )
    assert "M0-T07" in implemented
