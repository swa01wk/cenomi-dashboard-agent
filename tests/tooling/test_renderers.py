"""Renderer drift checks (M0-T10, AT-M0-T10-03)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts.docs.render_engineering_tables import check_drift as engineering_drift
from scripts.docs.render_register import check_drift as register_drift

REPO = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.trace("AT-M0-T10-03", reqs=["DEVENV-R011", "DREG-R002"])


def test_engineering_tables_match_committed() -> None:
    assert engineering_drift(REPO) == []


def test_decision_register_section2_matches_committed() -> None:
    assert register_drift(REPO) == []


def test_register_negative_bad_status_now(tmp_path: Path) -> None:
    shutil.copytree(REPO / "docs", tmp_path / "docs")
    reg = tmp_path / "docs/design/DECISION_REGISTER.md"
    text = reg.read_text(encoding="utf-8")
    reg.write_text(
        text.replace(
            "| DR-004 |",
            "| DR-004 |",
        ).replace(
            "Decision required | Approved · ready | Batch approval. All designs",
            "Decision required | Decision required | Batch approval. All designs",
            1,
        ),
        encoding="utf-8",
    )
    errors = register_drift(tmp_path)
    assert any("DR-004" in e or "status (now)" in e for e in errors)


def test_register_negative_note_prefix(tmp_path: Path) -> None:
    shutil.copytree(REPO / "docs", tmp_path / "docs")
    reg = tmp_path / "docs/design/DECISION_REGISTER.md"
    text = reg.read_text(encoding="utf-8")
    reg.write_text(text.replace("Batch approval. All designs", "Wrong prefix.", 1))
    errors = register_drift(tmp_path)
    assert errors
