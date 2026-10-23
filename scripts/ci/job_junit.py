"""Per-job JUnit artefact paths for CI upload and summary (M0-T07)."""

from __future__ import annotations

from pathlib import Path

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
