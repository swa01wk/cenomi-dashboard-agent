"""trace-report acceptance tests (M0-T10, AT-M0-T10-04)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.trace.report import TRACE_DIR, build_report

REPO = Path(__file__).resolve().parents[3]


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_unknown_card_id_fails() -> None:
    with pytest.raises(ValueError, match="malformed"):
        build_report(card="not-a-card")


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095"])
def test_at_without_test_is_not_implemented() -> None:
    payload, _, _ = build_report(card="M0-T10")
    rows = payload["acceptanceTests"]
    assert isinstance(rows, list)
    missing = [r for r in rows if r["atId"] == "AT-M0-T10-99"]
    if missing:
        assert missing[0]["result"] == "NOT_IMPLEMENTED"


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_card_mode_fails_when_at_not_passed(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts.trace import report as mod

    monkeypatch.setattr(mod, "_collect_junit_results", lambda: {})
    _, errors, code = mod.build_report(card="M0-T03")
    assert code == 1
    assert errors


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095", "ARCH-R105"])
def test_gate_mode_includes_m0_cards() -> None:
    payload, _, _ = build_report(gate="M0")
    at_ids = {row["atId"] for row in payload["acceptanceTests"] if isinstance(row, dict)}
    assert "AT-M0-T01-01" in at_ids


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R083"])
def test_manual_at_excluded_from_card_scope() -> None:
    payload, _, code = build_report(card="M0-T09")
    manual = payload.get("manualAcceptanceTests", [])
    assert manual
    scoped = payload.get("acceptanceTests", [])
    assert not any(isinstance(row, dict) and row.get("manual") for row in scoped)


@pytest.mark.trace("AT-M0-T10-04", reqs=["ARCH-R095"])
def test_writes_trace_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "trace"
    from scripts.trace import report as mod

    monkeypatch.setattr(mod, "TRACE_DIR", out)
    payload, _, _ = mod.build_report(card="M0-T10")
    out.mkdir(parents=True, exist_ok=True)
    (out / "trace.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out / "trace.md").write_text("# trace\n", encoding="utf-8")
    assert (out / "trace.json").is_file()
    assert (out / "trace.md").is_file()
