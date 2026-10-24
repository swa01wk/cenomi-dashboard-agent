"""JOB_JUNIT map vs DEFAULT_JUNIT_REL (M0-T07)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.changes import compute_applicability, load_ci_checks
from scripts.ci.job_junit import (
    JOB_JUNIT,
    assert_job_junit_covers_default,
    compute_full_evidence_run,
)

CI = load_ci_checks()


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R031"])
def test_job_junit_matches_default_junit_rel() -> None:
    assert_job_junit_covers_default()


def test_compute_full_evidence_all_jobs_applicable_and_staged(tmp_path: Path) -> None:
    apps = compute_applicability(
        changed_files=["specs/engineering/ci_checks.yaml"],
        event_mode="pull_request",
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
