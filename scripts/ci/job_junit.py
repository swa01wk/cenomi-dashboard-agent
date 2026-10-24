"""Per-job JUnit artefact paths for CI upload and summary (M0-T07)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.trace.report import DEFAULT_JUNIT_REL

# Each path in DEFAULT_JUNIT_REL is owned by exactly one make_ci job.
JOB_JUNIT: dict[str, list[str]] = {
    "ci/backend": [
        "tests/reports/backend/junit-unit.xml",
        "tests/reports/backend/junit-integration.xml",
    ],
    "ci/specs": ["tests/reports/backend/junit-tooling.xml"],
    "ci/frontend": ["tests/reports/frontend/junit-vitest.xml"],
    "ci/e2e": ["tests/reports/e2e/junit-playwright.xml"],
}

JUNIT_PRODUCER_TARGET: dict[str, str] = {
    "junit-unit.xml": "backend-test",
    "junit-integration.xml": "backend-test",
    "junit-tooling.xml": "backend-test",
    "junit-vitest.xml": "frontend-test",
    "junit-playwright.xml": "e2e",
}

BASENAME_TO_REL: dict[str, Path] = {
    Path(rel).name: Path(rel) for rel in DEFAULT_JUNIT_REL
}


def upload_staging_dir(job_name: str) -> Path:
    """Directory of flat basename copies for upload-artifact (prefix strip safe)."""
    slug = job_name.removeprefix("ci/").replace("/", "-")
    return Path("tests/reports/ci/junit-upload") / f"ci-{slug}"


def assert_job_junit_covers_default() -> None:
    covered: list[str] = []
    for paths in JOB_JUNIT.values():
        covered.extend(paths)
    if set(covered) != set(DEFAULT_JUNIT_REL):
        missing = set(DEFAULT_JUNIT_REL) - set(covered)
        extra = set(covered) - set(DEFAULT_JUNIT_REL)
        raise AssertionError(
            f"JOB_JUNIT must match DEFAULT_JUNIT_REL; missing={missing!r} extra={extra!r}"
        )
    if len(covered) != len(DEFAULT_JUNIT_REL):
        raise AssertionError("JOB_JUNIT must assign each DEFAULT_JUNIT_REL path once")


def compute_full_evidence_run(
    *,
    applicability: dict[str, Any],
    staged_paths: list[Path],
    repo_root: Path,
    ci: dict[str, Any] | None = None,
) -> tuple[bool, list[str]]:
    """
    True when every JOB_JUNIT job was applicable and all of its JUnit paths were staged.
    """
    from scripts.ci.changes import job_make_ci, load_ci_checks

    ci = ci or load_ci_checks()
    published = {r["job"]: r for r in applicability.get("jobs", [])}
    staged_rels: set[str] = set()
    for path in staged_paths:
        try:
            staged_rels.add(path.relative_to(repo_root).as_posix())
        except ValueError:
            staged_rels.add(path.as_posix())

    not_applicable: list[str] = []
    for job_name, rel_paths in sorted(JOB_JUNIT.items()):
        if not job_make_ci(job_name, ci):
            continue
        applicable = published.get(job_name, {}).get("applicable", True)
        if not applicable:
            not_applicable.append(job_name)
            continue
        for rel in rel_paths:
            if rel not in staged_rels:
                return False, not_applicable
    return (len(not_applicable) == 0), not_applicable
