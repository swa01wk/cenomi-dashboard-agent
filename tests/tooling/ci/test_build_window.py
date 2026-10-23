"""Build-window helpers for ci/summary live AT (ARCH-R103)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.build_window import assert_build_window_targets, implemented_m0_cards

MAKE_TARGETS = REPO_ROOT / "specs/engineering/make_targets.yaml"


def _target_rows() -> list[dict[str, str]]:
    data = yaml.safe_load(MAKE_TARGETS.read_text(encoding="utf-8"))
    return [
        {"name": str(t["name"]), "active_from": str(t["active_from"])}
        for t in data["targets"]
    ]


@pytest.mark.trace("AT-M0-T07-02", reqs=["ARCH-R103"])
def test_m0_t07_implemented_on_main_without_live_at(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_build_report(
        repo: Path, *, junit_paths: list[Path], card: str, **kwargs: object
    ) -> tuple[dict, list[str], int]:
        if card != "M0-T07":
            return {"acceptanceTests": []}, [], 0
        return {
            "acceptanceTests": [
                {"atId": "AT-M0-T07-01", "manual": False, "result": "PASSED"},
                {"atId": "AT-M0-T07-02", "manual": False, "result": "NOT_IMPLEMENTED"},
                {"atId": "AT-M0-T07-03", "manual": False, "result": "PASSED"},
            ]
        }, [], 0

    monkeypatch.setattr("scripts.ci.build_window.build_report", fake_build_report)

    implemented = implemented_m0_cards(
        REPO_ROOT, junit_paths=[], pr_card=None
    )
    assert "M0-T07" in implemented

    errors = assert_build_window_targets(
        repo=REPO_ROOT,
        status_records=[{"item": "ci", "kind": "target", "result": "PASSED"}],
        junit_paths=[],
        pr_card=None,
        make_targets=_target_rows(),
    )
    ci_errors = [e for e in errors if e.startswith("ci:")]
    assert not ci_errors, ci_errors
