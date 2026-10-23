"""Unit tests for HC-7 target owner table parser."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.target_owners import TargetOwnerError, parse_owner_table

PLAN = REPO_ROOT / "plans/M0_FOUNDATION.md"


def test_parse_owner_table_covers_m0_t07_ci() -> None:
    owners = parse_owner_table(PLAN)
    assert owners["M0-T07"] == ["ci"]
    assert "backend-test" in owners["M0-T03"]
    assert "specs-check" in owners["M0-T10"]
    assert "SUITE=tooling" not in str(owners)


def test_duplicate_target_in_table_raises(tmp_path: Path) -> None:
    text = (
        "**Make target owners (HC-7, test).**\n\n"
        "| Card | Targets |\n|---|---|\n"
        "| M0-T01 | `help`, `doctor` |\n"
        "| M0-T02 | `help`, `up` |\n"
    )
    path = tmp_path / "plan.md"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(TargetOwnerError, match="owned by both"):
        parse_owner_table(path)


def test_missing_section_raises(tmp_path: Path) -> None:
    path = tmp_path / "plan.md"
    path.write_text("# no table\n", encoding="utf-8")
    with pytest.raises(TargetOwnerError, match="not found"):
        parse_owner_table(path)
