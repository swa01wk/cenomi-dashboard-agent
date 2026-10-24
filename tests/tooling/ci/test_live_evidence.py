"""Unit tests for full vs partial CI evidence runs (DEF-0005)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.changes import compute_applicability, job_make_ci, load_ci_checks
from scripts.ci.job_junit import JOB_JUNIT, compute_full_evidence_run
from scripts.ci.summary import assert_live_summary_evidence, parse_card_from_branch

MAKE_TARGETS = REPO_ROOT / "specs/engineering/make_targets.yaml"
CI = load_ci_checks()


def _target_rows() -> list[dict[str, str]]:
    data = yaml.safe_load(MAKE_TARGETS.read_text(encoding="utf-8"))
    return [
        {"name": str(t["name"]), "active_from": str(t["active_from"])}
        for t in data["targets"]
    ]


def _docs_only_applicability() -> dict:
    return compute_applicability(
        changed_files=["plans/M0_FOUNDATION.md"],
        event_mode="pull_request",
        ci=CI,
    )


def test_docs_only_is_not_full_evidence() -> None:
    apps = _docs_only_applicability()
    published = {r["job"]: r["applicable"] for r in apps["jobs"]}
    full, not_app = compute_full_evidence_run(
        applicability=apps,
        staged_paths=[],
        repo_root=REPO_ROOT,
        ci=CI,
    )
    assert not full
    for job in JOB_JUNIT:
        if not job_make_ci(job, CI):
            continue
        if not published.get(job, True):
            assert job in not_app
        else:
            assert job not in not_app


def test_partial_run_skips_evidence_checks_despite_window_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Documentation-only applicability: live evidence checks are not evaluated."""
    import scripts.ci.summary as summary_mod

    monkeypatch.setattr(summary_mod, "REPO_ROOT", tmp_path)
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
    monkeypatch: pytest.MonkeyPatch,
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


def test_push_main_event_full_evidence_with_all_junit(tmp_path: Path) -> None:
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
