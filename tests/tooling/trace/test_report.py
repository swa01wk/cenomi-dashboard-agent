"""trace-report acceptance tests (M0-T10, AT-M0-T10-04)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.trace import report as trace_mod
from scripts.trace.report import _load_at_specs, build_report

REPO = Path(__file__).resolve().parents[3]


def _minimal_plan(card_id: str, field15: str) -> str:
    return f"""# Plan

### {card_id} — title

| # | Field | Content |
|---|---|---|
| 15 | Acceptance criteria | {field15} |
"""


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


def _junit(at_id: str, *, skipped: bool = False, failed: bool = False) -> str:
    if skipped:
        body = f'<testcase classname="c" name="[{at_id}] x"><skipped/></testcase>'
    elif failed:
        body = f'<testcase classname="c" name="[{at_id}] x"><failure/></testcase>'
    else:
        body = f'<testcase classname="c" name="[{at_id}] x"/>'
    return (
        '<?xml version="1.0"?><testsuite name="s" tests="1" failures="0">'
        f"{body}</testsuite>\n"
    )


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_unknown_card_id_fails(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    with pytest.raises(ValueError, match="malformed"):
        build_report(tmp_path, card="not-a-card")


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_malformed_gate_fails(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    with pytest.raises(ValueError, match="malformed"):
        build_report(tmp_path, gate="M0-T01")


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095"])
def test_at_without_test_is_not_implemented(tmp_path: Path) -> None:
    _seed_repo(tmp_path, extra_at="**AT-M0-T10-99** never runs.")
    payload, _, _ = build_report(tmp_path, card="M0-T10", junit_paths=[])
    rows = payload["acceptanceTests"]
    assert isinstance(rows, list)
    missing = [r for r in rows if r["atId"] == "AT-M0-T10-99"]
    assert missing and missing[0]["result"] == "NOT_IMPLEMENTED"


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095"])
def test_skipped_test_reported_skipped(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    junit = tmp_path / "junit.xml"
    junit.write_text(_junit("AT-M0-T10-01", skipped=True), encoding="utf-8")
    payload, _, _ = build_report(tmp_path, card="M0-T10", junit_paths=[junit])
    row = next(r for r in payload["acceptanceTests"] if r["atId"] == "AT-M0-T10-01")
    assert row["result"] == "SKIPPED"


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_card_mode_fails_when_at_not_passed(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _, errors, code = build_report(tmp_path, card="M0-T10", junit_paths=[])
    assert code == 1
    assert errors


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_card_mode_passes_when_all_passed(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    junit = tmp_path / "junit.xml"
    junit.write_text(_junit("AT-M0-T10-01"), encoding="utf-8")
    _, errors, code = build_report(tmp_path, card="M0-T10", junit_paths=[junit])
    assert code == 0
    assert not errors


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
def test_main_writes_trace_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed_repo(tmp_path)
    fake_mod = tmp_path / "scripts" / "trace" / "report.py"
    fake_mod.parent.mkdir(parents=True, exist_ok=True)
    fake_mod.write_text("# stub\n", encoding="utf-8")
    monkeypatch.setattr(trace_mod, "__file__", str(fake_mod))
    monkeypatch.setenv("CARD", "M0-T10")
    monkeypatch.delenv("GATE", raising=False)
    code = trace_mod.main()
    out = tmp_path / "tests/reports/trace"
    assert code == 1
    assert (out / "trace.json").is_file()
    assert (out / "trace.md").is_file()


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095"])
@pytest.mark.parametrize("mode", ["", "M0-T10", "M0"])
def test_unknown_at_in_junit_fails_every_mode(
    tmp_path: Path, mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed_repo(tmp_path)
    junit = tmp_path / "junit.xml"
    junit.write_text(_junit("AT-M0-T99-99"), encoding="utf-8")
    kwargs: dict = {"junit_paths": [junit]}
    if mode.startswith("M0-T"):
        kwargs["card"] = mode
    elif mode:
        kwargs["gate"] = mode
    _, errors, code = build_report(tmp_path, **kwargs)
    assert code == 1
    assert any("unknown AT" in e for e in errors)


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095"])
def test_unreadable_junit_exits_with_filename(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    bad = tmp_path / "bad.xml"
    bad.write_text("not xml", encoding="utf-8")
    _, errors, code = build_report(tmp_path, junit_paths=[bad])
    assert code == 1
    assert any("bad.xml" in e for e in errors)


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R083"])
def test_manual_at_set_on_real_plans() -> None:
    specs = _load_at_specs(REPO)
    manual = {at_id for at_id, s in specs.items() if s.manual}
    assert manual == {
        "AT-M0-T07-07",
        "AT-M0-T08-05",
        "AT-M0-T09-01",
        "AT-M0-T09-02",
        "AT-M0-T09-03",
    }


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_gate_manual_without_result_fails(tmp_path: Path) -> None:
    _seed_repo(
        tmp_path,
        card="M0-T08",
        field15="**AT-M0-T08-05** (*manual record*) only.",
    )
    _, errors, code = build_report(tmp_path, gate="M0", junit_paths=[])
    assert code == 1
    assert any("AT-M0-T08-05" in e for e in errors)


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_gate_manual_with_result_passes_manual_check(tmp_path: Path) -> None:
    _seed_repo(
        tmp_path,
        card="M0-T08",
        field15="**AT-M0-T08-05** (*manual record*) only.",
    )
    gates = tmp_path / "plans/gates"
    gates.mkdir(parents=True)
    (gates / "M0-manual-results.json").write_text(
        json.dumps(
            {
                "schema": "cenomi.manual_results.v1",
                "milestone": "M0",
                "results": [{"atId": "AT-M0-T08-05", "result": "PASSED"}],
            }
        ),
        encoding="utf-8",
    )
    junit = tmp_path / "junit.xml"
    junit.write_text(_junit("AT-M0-T08-05"), encoding="utf-8")
    _, errors, code = build_report(tmp_path, gate="M0", junit_paths=[junit])
    assert not any("manual AT lacks" in e for e in errors)
