"""Copy a job's JUnit files into a flat upload staging directory."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.job_junit import JOB_JUNIT, upload_staging_dir


def stage(job_name: str) -> Path:
    rel_paths = JOB_JUNIT.get(job_name, [])
    staging = REPO_ROOT / upload_staging_dir(job_name)
    if staging.exists():
        shutil.rmtree(staging)
    if not rel_paths:
        return staging
    staging.mkdir(parents=True, exist_ok=True)
    for rel in rel_paths:
        src = REPO_ROOT / rel
        if src.is_file():
            shutil.copy2(src, staging / src.name)
    return staging


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: stage_job_junit_upload.py <ci/job>", file=sys.stderr)
        return 2
    job = sys.argv[1]
    if job not in JOB_JUNIT:
        print(f"unknown or non-junit job: {job!r}", file=sys.stderr)
        return 2
    stage(job)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
