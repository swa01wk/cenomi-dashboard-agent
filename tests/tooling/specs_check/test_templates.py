"""GitHub template tests (M0-T10, AT-M0-T10-05)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]

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


def _devenv_pr_section_names() -> list[str]:
    text = (REPO / "docs/architecture/DEVELOPMENT_ENVIRONMENT.md").read_text(
        encoding="utf-8"
    )
    block = text.split("**DEVENV-R035**", 1)[1].split("### 8.3", 1)[0]
    names: list[str] = []
    for line in block.splitlines():
        match = re.match(r"^\|\s*\d+\s*\|\s*(.+?)\s*\|", line)
        if not match:
            continue
        cell = match.group(1).strip()
        names.append(re.split(r"\s*\(", cell, maxsplit=1)[0].strip())
    return names


@pytest.mark.trace("AT-M0-T10-05", reqs=["DEVENV-R035", "DEVENV-R046"])
def test_pr_template_has_fifteen_sections() -> None:
    expected = _devenv_pr_section_names()
    assert len(expected) == 15
    text = (REPO / ".github/pull_request_template.md").read_text(encoding="utf-8")
    headings = [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]
    assert headings == expected
    assert "DEVENV-R035" in text
    for heading in headings:
        assert f"<!-- DEVENV-R035" in text


@pytest.mark.trace("AT-M0-T10-05", reqs=["DEVENV-R046"])
def test_defect_template_nine_triage_classes() -> None:
    data = yaml.safe_load(
        (REPO / ".github/ISSUE_TEMPLATE/defect.yml").read_text(encoding="utf-8")
    )
    options = None
    blocking_type = None
    for field in data["body"]:
        if field.get("id") == "triage_class":
            options = field["attributes"]["options"]
        if field.get("id") == "blocking":
            blocking_type = field["type"]
    assert options == TRIAGE_CLASSES
    assert blocking_type == "checkboxes"
    title = data.get("title", "")
    assert title.startswith("DEF-")
