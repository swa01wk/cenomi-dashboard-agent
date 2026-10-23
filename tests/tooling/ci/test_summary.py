"""AT-M0-T07-04 — ci/summary fail-closed semantics."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.changes import compute_applicability, job_make_ci, load_ci_checks
from scripts.ci.summary import evaluate, load_required_json

CI = load_ci_checks()


def _status_files_for_applicable(
    job_conclusions: dict[str, str | None],
    applicability: dict[str, Any],
    tmp_path: Path,
) -> dict[str, Path]:
    published = {r["job"]: r["applicable"] for r in applicability["jobs"]}
    files: dict[str, Path] = {}
    for job, conclusion in job_conclusions.items():
        if job == "ci/summary":
            continue
        if not job_make_ci(job, CI):
            continue
        if not published.get(job):
            continue
        if conclusion in (None, "skipped"):
            continue
        path = tmp_path / f"{job.replace('/', '_')}.jsonl"
        path.write_text(
            '{"item":"ci","result":"PASSED","reason":"fixture"}\n',
            encoding="utf-8",
        )
        files[job] = path
    return files


def _applicability(
    files: list[str] | None, event: str = "pull_request"
) -> dict[str, Any]:
    return compute_applicability(changed_files=files, event_mode=event, ci=CI)


def _all_jobs_success(exclude: set[str] | None = None) -> dict[str, str]:
    exclude = exclude or set()
    return {
        j["name"]: "success"
        for j in CI["jobs"]
        if j["name"] not in exclude and j["name"] != "ci/summary"
    }


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R020"])
@pytest.mark.parametrize(
    "conclusion",
    ["failure", "cancelled", "timed_out", "neutral", None],
)
def test_blocking_job_bad_conclusion_fails(
    conclusion: str | None, tmp_path: Path
) -> None:
    jobs = _all_jobs_success()
    jobs["ci/static"] = conclusion
    apps = _applicability(["backend/src/cenomi/api/main.py"])
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=["backend/src/cenomi/api/main.py"],
        event_mode="pull_request",
        head_branch=None,
        status_records=[],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert not out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R020"])
def test_skipped_while_applicable_fails(tmp_path: Path) -> None:
    files = ["backend/src/cenomi/api/main.py"]
    jobs = _all_jobs_success()
    jobs["ci/backend"] = "skipped"
    apps = _applicability(files)
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=files,
        event_mode="pull_request",
        head_branch=None,
        status_records=[],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert not out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R050"])
def test_applicability_disagreement_fails(tmp_path: Path) -> None:
    files = ["backend/src/cenomi/api/main.py"]
    published = _applicability(files)
    published["jobs"][0]["applicable"] = not published["jobs"][0]["applicable"]
    jobs = _all_jobs_success()
    out = evaluate(
        job_conclusions=jobs,
        applicability=published,
        changed_files=files,
        event_mode="pull_request",
        head_branch=None,
        status_records=[],
        job_status_files=_status_files_for_applicable(jobs, published, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert not out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R050"])
def test_failed_changes_job_fails() -> None:
    jobs = _all_jobs_success()
    jobs["ci/changes"] = "failure"
    out = evaluate(
        job_conclusions=jobs,
        applicability=_applicability(["docs/readme.md"]),
        changed_files=["docs/readme.md"],
        event_mode="pull_request",
        head_branch=None,
        status_records=[],
        active_milestone="M0",
        ci=CI,
    )
    assert not out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R050"])
def test_missing_job_from_run_fails(tmp_path: Path) -> None:
    jobs = _all_jobs_success()
    del jobs["ci/backend"]
    apps = _applicability(["backend/src/cenomi/api/main.py"])
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=["backend/src/cenomi/api/main.py"],
        event_mode="pull_request",
        head_branch=None,
        status_records=[],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert not out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R101"])
def test_failed_status_jsonl_fails(tmp_path: Path) -> None:
    jobs = _all_jobs_success()
    apps = _applicability(["plans/M0_FOUNDATION.md"])
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=["plans/M0_FOUNDATION.md"],
        event_mode="pull_request",
        head_branch=None,
        status_records=[{"item": "doctor", "result": "FAILED", "reason": "x"}],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert not out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R103"])
def test_not_implemented_before_active_milestone_fails(tmp_path: Path) -> None:
    jobs = _all_jobs_success()
    apps = _applicability(["plans/M0_FOUNDATION.md"])
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=["plans/M0_FOUNDATION.md"],
        event_mode="pull_request",
        head_branch=None,
        status_records=[
            {"item": "doctor", "result": "NOT_IMPLEMENTED", "reason": "stub"}
        ],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M1",
        ci=CI,
    )
    assert not out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R105"])
def test_card_branch_trace_not_passed_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import subprocess

    def fake_run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args, returncode=1, stdout="", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    jobs = _all_jobs_success()
    apps = _applicability([".github/workflows/ci.yml"])
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=[".github/workflows/ci.yml"],
        event_mode="pull_request",
        head_branch="chore/m0-t07-ci-workflows",
        status_records=[],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert not out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R020"])
def test_allowed_skip_when_not_applicable_passes(tmp_path: Path) -> None:
    files = ["plans/M0_FOUNDATION.md"]
    jobs = _all_jobs_success()
    jobs["ci/static"] = "skipped"
    apps = _applicability(files)
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=files,
        event_mode="pull_request",
        head_branch=None,
        status_records=[],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R103"])
def test_not_implemented_in_build_window_passes(tmp_path: Path) -> None:
    jobs = _all_jobs_success()
    apps = _applicability(["plans/M0_FOUNDATION.md"])
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=["plans/M0_FOUNDATION.md"],
        event_mode="pull_request",
        head_branch=None,
        status_records=[{"item": "e2e", "result": "NOT_IMPLEMENTED", "reason": "stub"}],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R031"])
def test_echarts_gate_non_blocking_before_m2(tmp_path: Path) -> None:
    jobs = _all_jobs_success()
    jobs["ci/echarts-gate"] = "failure"
    apps = _applicability(["packages/viz/package.json"])
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=["packages/viz/package.json"],
        event_mode="pull_request",
        head_branch=None,
        status_records=[],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert out.success
    assert any("non-blocking" in w for w in out.warnings)


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R020"])
def test_missing_applicability_file_fails(tmp_path: Path) -> None:
    missing = tmp_path / "applicability.json"
    with pytest.raises(FileNotFoundError):
        load_required_json(missing, "applicability")


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R020"])
def test_unreadable_job_conclusions_fails(tmp_path: Path) -> None:
    bad = tmp_path / "jobs.json"
    bad.write_text("{not-json", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        load_required_json(bad, "job-conclusions")


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R050"])
def test_missing_status_artifact_for_non_make_ci_job_passes(tmp_path: Path) -> None:
    files = ["backend/Dockerfile"]
    jobs = _all_jobs_success()
    apps = _applicability(files)
    status_files = _status_files_for_applicable(jobs, apps, tmp_path)
    assert "ci/images" not in status_files
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=files,
        event_mode="pull_request",
        head_branch=None,
        status_records=[],
        job_status_files=status_files,
        active_milestone="M0",
        ci=CI,
    )
    assert out.success


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R050"])
def test_missing_status_artifact_for_applicable_job_fails(tmp_path: Path) -> None:
    files = ["backend/src/cenomi/api/main.py"]
    jobs = _all_jobs_success()
    apps = _applicability(files)
    out = evaluate(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=files,
        event_mode="pull_request",
        head_branch=None,
        status_records=[],
        job_status_files={},
        active_milestone="M0",
        ci=CI,
    )
    assert not out.success
    assert any("missing status report" in e for e in out.errors)
