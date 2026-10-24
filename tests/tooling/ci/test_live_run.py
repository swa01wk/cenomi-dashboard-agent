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

from scripts.ci.changes import compute_applicability, load_ci_checks
from scripts.ci.job_junit import JOB_JUNIT, compute_full_evidence_run
from scripts.ci.summary import (
    STAGED_JUNIT_JSON,
    VERDICT_JSON,
    assert_live_summary_evidence,
    parse_card_from_branch,
)

MAKE_TARGETS = REPO_ROOT / "specs/engineering/make_targets.yaml"
CI = load_ci_checks()


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


def _docs_only_applicability() -> dict:
    return compute_applicability(
        changed_files=["plans/M0_FOUNDATION.md"],
        event_mode="pull_request",
        ci=CI,
    )


def test_docs_only_is_not_full_evidence() -> None:
    apps = _docs_only_applicability()
    full, not_app = compute_full_evidence_run(
        applicability=apps,
        staged_paths=[],
        repo_root=REPO_ROOT,
        ci=CI,
    )
    assert not full
    assert not_app
    assert set(not_app) == set(JOB_JUNIT.keys())


def test_partial_run_skips_evidence_checks_despite_window_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Documentation-only applicability: live evidence checks are not evaluated."""
    import scripts.ci.summary as summary_mod

    monkeypatch.setattr(summary_mod, "REPO_ROOT", tmp_path)
    apps = _docs_only_applicability()
    verdict = {
        "success": True,
        "errors": [],
        "warnings": [],
        "full_evidence_run": False,
        "jobs_not_applicable": list(JOB_JUNIT.keys()),
        "live_checks_not_evaluated": ["build-window target inference (M0 implemented cards)"],
    }
    status = [
        {
            "item": "backend-test",
            "kind": "target",
            "result": "PASSED",
        }
    ]
    errors = assert_live_summary_evidence(
        repo=tmp_path,
        verdict=verdict,
        junit_paths=[],
        status_records=status,
        pr_card=None,
        make_targets=_target_rows(),
    )
    assert not errors


def test_full_evidence_run_fails_bootstrap_when_at_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scripts.ci.summary as summary_mod

    monkeypatch.setattr(summary_mod, "REPO_ROOT", REPO_ROOT)
    tooling = REPO_ROOT / "tests/reports/backend/junit-tooling.xml"
    if not tooling.is_file():
        pytest.skip("run make backend-test SUITE=tooling to generate junit-tooling.xml")

    junit_paths = [tooling]

    verdict = {
        "success": True,
        "errors": [],
        "full_evidence_run": True,
    }
    errors = assert_live_summary_evidence(
        repo=REPO_ROOT,
        verdict=verdict,
        junit_paths=junit_paths,
        status_records=[],
        pr_card=None,
        make_targets=_target_rows(),
    )
    assert errors


def test_pr_card_branch_parsing_unchanged() -> None:
    assert parse_card_from_branch("feat/m0-t07-ci-workflows") == "M0-T07"
    assert parse_card_from_branch("main") is None


def test_push_main_event_full_evidence_with_all_junit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Push to main with all JOB_JUNIT artefacts staged is a full evidence run."""
    apps = compute_applicability(
        changed_files=[],
        event_mode="push",
        ci=CI,
    )
    staged: list[Path] = []
    for rels in JOB_JUNIT.values():
        for rel in rels:
            path = tmp_path / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                '<?xml version="1.0"?><testsuite></testsuite>', encoding="utf-8"
            )
            staged.append(path)
    full, not_app = compute_full_evidence_run(
        applicability=apps,
        staged_paths=staged,
        repo_root=tmp_path,
        ci=CI,
    )
    assert full
    assert not not_app


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
