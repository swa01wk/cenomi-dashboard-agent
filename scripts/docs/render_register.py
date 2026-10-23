"""Consistency-check DECISION_REGISTER §2 against the frozen export (M0-T10, HC-10)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

APPROVED_READY = "Approved · ready"
SUPERSEDED = "Superseded"

AUTHORITY_IN_NOTE = re.compile(r"(GDQ-[0-9]{2}|ADR-[0-9]{4}|CR-[0-9]{3}|ED-[0-9]{2})")


def _parse_export_table(text: str) -> list[dict[str, str]]:
    idx = text.index("| ID |")
    lines = text[idx:].splitlines()
    rows: list[dict[str, str]] = []
    for line in lines:
        if not line.startswith("|"):
            break
        if line.startswith(("| ---", "| ID |")):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 6:
            continue
        id_, decision, rule, origin, status, note = parts[:6]
        rows.append(
            {
                "id": id_,
                "decision": decision,
                "rule": rule,
                "origin": origin,
                "status_pre_gate": status,
                "note_export": note,
            }
        )
    return rows


def _parse_section2_table(text: str) -> list[dict[str, str]]:
    start = text.index("## 2. Register")
    section = text[start:]
    idx = section.index("| ID |")
    lines = section[idx:].splitlines()
    rows: list[dict[str, str]] = []
    for line in lines:
        if not line.startswith("|"):
            break
        if line.startswith(("| ---", "| ID |")):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 7:
            continue
        rows.append(
            {
                "id": parts[0],
                "decision": parts[1],
                "rule": parts[2],
                "origin": parts[3],
                "status_pre_gate": parts[4],
                "status_now": parts[5],
                "note": parts[6],
            }
        )
    return rows


def _parse_section1_status_overrides(section1: str) -> dict[str, str]:
    """Derive Status (now) overrides from §1 narrative (HC-10)."""
    overrides: dict[str, str] = {}

    batch = re.search(
        r"GDQ-10 batch \(\d+\):\s*([^.]+)\.",
        section1,
    )
    if batch:
        for token in batch.group(1).split(","):
            id_ = token.strip()
            if id_:
                overrides[id_] = APPROVED_READY

    for match in re.finditer(r"GDQ-(05|12|11|03):\s*([^.;]+)", section1):
        segment = match.group(2)
        for id_ in re.findall(r"\b(DR-[0-9]{3}b?|DXD-[0-9]{2})\b", segment):
            overrides[id_] = APPROVED_READY

    if re.search(r"ADR-0001.*DR-035.*Superseded", section1, re.DOTALL):
        overrides["DR-035"] = SUPERSEDED

    return overrides


def _expected_status_now(
    export_status: str, overrides: dict[str, str], id_: str
) -> str:
    return overrides.get(id_, export_status)


def _note_ok(export_note: str, committed_note: str) -> tuple[bool, str]:
    if committed_note == export_note:
        return True, ""
    if not committed_note.startswith(export_note):
        return False, "note does not start with export text"
    if not AUTHORITY_IN_NOTE.search(committed_note):
        return False, "amended note missing authority (GDQ, ADR, CR, ED)"
    return True, ""


def check_drift(repo: Path) -> list[str]:
    register = repo / "docs/design/DECISION_REGISTER.md"
    export_path = repo / "docs/reference/final-design-gate/03_DECISION_REGISTER.md"
    errors: list[str] = []
    if not register.is_file():
        return [f"{register}: missing DECISION_REGISTER.md"]
    if not export_path.is_file():
        return [f"{export_path}: missing frozen export"]

    register_text = register.read_text(encoding="utf-8")
    export_rows = _parse_export_table(export_path.read_text(encoding="utf-8"))
    committed_rows = _parse_section2_table(register_text)

    section1_start = register_text.index("## 1. Status after")
    section1 = register_text[section1_start : register_text.index("## 2. Register")]
    status_overrides = _parse_section1_status_overrides(section1)

    if len(committed_rows) != len(export_rows):
        errors.append(
            f"{register}: §2 row count {len(committed_rows)} != export {len(export_rows)}"
        )

    for index, (export, committed) in enumerate(
        zip(export_rows, committed_rows, strict=False)
    ):
        row_ref = f"§2 row {index + 1} ({export['id']})"
        if committed["id"] != export["id"]:
            errors.append(f"{register}: {row_ref} id {committed['id']!r} != export")
            continue
        for col in ("decision", "rule", "origin", "status_pre_gate"):
            if committed[col] != export[col]:
                errors.append(f"{register}: {row_ref} column {col} differs from export")
        expected_now = _expected_status_now(
            export["status_pre_gate"], status_overrides, export["id"]
        )
        if committed["status_now"] != expected_now:
            errors.append(
                f"{register}: {row_ref} status (now) {committed['status_now']!r} "
                f"!= expected {expected_now!r} from §1"
            )
        ok, reason = _note_ok(export["note_export"], committed["note"])
        if not ok:
            errors.append(f"{register}: {row_ref} {reason}")

    if len(committed_rows) > len(export_rows):
        for extra in committed_rows[len(export_rows) :]:
            errors.append(f"{register}: extra §2 row {extra['id']!r}")

    return errors


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = check_drift(repo)
        for err in errors:
            print(err, file=sys.stderr)
        return 1 if errors else 0
    print(
        "render_register: §2 is maintained in DECISION_REGISTER.md (consistency check only)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
