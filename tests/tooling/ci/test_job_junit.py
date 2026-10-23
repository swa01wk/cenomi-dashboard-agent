"""JOB_JUNIT map vs DEFAULT_JUNIT_REL (M0-T07)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.job_junit import assert_job_junit_covers_default


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R031"])
def test_job_junit_matches_default_junit_rel() -> None:
    assert_job_junit_covers_default()
