"""AT-M0-T07-02 — live CI summary compensating control (EXC-001 C5)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.summary import BOOTSTRAP_CARDS, VERDICT_JSON
from scripts.make.report import milestone_index, read_active_milestone
from scripts.trace.report import build_report

SPEC_SET = REPO_ROOT / "specs/engineering/spec_set.yaml"
MAKE_TARGETS = REPO_ROOT / "specs/engineering/make_targets.yaml"

MERGED_M0_CARDS = frozenset({"M0-T01", "M0-T03", "M0-T10", "M0-T11", "M0-T07"})


def _merged_m0_cards() -> set[str]:
    """Cards whose implementation is on main before/at M0-T07 merge."""
    return set(MERGED_M0_CARDS)


def _target_rows() -> list[dict[str, str]]:
    data = yaml.safe_load(MAKE_TARGETS.read_text(encoding="utf-8"))
    return [
        {
            "name": str(t["name"]),
            "active_from": str(t["active_from"]),
        }
        for t in data["targets"]
    ]


@pytest.mark.trace("AT-M0-T07-02", reqs=["ARCH-R105", "DEVENV-R031"])
def test_at_m0_t07_02_live_summary() -> None:
    if os.environ.get("GITHUB_ACTIONS", "").strip().lower() != "true":
        pytest.skip("AT-M0-T07-02 runs only in GitHub Actions")

    assert VERDICT_JSON.is_file(), "summary must write verdict before live test"
    verdict = json.loads(VERDICT_JSON.read_text(encoding="utf-8"))
    assert verdict.get("success") is True, verdict.get("errors")
    assert not verdict.get("errors"), verdict.get("errors")

    active = read_active_milestone(SPEC_SET)
    active_idx = milestone_index(active)

    status_paths = list((REPO_ROOT / "tests/reports").rglob("status.jsonl"))
    records: list[dict] = []
    for path in status_paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))

    merged_cards = _merged_m0_cards()
    for row in _target_rows():
        name = row["name"]
        active_from = row["active_from"]
        from_idx = milestone_index(active_from)
        recs = [r for r in records if r.get("item") == name and r.get("kind") == "target"]
        if not recs:
            continue
        result = recs[-1].get("result")
        if active_from.startswith("M0") and active_from not in merged_cards:
            assert result == "NOT_IMPLEMENTED", f"{name}: expected NOT_IMPLEMENTED, got {result}"
        elif from_idx > active_idx:
            assert result == "NOT_APPLICABLE", f"{name}: expected NOT_APPLICABLE, got {result}"

    junit_dir = REPO_ROOT / "tests/reports"
    junit_paths = sorted(junit_dir.rglob("junit*.xml"))
    for card in BOOTSTRAP_CARDS:
        payload, errors, code = build_report(REPO_ROOT, junit_paths=junit_paths, card=card)
        assert code == 0, f"{card}: build_report failed: {errors}"
        tests = payload.get("acceptanceTests")
        assert isinstance(tests, list)
        for row in tests:
            if not isinstance(row, dict) or row.get("manual"):
                continue
            assert row.get("result") == "PASSED", f"{card} {row.get('atId')}: {row.get('result')}"
