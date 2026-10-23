"""Renderer drift checks (M0-T10, AT-M0-T10-03)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts.docs.render_engineering_tables import check_drift as engineering_drift
from scripts.docs.render_register import check_drift as register_drift

REPO = Path(__file__).resolve().parents[2]
REGISTER = "docs/design/DECISION_REGISTER.md"

pytestmark = pytest.mark.trace("AT-M0-T10-03", reqs=["DEVENV-R011", "DREG-R002"])


def _copy_docs(tmp_path: Path) -> Path:
    shutil.copytree(REPO / "docs", tmp_path / "docs")
    return tmp_path / REGISTER


def test_engineering_tables_match_committed() -> None:
    assert engineering_drift(REPO) == []


def test_decision_register_section2_matches_committed() -> None:
    assert register_drift(REPO) == []


def test_register_negative_bad_status_now(tmp_path: Path) -> None:
    reg = _copy_docs(tmp_path)
    text = reg.read_text(encoding="utf-8")
    reg.write_text(
        text.replace(
            "Decision required | Approved · ready | Batch approval. All designs",
            "Decision required | Decision required | Batch approval. All designs",
            1,
        ),
        encoding="utf-8",
    )
    errors = register_drift(tmp_path)
    assert any(
        "§2 row 4 (DR-004) status (now)" in e and "!= expected" in e for e in errors
    )


def test_register_negative_note_prefix(tmp_path: Path) -> None:
    reg = _copy_docs(tmp_path)
    text = reg.read_text(encoding="utf-8")
    reg.write_text(text.replace("Batch approval. All designs", "Wrong prefix.", 1))
    errors = register_drift(tmp_path)
    assert any(
        "§2 row 4 (DR-004) note does not start with export text" in e for e in errors
    )


def test_register_negative_id_out_of_order(tmp_path: Path) -> None:
    reg = _copy_docs(tmp_path)
    text = reg.read_text(encoding="utf-8")
    reg.write_text(
        text.replace(
            "| DR-004 | as\\_of value",
            "| DR-005 | as\\_of value",
            1,
        ),
        encoding="utf-8",
    )
    errors = register_drift(tmp_path)
    assert any("§2 row 4 (DR-004) id 'DR-005' != export" in e for e in errors)


def test_register_negative_decision_column(tmp_path: Path) -> None:
    reg = _copy_docs(tmp_path)
    text = reg.read_text(encoding="utf-8")
    reg.write_text(
        text.replace(
            "| DR-001 | Parity policy |",
            "| DR-001 | Parity policy CHANGED |",
            1,
        ),
        encoding="utf-8",
    )
    errors = register_drift(tmp_path)
    assert any(
        "§2 row 1 (DR-001) column decision differs from export" in e for e in errors
    )


def test_register_negative_amended_note_without_authority(tmp_path: Path) -> None:
    from scripts.docs.render_register import _parse_export_table

    export_rows = _parse_export_table(
        (REPO / "docs/reference/final-design-gate/03_DECISION_REGISTER.md").read_text(
            encoding="utf-8"
        )
    )
    target = next(r for r in export_rows if r["id"] == "DR-018b")
    export_note = target["note_export"]
    reg = _copy_docs(tmp_path)
    text = reg.read_text(encoding="utf-8")
    bad_note = f"{export_note} Additional text without a gate reference."
    old_line = (
        "| DR-018b | No approvals filter-list snapshot table | Filter options from live data. "
        "| G0 · proposed (M0) | Decision required | Approved · ready | "
        "Batch approval. GDQ-10 A (22 Oct 2026); final definition in §4. |"
    )
    new_line = (
        "| DR-018b | No approvals filter-list snapshot table | Filter options from live data. "
        "| G0 · proposed (M0) | Decision required | Approved · ready | "
        f"{bad_note} |"
    )
    reg.write_text(text.replace(old_line, new_line, 1), encoding="utf-8")
    errors = register_drift(tmp_path)
    row_no = export_rows.index(target) + 1
    assert any(
        f"§2 row {row_no} (DR-018b) amended note missing authority (GDQ, ADR, CR, ED)"
        in e
        for e in errors
    )
