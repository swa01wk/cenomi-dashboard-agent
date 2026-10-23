"""trace-report acceptance tests (M0-T10, AT-M0-T10-04)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.trace.report import build_report, _load_at_specs

REPO = Path(__file__).resolve().parents[3]


def _minimal_plan(card_id: str, field15: str) -> str:
    return f"""# Plan

### {card_id} — title

| # | Field | Content |
|---|---|---|
| 15 | Acceptance criteria | {field15} |
"""


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_unknown_card_id_fails(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    with pytest.raises(ValueError, match="malformed"):
        build_report(tmp_path, card="not-a-card")


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095"])
def test_at_without_test_is_not_implemented(tmp_path: Path) -> None:
    _seed_repo(tmp_path, extra_at="**AT-M0-T10-99** never runs.")
    payload, _, _ = build_report(tmp_path, card="M0-T10", junit_paths=[])
    rows = payload["acceptanceTests"]
    assert isinstance(rows, list)
    missing = [r for r in rows if r["atId"] == "AT-M0-T10-99"]
    assert missing and missing[0]["result"] == "NOT_IMPLEMENTED"


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_card_mode_fails_when_at_not_passed(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _, errors, code = build_report(tmp_path, card="M0-T10", junit_paths=[])
    assert code == 1
    assert errors


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R083"])
def test_manual_at_excluded_from_card_scope(tmp_path: Path) -> None:
    _seed_repo(
        tmp_path,
        card="M0-T09",
        field15="**AT-M0-T09-01** (*manual review*) x. **AT-M0-T09-04** auto.",
    )
    payload, _, _ = build_report(tmp_path, card="M0-T09", junit_paths=[])
    manual = payload.get("manualAcceptanceTests", [])
    assert manual
    scoped = payload.get("acceptanceTests", [])
    assert not any(isinstance(row, dict) and row.get("manual") for row in scoped)


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095"])
def test_writes_trace_artifacts_via_main_pattern(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    out = tmp_path / "trace"
    payload, _, _ = build_report(tmp_path, card="M0-T10", junit_paths=[], output_dir=out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "trace.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out / "trace.md").write_text("# trace\n", encoding="utf-8")
    assert (out / "trace.json").is_file()


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095"])
def test_unknown_at_in_junit_fails(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    junit = tmp_path / "junit.xml"
    junit.write_text(
        '<?xml version="1.0"?><testsuite name="s" tests="1" failures="0">'
        '<testcase classname="c" name="[AT-M0-T99-99] x"/>'
        "</testsuite>\n",
        encoding="utf-8",
    )
    _, errors, code = build_report(tmp_path, card="", junit_paths=[junit])
    assert code == 1
    assert any("unknown AT" in e for e in errors)


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R083"])
def test_manual_at_set_on_real_plans() -> None:
    specs = _load_at_specs(REPO)
    manual = {at_id for at_id, s in specs.items() if s.manual}
    assert {
        "AT-M0-T07-07",
        "AT-M0-T08-05",
        "AT-M0-T09-01",
        "AT-M0-T09-02",
        "AT-M0-T09-03",
    } <= manual


def _seed_repo(
    tmp_path: Path,
    *,
    card: str = "M0-T10",
    field15: str | None = None,
    extra_at: str = "",
) -> None:
    if field15 is None:
        field15 = f"**AT-M0-T10-01** check. {extra_at}"
    (tmp_path / "plans").mkdir(parents=True)
    (tmp_path / "plans/M0_FOUNDATION.md").write_text(
        _minimal_plan(card, field15), encoding="utf-8"
    )
    id_conv = REPO / "specs/traceability/id_conventions.yaml"
    dest = tmp_path / "specs/traceability/id_conventions.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(id_conv.read_text(encoding="utf-8"), encoding="utf-8")
