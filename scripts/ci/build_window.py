"""M0 build-window checks for ci/summary live AT (ARCH-R103, HC-7)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.ci.target_owners import m0_cards_in_table, target_to_card
from scripts.make.report import milestone_index, read_active_milestone
from scripts.trace.report import build_report

ARCH_RESULTS = frozenset(
    {"PASSED", "FAILED", "SKIPPED", "NOT_APPLICABLE", "NOT_IMPLEMENTED"}
)

PLAN = Path(__file__).resolve().parents[2] / "plans/M0_FOUNDATION.md"
SPEC_SET = Path(__file__).resolve().parents[2] / "specs/engineering/spec_set.yaml"


def card_non_manual_all_passed(
    repo: Path, junit_paths: list[Path], card_id: str
) -> bool:
    payload, _errors, code = build_report(repo, junit_paths=junit_paths, card=card_id)
    if code != 0:
        return False
    tests = payload.get("acceptanceTests")
    if not isinstance(tests, list):
        return False
    for row in tests:
        if not isinstance(row, dict) or row.get("manual"):
            continue
        if row.get("result") != "PASSED":
            return False
    return True


def implemented_m0_cards(
    repo: Path, *, junit_paths: list[Path], pr_card: str | None
) -> set[str]:
    table_cards = m0_cards_in_table(PLAN)
    out: set[str] = set()
    for card in table_cards:
        if (pr_card and card == pr_card) or card_non_manual_all_passed(
            repo, junit_paths, card
        ):
            out.add(card)
    return out


def assert_build_window_targets(
    *,
    repo: Path,
    status_records: list[dict[str, Any]],
    junit_paths: list[Path],
    pr_card: str | None,
    make_targets: list[dict[str, str]],
) -> list[str]:
    """Return human-readable assertion failures (empty if ok)."""
    errors: list[str] = []
    active = read_active_milestone(SPEC_SET)
    active_idx = milestone_index(active)
    implemented = implemented_m0_cards(repo, junit_paths=junit_paths, pr_card=pr_card)
    owner_map = target_to_card(PLAN)
    m0_cards = m0_cards_in_table(PLAN)

    last_by_item: dict[str, dict[str, Any]] = {}
    for rec in status_records:
        if rec.get("kind") != "target":
            continue
        item = str(rec.get("item", ""))
        if item:
            last_by_item[item] = rec

    for rec in last_by_item.values():
        result = str(rec.get("result", ""))
        if result not in ARCH_RESULTS:
            errors.append(f"{rec.get('item')}: invalid result {result!r}")

    for row in make_targets:
        name = row["name"]
        active_from = row["active_from"]
        record = last_by_item.get(name)
        if record is None:
            continue
        result = str(record.get("result", ""))

        from_idx = milestone_index(active_from)
        if from_idx > active_idx:
            if result != "NOT_APPLICABLE":
                errors.append(
                    f"{name}: expected NOT_APPLICABLE (active_from {active_from}), got {result}"
                )
            continue

        owner = owner_map.get(name)
        if owner is None:
            continue

        if active_from.startswith("M0"):
            if owner in implemented:
                if result == "NOT_IMPLEMENTED":
                    errors.append(
                        f"{name}: owner {owner} implemented but result NOT_IMPLEMENTED"
                    )
            elif owner in m0_cards and result != "NOT_IMPLEMENTED":
                errors.append(
                    f"{name}: owner {owner} not implemented; expected NOT_IMPLEMENTED, got {result}"
                )

    return errors
