"""Run Playwright harness specs when make e2e is still a stub (HC-12, ARCH-R103)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.make.report import (
    STATUS_PATH,
    ensure_reports_dir,
    read_active_milestone,
)

SPEC_SET = REPO_ROOT / "specs/engineering/spec_set.yaml"
HARNESS_ITEM = "e2e-harness"
PLAYWRIGHT_ARGS = ["pnpm", "exec", "playwright", "test", "tests/e2e/support"]


def read_status_records() -> list[dict[str, Any]]:
    if not STATUS_PATH.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in STATUS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def last_e2e_target_result(records: list[dict[str, Any]]) -> str | None:
    last: str | None = None
    for rec in records:
        if rec.get("kind") == "target" and rec.get("item") == "e2e":
            last = str(rec.get("result", ""))
    return last


def append_step_record(*, result: str, milestone: str, reason: str) -> None:
    ensure_reports_dir()
    record = {
        "item": HARNESS_ITEM,
        "kind": "step",
        "result": result,
        "milestone": milestone,
        "reason": reason,
    }
    with STATUS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def run_playwright_harness() -> bool:
    cmd = PLAYWRIGHT_ARGS
    print("+ " + " ".join(cmd), flush=True)
    completed = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
    return completed.returncode == 0


def main() -> int:
    records = read_status_records()
    e2e_result = last_e2e_target_result(records)
    if e2e_result != "NOT_IMPLEMENTED":
        return 0

    active = read_active_milestone(SPEC_SET)
    ok = run_playwright_harness()
    if ok:
        append_step_record(
            result="PASSED",
            milestone=active,
            reason="playwright harness specs in tests/e2e/support",
        )
        return 0
    append_step_record(
        result="FAILED",
        milestone=active,
        reason="playwright harness specs failed",
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
