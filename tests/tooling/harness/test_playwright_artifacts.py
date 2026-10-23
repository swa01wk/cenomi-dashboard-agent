"""AT-M0-T11-04 — Playwright failure artefacts from an isolated harness run."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HARNESS_PW = Path(__file__).resolve().parent / "fixtures" / "playwright"
ARTIFACTS_DIR = REPO_ROOT / "tests" / "reports" / "harness" / "playwright-artifacts"
NETWORK_LOG = ARTIFACTS_DIR / "network-log.json"
EXPECTED_REQUEST_REF = "req-fixture-m0-t11-04"


def _run_harness_playwright(*, grep: str | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [
        "pnpm",
        "exec",
        "playwright",
        "test",
        "--config",
        str(HARNESS_PW / "playwright.config.ts"),
        "--project=desktop",
    ]
    if grep:
        cmd.extend(["--grep", grep])
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.trace("AT-M0-T11-04", reqs=["ARCH-R087", "DEVENV-R029"])
def test_failure_artefacts_and_request_ref(tmp_path: Path) -> None:
    del tmp_path
    if ARTIFACTS_DIR.is_dir():
        shutil.rmtree(ARTIFACTS_DIR)

    proc = _run_harness_playwright(grep="AT-M0-T11-04")
    assert proc.returncode == 1, proc.stdout + proc.stderr

    traces = list(ARTIFACTS_DIR.rglob("trace.zip"))
    screenshots = list(ARTIFACTS_DIR.rglob("*.png"))
    videos = list(ARTIFACTS_DIR.rglob("*.webm"))
    assert traces, f"missing trace.zip under {ARTIFACTS_DIR}"
    assert screenshots, f"missing screenshot under {ARTIFACTS_DIR}"
    assert videos, f"missing video under {ARTIFACTS_DIR}"

    assert NETWORK_LOG.is_file(), f"missing network log at {NETWORK_LOG}"
    entries = json.loads(NETWORK_LOG.read_text(encoding="utf-8"))
    refs = [entry.get("requestRef") for entry in entries if entry.get("requestRef")]
    assert EXPECTED_REQUEST_REF in refs
