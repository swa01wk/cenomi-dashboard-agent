"""AT-M0-T07-02 — live test is deselected unless summary invokes it."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _collect_live_test_ids(env: dict[str, str]) -> str:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/tooling/ci/test_live_run.py",
            "--collect-only",
            "-q",
        ],
        cwd=REPO_ROOT,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout + proc.stderr


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R105"])
def test_live_run_deselected_without_summary_env() -> None:
    out = _collect_live_test_ids(
        {"GITHUB_ACTIONS": "true", "CENOMI_CI_SUMMARY_LIVE": ""},
    )
    assert "test_at_m0_t07_02_live_summary" not in out


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R105"])
def test_live_run_collected_when_summary_invokes() -> None:
    out = _collect_live_test_ids(
        {"GITHUB_ACTIONS": "true", "CENOMI_CI_SUMMARY_LIVE": "1"},
    )
    assert "test_at_m0_t07_02_live_summary" in out
