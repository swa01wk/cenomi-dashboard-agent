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
from scripts.ci.summary import (
    evaluate,
    evaluate_card_rule,
    evaluate_verdict,
    load_required_json,
    stage_junit_artifacts,
)

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
    def fake_build_report(*args: Any, **kwargs: Any) -> tuple[dict, list[str], int]:
        return {}, ["fixture failure"], 1

    monkeypatch.setattr(
        "scripts.ci.summary.build_report",
        fake_build_report,
    )
    jobs = _all_jobs_success()
    apps = _applicability([".github/workflows/ci.yml"])
    verdict = evaluate_verdict(
        job_conclusions=jobs,
        applicability=apps,
        changed_files=[".github/workflows/ci.yml"],
        event_mode="pull_request",
        status_records=[],
        job_status_files=_status_files_for_applicable(jobs, apps, tmp_path),
        active_milestone="M0",
        ci=CI,
    )
    assert verdict.success
    card_out = evaluate_card_rule(card="M0-T07", junit_paths=[])
    assert not card_out.success
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
        junit_paths=[],
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


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R105"])
def test_summary_order_verdict_before_card_rule(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    order: list[str] = []

    def fake_verdict(**kwargs: Any) -> Any:
        order.append("verdict")
        from scripts.ci.summary import SummaryOutcome

        return SummaryOutcome(success=True)

    def fake_write_verdict(outcome: Any, path: Path | None = None) -> None:
        order.append("write_verdict")
        path = path or tmp_path / "verdict.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"success": true, "errors": [], "warnings": []}', encoding="utf-8")

    def fake_live() -> tuple[int, Path | None]:
        order.append("live")
        return 0, None

    def fake_card(**kwargs: Any) -> Any:
        order.append("card")
        from scripts.ci.summary import SummaryOutcome

        return SummaryOutcome(success=True)

    monkeypatch.setattr("scripts.ci.summary.evaluate_verdict", fake_verdict)
    monkeypatch.setattr("scripts.ci.summary.write_verdict_json", fake_write_verdict)
    monkeypatch.setattr("scripts.ci.summary.run_live_summary_test", fake_live)
    monkeypatch.setattr("scripts.ci.summary.evaluate_card_rule", fake_card)
    monkeypatch.setattr("scripts.ci.summary.write_card_trace_artifacts", fake_card)
    monkeypatch.setattr("scripts.ci.summary.stage_junit_artifacts", lambda _p: ([], []))
    monkeypatch.setattr(
        "scripts.ci.summary.parse_card_from_branch", lambda _b: "M0-T07"
    )

    from scripts.ci.summary import main

    app_json = tmp_path / "app.json"
    app_json.write_text(
        '{"jobs": [{"job": "ci/static", "applicable": true}], "changed_files": []}',
        encoding="utf-8",
    )
    jobs_json = tmp_path / "jobs.json"
    jobs_json.write_text('{"ci/changes": "success", "ci/static": "success"}', encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "summary.py",
            "--applicability",
            str(app_json),
            "--jobs-json",
            str(jobs_json),
            "--head-branch",
            "chore/m0-t07-ci-workflows",
        ],
    )
    assert main() == 0
    assert order.index("verdict") < order.index("live") < order.index("card")


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R031"])
def test_stage_junit_duplicate_dest_fails(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    a = root / "junit-ci-backend" / "tests/reports/backend/junit-unit.xml"
    b = root / "junit-ci-specs" / "tests/reports/backend/junit-unit.xml"
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    a.write_text('<?xml version="1.0"?><testsuite></testsuite>', encoding="utf-8")
    b.write_text('<?xml version="1.0"?><testsuite></testsuite>', encoding="utf-8")
    paths, errors = stage_junit_artifacts(root)
    assert not paths
    assert any("duplicate" in e for e in errors)


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R031"])
def test_stage_junit_places_at_default_rel(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import scripts.ci.summary as summary_mod

    monkeypatch.setattr(summary_mod, "REPO_ROOT", tmp_path)
    root = tmp_path / "artifacts"
    src = root / "junit-ci-specs" / "tests/reports/backend/junit-tooling.xml"
    src.parent.mkdir(parents=True)
    src.write_text('<?xml version="1.0"?><testsuite></testsuite>', encoding="utf-8")
    paths, errors = stage_junit_artifacts(root)
    assert not errors
    dest = tmp_path / "tests/reports/backend/junit-tooling.xml"
    assert dest.is_file()
    assert dest in paths


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R031"])
def test_stage_junit_skips_copy_when_source_is_dest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scripts.ci.summary as summary_mod

    monkeypatch.setattr(summary_mod, "REPO_ROOT", tmp_path)
    dest = tmp_path / "tests/reports/backend/junit-tooling.xml"
    dest.parent.mkdir(parents=True)
    dest.write_text('<?xml version="1.0"?><testsuite></testsuite>', encoding="utf-8")
    root = tmp_path / "artifacts" / "junit-ci-specs"
    src = root / "tests/reports/backend/junit-tooling.xml"
    src.parent.mkdir(parents=True)
    src.symlink_to(dest.resolve())
    paths, errors = stage_junit_artifacts(root)
    assert not errors
    assert dest in paths
