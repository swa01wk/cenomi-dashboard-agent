"""Ensure tests/reports/status.jsonl exists after a CI job step."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.make.report import (  # type: ignore[import-not-found]
    append_status,
    read_active_milestone,
)

STATUS = REPO_ROOT / "tests/reports/status.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, help="GitHub job name, e.g. ci/static")
    parser.add_argument("--reason", default="job failed before make ci recorded status")
    args = parser.parse_args()

    if STATUS.is_file():
        return 0

    STATUS.parent.mkdir(parents=True, exist_ok=True)
    milestone = read_active_milestone()
    append_status(
        item="ci",
        result="FAILED",
        rule="ci_job",
        reason=f"{args.job}: {args.reason}",
        milestone=milestone,
        duration_ms=0,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
