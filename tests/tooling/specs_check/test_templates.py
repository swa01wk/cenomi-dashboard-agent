"""GitHub template tests (M0-T10, AT-M0-T10-05)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]

PR_SECTIONS = [
    "Feature ID and title",
    "Requirement and specification references",
    "Scope of changes",
    "Implementation summary",
    "Files and modules affected",
    "Acceptance criteria",
    "Tests added or updated",
    "Local validation",
    "CI results",
    "Screenshots for UI changes",
    "API, schema and migration impact",
    "Security considerations",
    "Known limitations and deferred items",
    "Rollback and recovery notes",
    "Dependencies on other PRs",
]

TRIAGE_CLASSES = [
    "triage:test-failure",
    "triage:contract-mismatch",
    "triage:kpi-discrepancy",
    "triage:authorization",
    "triage:grounding",
    "triage:ui-rendering",
    "triage:ci-infrastructure",
    "triage:live-model-variability",
    "triage:flaky",
]


@pytest.mark.trace("AT-M0-T10-05", reqs=["DEVENV-R035", "DEVENV-R046"])
def test_pr_template_has_fifteen_sections() -> None:
    text = (REPO / ".github/pull_request_template.md").read_text(encoding="utf-8")
    headings = [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]
    assert headings == PR_SECTIONS


@pytest.mark.trace("AT-M0-T10-05", reqs=["DEVENV-R046"])
def test_defect_template_nine_triage_classes() -> None:
    data = yaml.safe_load(
        (REPO / ".github/ISSUE_TEMPLATE/defect.yml").read_text(encoding="utf-8")
    )
    options = None
    for field in data["body"]:
        if field.get("id") == "triage_class":
            options = field["attributes"]["options"]
            break
    assert options == TRIAGE_CLASSES
    title = data.get("title", "")
    assert title.startswith("DEF-")
