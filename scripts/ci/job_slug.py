"""Map ci_checks job names to artifact slugs."""

from __future__ import annotations


def job_to_artifact_slug(job_name: str) -> str:
    """ci/static -> ci-static; ci/echarts-gate -> ci-echarts-gate."""
    if job_name.startswith("ci/"):
        return "ci-" + job_name.removeprefix("ci/")
    return job_name.replace("/", "-")


def artifact_slug_to_job(slug: str) -> str:
    """ci-static -> ci/static."""
    if slug.startswith("ci-"):
        return "ci/" + slug.removeprefix("ci-")
    return slug.replace("-", "/", 1) if "-" in slug else slug
