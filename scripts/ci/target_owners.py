"""Parse M0 Make target owners (HC-7) from plans/M0_FOUNDATION.md §3."""

from __future__ import annotations

import re
from pathlib import Path

OWNER_SECTION = re.compile(
    r"\*\*Make target owners \(HC-7[^\n]*\*\*[^\n]*\n\n(\| Card \| Targets \|\n\|---\|---\|\n(?:\|[^\n]+\n)+)",
    re.MULTILINE,
)
ROW = re.compile(
    r"^\|\s*(M0-T\d{2})\s*\|\s*(.+?)\s*\|\s*$",
    re.MULTILINE,
)
TARGET = re.compile(r"`([^`]+)`")


class TargetOwnerError(ValueError):
    pass


def parse_owner_table(plan_path: Path) -> dict[str, list[str]]:
    """Return card id -> ordered target names from the HC-7 table."""
    if not plan_path.is_file():
        raise TargetOwnerError(f"missing plan file: {plan_path}")
    text = plan_path.read_text(encoding="utf-8")
    match = OWNER_SECTION.search(text)
    if not match:
        raise TargetOwnerError("Make target owners (HC-7) table not found in plan")
    block = match.group(1)
    owners: dict[str, list[str]] = {}
    seen_target: dict[str, str] = {}
    for row in ROW.finditer(block):
        card = row.group(1)
        cell = row.group(2)
        if ";" in cell:
            cell = cell.split(";", 1)[0]
        targets = TARGET.findall(cell)
        if not targets:
            raise TargetOwnerError(f"card {card} has no targets in owner table")
        if card in owners:
            raise TargetOwnerError(f"duplicate card row in owner table: {card}")
        owners[card] = targets
        for target in targets:
            if target in seen_target:
                raise TargetOwnerError(
                    f"target {target!r} owned by both {seen_target[target]} and {card}"
                )
            seen_target[target] = card
    if not owners:
        raise TargetOwnerError("owner table is empty")
    return owners


def target_to_card(plan_path: Path) -> dict[str, str]:
    owners = parse_owner_table(plan_path)
    return {target: card for card, targets in owners.items() for target in targets}


def m0_cards_in_table(plan_path: Path) -> frozenset[str]:
    return frozenset(parse_owner_table(plan_path).keys())
