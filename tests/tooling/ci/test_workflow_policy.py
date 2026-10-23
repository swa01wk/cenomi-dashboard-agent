"""AT-M0-T07-01, AT-M0-T07-05, AT-M0-T07-06, AT-M0-T07-08 — workflow policy."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CI_CHECKS = REPO_ROOT / "specs/engineering/ci_checks.yaml"
CI_YML = REPO_ROOT / ".github/workflows/ci.yml"
EVAL_LIVE = REPO_ROOT / ".github/workflows/eval-live.yml"
CHECK_BRANCH = REPO_ROOT / "scripts/ci/check_branch_name.py"
EVAL_GUARD = REPO_ROOT / "scripts/ci/eval_live_guard.py"

SHA_PIN = re.compile(r"@[0-9a-f]{40}\b")


def _workflow_job_names(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    jobs = data.get("jobs", {})
    names: list[str] = []
    for job in jobs.values():
        if isinstance(job, dict) and "name" in job:
            names.append(job["name"])
    return names


def _expected_ci_job_names() -> list[str]:
    ci = yaml.safe_load(CI_CHECKS.read_text(encoding="utf-8"))
    return [j["name"] for j in ci["jobs"]]


@pytest.mark.trace("AT-M0-T07-01", reqs=["DEVENV-R028"])
def test_workflow_job_names_match_ci_checks() -> None:
    expected = set(_expected_ci_job_names())
    actual = set(_workflow_job_names(CI_YML))
    assert expected == actual


@pytest.mark.trace("AT-M0-T07-05", reqs=["DEVENV-R027", "ADR-0017"])
def test_ci_yml_policy_lint() -> None:
    text = CI_YML.read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    assert data.get("permissions") == {"contents": "read"}
    assert "pull_request_target" not in text
    assert "pull_request:" in text
    assert "${{ secrets." not in text

    for line in text.splitlines():
        stripped = line.strip()
        if (
            "uses:" in line
            and "./.github/" not in line
            and "pip install" not in line
            and stripped.startswith(("- uses:", "uses:"))
        ):
            assert SHA_PIN.search(line), f"unpinned action: {stripped}"

    assert "LLM_MODE: replay" in text


@pytest.mark.trace("AT-M0-T07-05", reqs=["DEVENV-R032"])
def test_check_branch_name_accepts_and_rejects() -> None:
    ok = subprocess.run(
        [sys.executable, str(CHECK_BRANCH), "feat/m0-t03-backend-skeleton"],
        cwd=REPO_ROOT,
        check=False,
    )
    assert ok.returncode == 0
    bad = subprocess.run(
        [sys.executable, str(CHECK_BRANCH), "feature/foo"],
        cwd=REPO_ROOT,
        check=False,
    )
    assert bad.returncode != 0
    docs = subprocess.run(
        [sys.executable, str(CHECK_BRANCH), "docs/m0-foundation-specs"],
        cwd=REPO_ROOT,
        check=False,
    )
    assert docs.returncode == 0


@pytest.mark.trace("AT-M0-T07-06", reqs=["ED-05"])
def test_ci_images_builds_without_push_or_login() -> None:
    text = CI_YML.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    images = data["jobs"]["images"]
    steps_yaml = yaml.dump(images["steps"])
    assert "docker buildx build" in steps_yaml
    assert "docker/login-action" not in steps_yaml
    assert "push: true" not in steps_yaml
    assert "docker push" not in steps_yaml


@pytest.mark.trace("AT-M0-T07-08", reqs=["ARCH-R089", "ADR-0017"])
def test_eval_live_guard_refuses_missing_environment_or_budgets() -> None:
    base = [
        sys.executable,
        str(EVAL_GUARD),
        "--repository",
        "swa01wk/cenomi-dashboard-agent",
        "--ref-type",
        "branch",
        "--set",
        "slice",
        "--max-cases",
        "1",
        "--max-tokens",
        "100",
        "--max-cost-usd",
        "1",
    ]
    missing_budget = subprocess.run(
        base[:-2] + ["--max-tokens", "100", "--max-cost-usd", ""],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing_budget.returncode != 0

    missing_env = subprocess.run(
        base + ["--require-environment", "--environment", ""],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing_env.returncode != 0

    assert "live-eval" in EVAL_LIVE.read_text(encoding="utf-8")
