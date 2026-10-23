"""Render DECISION_REGISTER §2 from the frozen export (M0-T10)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.docs.register_overrides import NOTE_OVERRIDES, STATUS_NOW

REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_EXPORT = REPO_ROOT / "docs/reference/final-design-gate/03_DECISION_REGISTER.md"
DECISION_REGISTER = REPO_ROOT / "docs/design/DECISION_REGISTER.md"


def _parse_export_table(text: str) -> list[list[str]]:
    idx = text.index("| ID |")
    lines = text[idx:].splitlines()
    rows: list[list[str]] = []
    for line in lines:
        if not line.startswith("|"):
            break
        if line.startswith("| ---"):
            continue
        if line.startswith("| ID |"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        rows.append(parts)
    return rows


def render_section2() -> str:
    export_rows = _parse_export_table(FROZEN_EXPORT.read_text(encoding="utf-8"))
    header = (
        "| ID | Decision | Rule | Origin | Status (pre-gate) | Status (now) | Note |"
    )
    sep = "| --- | --- | --- | --- | --- | --- | --- |"
    lines = [header, sep]
    for row in export_rows:
        id_, decision, rule, origin, gd_status, note = row
        pre_gate = gd_status
        now = STATUS_NOW.get(id_, gd_status)
        note_text = NOTE_OVERRIDES.get(id_, note)
        lines.append(
            "| "
            + f"{id_} | {decision} | {rule} | {origin} | {pre_gate} | {now} | {note_text}"
            + " |"
        )
    return "\n".join(lines) + "\n"


def extract_section2(doc: str) -> str:
    start = doc.index("## 2. Register")
    section = doc[start:]
    idx = section.index("| ID |")
    lines = section[idx:].splitlines()
    out: list[str] = []
    for line in lines:
        if not line.startswith("|"):
            break
        out.append(line)
    return "\n".join(out) + "\n"


def check_drift() -> list[str]:
    doc = DECISION_REGISTER.read_text(encoding="utf-8")
    rendered = render_section2()
    committed = extract_section2(doc)
    if rendered != committed:
        return [
            (
                f"{DECISION_REGISTER}: §2 register table drift "
                f"(committed {len(committed)} bytes, rendered {len(rendered)} bytes)"
            )
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = check_drift()
        for err in errors:
            print(err, file=sys.stderr)
        return 1 if errors else 0
    print(render_section2(), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
