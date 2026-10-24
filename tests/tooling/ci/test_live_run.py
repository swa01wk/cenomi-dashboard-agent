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

from scripts.ci.summary import (
    STAGED_JUNIT_JSON,
    VERDICT_JSON,
    assert_live_summary_evidence,
    parse_card_from_branch,
)

MAKE_TARGETS = REPO_ROOT / "specs/engineering/make_targets.yaml"


def _target_rows() -> list[dict[str, str]]:
    data = yaml.safe_load(MAKE_TARGETS.read_text(encoding="utf-8"))
    return [
        {"name": str(t["name"]), "active_from": str(t["active_from"])}
        for t in data["targets"]
    ]


def _junit_paths() -> list[Path]:
    env_path = os.environ.get("CENOMI_CI_STAGED_JUNIT_JSON", "").strip()
    if env_path:
        rels = json.loads(Path(env_path).read_text(encoding="utf-8"))
        return [REPO_ROOT / rel for rel in rels if (REPO_ROOT / rel).is_file()]
    if STAGED_JUNIT_JSON.is_file():
        rels = json.loads(STAGED_JUNIT_JSON.read_text(encoding="utf-8"))
        return [REPO_ROOT / rel for rel in rels if (REPO_ROOT / rel).is_file()]
    from scripts.trace.report import DEFAULT_JUNIT_REL

    return [REPO_ROOT / rel for rel in DEFAULT_JUNIT_REL if (REPO_ROOT / rel).is_file()]


def _status_records() -> list[dict]:
    records: list[dict] = []
    for path in (REPO_ROOT / "tests/reports").rglob("status.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


@pytest.mark.trace("AT-M0-T07-02", reqs=["ARCH-R105", "DEVENV-R031"])
def test_at_m0_t07_02_live_summary() -> None:
    assert VERDICT_JSON.is_file(), "summary must write verdict before live test"
    verdict = json.loads(VERDICT_JSON.read_text(encoding="utf-8"))
    assert verdict.get("success") is True, verdict.get("errors")
    assert not verdict.get("errors"), verdict.get("errors")

    pr_card = parse_card_from_branch(os.environ.get("HEAD_BRANCH", "").strip() or None)
    junit_paths = _junit_paths()
    status_records = _status_records()

    evidence_errors = assert_live_summary_evidence(
        repo=REPO_ROOT,
        verdict=verdict,
        junit_paths=junit_paths,
        status_records=status_records,
        pr_card=pr_card,
        make_targets=_target_rows(),
    )
    assert not evidence_errors, evidence_errors
