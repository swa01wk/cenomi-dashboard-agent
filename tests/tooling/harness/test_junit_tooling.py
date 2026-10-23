"""AT-M0-T11-02 — Vitest and Playwright JUnit AT title parsing via real tool runs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.reports import parse_junit

VITEST_JUNIT = REPO_ROOT / "tests" / "reports" / "frontend" / "junit-vitest.xml"
PLAYWRIGHT_JUNIT = REPO_ROOT / "tests" / "reports" / "harness" / "e2e" / "junit-playwright-at02.xml"
HARNESS_PW = Path(__file__).resolve().parent / "fixtures" / "playwright"
VITEST_TEST = REPO_ROOT / "tests" / "tooling" / "harness" / "at_title.vitest.test.ts"


@pytest.mark.trace("AT-M0-T11-02", reqs=["ARCH-R083", "ARCH-R102"])
def test_vitest_and_playwright_junit_carry_at_ids() -> None:
    PLAYWRIGHT_JUNIT.parent.mkdir(parents=True, exist_ok=True)
    VITEST_JUNIT.parent.mkdir(parents=True, exist_ok=True)

    vitest = subprocess.run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "--config",
            str(REPO_ROOT / "apps/web/vitest.config.ts"),
            str(VITEST_TEST),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert vitest.returncode == 0, vitest.stdout + vitest.stderr

    playwright = subprocess.run(
        [
            "pnpm",
            "exec",
            "playwright",
            "test",
            "--config",
            str(HARNESS_PW / "playwright.config.ts"),
            "at_title_junit.spec.ts",
            "--project=desktop",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert playwright.returncode == 0, playwright.stdout + playwright.stderr

    _, vitest_cases = parse_junit(VITEST_JUNIT)
    assert any(c.at_id == "AT-M0-T11-02" for c in vitest_cases)

    _, pw_cases = parse_junit(PLAYWRIGHT_JUNIT)
    assert any(c.at_id == "AT-M0-T11-02" for c in pw_cases)
