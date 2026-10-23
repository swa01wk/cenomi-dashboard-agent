"""Append Make target results to tests/reports/status.jsonl (ARCH-R102)."""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC_SET = REPO_ROOT / "specs/engineering/spec_set.yaml"
STATUS_PATH = REPO_ROOT / "tests/reports/status.jsonl"


def milestone_index(code: str) -> int:
    match = re.fullmatch(r"M(\d+)", code.strip())
    if not match:
        raise ValueError(f"Invalid milestone code: {code!r}")
    return int(match.group(1))


def read_active_milestone(spec_set_path: Path | None = None) -> str:
    path = spec_set_path or Path(os.environ.get("CENOMI_SPEC_SET", DEFAULT_SPEC_SET))
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^active_milestone:\s*(M\d+)\b", text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"active_milestone not found in {path}")
    return match.group(1)


def ensure_reports_dir() -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)


def append_status(
    *,
    item: str,
    result: str,
    rule: str,
    reason: str,
    milestone: str,
    duration_ms: int,
) -> None:
    ensure_reports_dir()
    record = {
        "item": item,
        "kind": "target",
        "result": result,
        "rule": rule,
        "reason": reason,
        "milestone": milestone,
        "durationMs": duration_ms,
    }
    with STATUS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def emit_result(target: str, result: str, reason: str) -> None:
    if result == "NOT_APPLICABLE":
        print(f"NOT_APPLICABLE: {target} {reason}", flush=True)
    else:
        print(f"{result}: {target} — {reason}", flush=True)


class TargetRun:
    def __init__(self, target: str) -> None:
        self.target = target
        self._start = time.monotonic()

    def finish(self, result: str, rule: str, reason: str, exit_code: int) -> None:
        duration_ms = int((time.monotonic() - self._start) * 1000)
        milestone = read_active_milestone()
        append_status(
            item=self.target,
            result=result,
            rule=rule,
            reason=reason,
            milestone=milestone,
            duration_ms=duration_ms,
        )
        emit_result(self.target, result, reason)
        sys.exit(exit_code)


def not_applicable(target: str, active_from: str, reason: str, run: TargetRun) -> None:
    line_reason = f"becomes active in {active_from} — {reason}"
    run.finish("NOT_APPLICABLE", "milestone", line_reason, 0)


def not_implemented(
    target: str, reason: str, run: TargetRun, *, active_from: str
) -> None:
    active = read_active_milestone()
    gate = os.environ.get("GATE", "").strip()
    in_window = milestone_index(active_from) == milestone_index(active)
    if gate:
        gate_idx = milestone_index(gate)
        if milestone_index(active_from) <= gate_idx:
            run.finish("NOT_IMPLEMENTED", "build_window", reason, 1)
            return
    if in_window:
        run.finish("NOT_IMPLEMENTED", "build_window", reason, 0)
        return
    run.finish("NOT_IMPLEMENTED", "build_window", reason, 1)


def passed(target: str, reason: str, run: TargetRun) -> None:
    run.finish("PASSED", "", reason, 0)


def failed(target: str, reason: str, run: TargetRun, exit_code: int = 1) -> None:
    run.finish("FAILED", "", reason, exit_code)
