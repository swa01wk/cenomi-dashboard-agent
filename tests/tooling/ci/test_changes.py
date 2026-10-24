"""AT-M0-T07-03 — path classification for ci/changes."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.changes import compute_applicability, load_ci_checks

CI = load_ci_checks()


def _applicable(files: list[str]) -> dict[str, bool]:
    result = compute_applicability(
        changed_files=files, event_mode="pull_request", ci=CI
    )
    return {r["job"]: r["applicable"] for r in result["jobs"]}


ALWAYS = {
    "ci/changes",
    "ci/specs",
    "ci/security",
    "ci/quarantine",
    "ci/summary",
}


@pytest.mark.trace("AT-M0-T07-03", reqs=["DEVENV-R019", "DEVENV-R047"])
def test_docs_only_selects_always_run_jobs() -> None:
    apps = _applicable(["plans/M0_FOUNDATION.md"])
    for job, ok in apps.items():
        if job in ALWAYS:
            assert ok, job
        else:
            assert not ok, job


@pytest.mark.trace("AT-M0-T07-03", reqs=["DEVENV-R049"])
def test_specs_change_selects_every_job() -> None:
    apps = _applicable(["specs/engineering/ci_checks.yaml"])
    assert all(apps.values())


@pytest.mark.trace("AT-M0-T07-03", reqs=["DEVENV-R019"])
def test_frontend_only_does_not_select_database() -> None:
    apps = _applicable(["apps/web/src/page.tsx"])
    assert apps["ci/database"] is False
    assert apps["ci/frontend"] is True


@pytest.mark.trace("AT-M0-T07-03", reqs=["DEVENV-R048"])
def test_uncategorized_file_selects_every_job() -> None:
    apps = _applicable(["mystery-root-file.xyz"])
    assert all(apps.values())


@pytest.mark.trace("AT-M0-T07-03", reqs=["DEVENV-R048"])
def test_uncomputable_diff_selects_every_job() -> None:
    result = compute_applicability(changed_files=None, event_mode="pull_request", ci=CI)
    assert all(r["applicable"] for r in result["jobs"])
