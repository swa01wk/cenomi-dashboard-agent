"""Build requirement → test trace reports (M0-T10, ARCH-R095)."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS = REPO_ROOT / "tests/reports"
TRACE_DIR = REPORTS / "trace"

Result = Literal["PASSED", "FAILED", "NOT_IMPLEMENTED", "SKIPPED"]

CARD_RE = re.compile(r"^M[0-6]-T[0-9]{2}$")
GATE_RE = re.compile(r"^M[0-6]$")
AT_RE = re.compile(r"\*\*(AT-M[0-6]-T[0-9]{2}-[0-9]{2})\*\*")
CARD_HEADING = re.compile(r"^### (M[0-6]-T[0-9]{2}) —", re.MULTILINE)

JUNIT_PATHS = [
    REPORTS / "backend/junit-unit.xml",
    REPORTS / "backend/junit-integration.xml",
    REPORTS / "backend/junit-tooling.xml",
    REPORTS / "frontend/junit-vitest.xml",
    REPORTS / "e2e/junit-playwright.xml",
]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.reports import parse_junit


@dataclass(frozen=True)
class AtSpec:
    at_id: str
    card_id: str
    manual: bool


def _milestone_index(name: str) -> int:
    return int(name[1])


def _card_milestone(card_id: str) -> str:
    return card_id.split("-", 1)[0]


def _load_at_specs() -> dict[str, AtSpec]:
    specs: dict[str, AtSpec] = {}
    for plan in sorted(REPO_ROOT.glob("plans/M*_*.md")):
        text = plan.read_text(encoding="utf-8")
        for heading in CARD_HEADING.finditer(text):
            card_id = heading.group(1)
            start = heading.end()
            next_h = text.find("\n### ", start)
            block = text[start:] if next_h == -1 else text[start:next_h]
            field15 = re.search(r"^\| 15 \|[^\n]*\|([^\|]*)\|$", block, re.MULTILINE)
            if not field15:
                continue
            content = field15.group(1)
            for match in AT_RE.finditer(content):
                at_id = match.group(1)
                window = content[max(0, match.start() - 40) : match.end() + 40]
                manual = "manual" in window.lower()
                specs[at_id] = AtSpec(at_id=at_id, card_id=card_id, manual=manual)
    return specs


def _collect_junit_results() -> dict[str, Result]:
    by_at: dict[str, list[Result]] = {}
    for path in JUNIT_PATHS:
        if not path.is_file():
            continue
        try:
            _, cases = parse_junit(path)
        except (OSError, ValueError):
            continue
        for case in cases:
            if not case.at_id:
                continue
            by_at.setdefault(case.at_id, []).append(case.result)

    results: dict[str, Result] = {}
    for at_id, outcomes in by_at.items():
        if any(r == "FAILED" for r in outcomes):
            results[at_id] = "FAILED"
        elif outcomes and (
            all(r == "SKIPPED" for r in outcomes)
            or any(r == "SKIPPED" for r in outcomes)
        ):
            results[at_id] = "SKIPPED"
        else:
            results[at_id] = "PASSED"
    return results


def _validate_id(at_id: str, conventions: dict[str, str]) -> None:
    pattern = conventions.get("acceptance_test")
    if not pattern or not re.compile(pattern).fullmatch(at_id):
        raise ValueError(f"unknown or malformed AT id {at_id!r}")


def _load_conventions() -> dict[str, str]:
    data = yaml.safe_load(
        (REPO_ROOT / "specs/traceability/id_conventions.yaml").read_text(
            encoding="utf-8"
        )
    )
    return {
        entry["id"]: entry["pattern"]
        for entry in data["families"]
        if entry["id"] in {"acceptance_test", "task_card"}
    }


def _manual_results(milestone: str) -> dict[str, Result]:
    path = REPO_ROOT / "plans/gates" / f"{milestone}-manual-results.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, Result] = {}
    for item in payload.get("results", []):
        out[item["atId"]] = item["result"]
    return out


def build_report(
    *,
    card: str = "",
    gate: str = "",
) -> tuple[dict[str, object], list[str], int]:
    conventions = _load_conventions()
    at_specs = _load_at_specs()
    junit = _collect_junit_results()

    errors: list[str] = []
    exit_code = 0

    for path in JUNIT_PATHS:
        if not path.is_file():
            continue
        try:
            _, cases = parse_junit(path)
        except (OSError, ValueError):
            continue
        for case in cases:
            if case.at_id and case.at_id not in at_specs:
                msg = f"unknown AT id {case.at_id} in {path.name}"
                errors.append(msg)
                exit_code = 1

    if card and not CARD_RE.fullmatch(card):
        raise ValueError(f"unknown or malformed CARD={card!r}")
    if gate and not GATE_RE.fullmatch(gate):
        raise ValueError(f"unknown or malformed GATE={gate!r}")
    if card and card not in {s.card_id for s in at_specs.values()}:
        raise ValueError(f"unknown card {card!r}")

    scope: dict[str, AtSpec] = {}
    for at_id, spec in at_specs.items():
        _validate_id(at_id, conventions)
        if card and spec.card_id != card:
            continue
        if gate:
            card_ms = _milestone_index(_card_milestone(spec.card_id))
            if card_ms > _milestone_index(gate):
                continue
        scope[at_id] = spec

    manual_by_ms: dict[str, dict[str, Result]] = {}
    records: list[dict[str, object]] = []
    manual_list: list[dict[str, object]] = []

    for at_id, spec in sorted(scope.items()):
        if spec.manual:
            milestone = _card_milestone(spec.card_id)
            manual_by_ms.setdefault(milestone, _manual_results(milestone))
            manual_result = manual_by_ms[milestone].get(at_id)
            entry = {
                "atId": at_id,
                "cardId": spec.card_id,
                "manual": True,
                "result": manual_result or "NOT_IMPLEMENTED",
            }
            manual_list.append(entry)
            if card:
                continue
            if gate and not manual_result:
                errors.append(f"{at_id}: manual AT lacks recorded result")
                exit_code = 1
            records.append(entry)
            continue

        result: Result = junit.get(at_id, "NOT_IMPLEMENTED")
        entry = {
            "atId": at_id,
            "cardId": spec.card_id,
            "manual": False,
            "result": result,
        }
        records.append(entry)
        if card and result != "PASSED":
            errors.append(f"{at_id}: {result}")
            exit_code = 1
        if gate and result != "PASSED":
            errors.append(f"{at_id}: {result}")
            exit_code = 1

    payload: dict[str, object] = {
        "schema": "cenomi.trace_report.v1",
        "mode": "card" if card else "gate" if gate else "default",
        "card": card or None,
        "gate": gate or None,
        "acceptanceTests": records,
        "manualAcceptanceTests": manual_list,
        "errors": errors,
    }
    return payload, errors, exit_code


def _markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Trace report",
        "",
        f"- Mode: `{payload.get('mode')}`",
    ]
    if payload.get("card"):
        lines.append(f"- Card: `{payload['card']}`")
    if payload.get("gate"):
        lines.append(f"- Gate: `{payload['gate']}`")
    lines.extend(["", "| AT ID | Card | Manual | Result |", "|---|---|---|---|"])
    acceptance = payload.get("acceptanceTests")
    if not isinstance(acceptance, list):
        acceptance = []
    for row in acceptance:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('atId')}` | `{row.get('cardId')}` | "
            f"{'yes' if row.get('manual') else 'no'} | **{row.get('result')}** |"
        )
    err_list = payload.get("errors")
    if isinstance(err_list, list) and err_list:
        lines.extend(["", "## Errors", ""])
        for err in err_list:
            lines.append(f"- {err}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    card = os.environ.get("CARD", "").strip()
    gate = os.environ.get("GATE", "").strip()
    try:
        payload, errors, exit_code = build_report(card=card, gate=gate)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    (TRACE_DIR / "trace.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    (TRACE_DIR / "trace.md").write_text(_markdown(payload), encoding="utf-8")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
    if exit_code == 0:
        tests = payload.get("acceptanceTests")
        count = len(tests) if isinstance(tests, list) else 0
        print(f"PASSED: trace-report — {count} AT(s) in scope")
    else:
        print("FAILED: trace-report — one or more ATs not PASSED", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
