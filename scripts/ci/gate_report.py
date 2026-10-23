"""Assemble milestone gate report markdown (RMAP-R010 skeleton for M0)."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--milestone", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    milestone = args.milestone.strip().upper()
    out_dir = args.output.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    body = "\n".join(
        [
            f"# Milestone gate report — {milestone}",
            "",
            f"- Merged commit: `{args.sha}`",
            f"- Generated: {datetime.now(tz=UTC).isoformat()}",
            "",
            "See `tests/reports/gate/` artefacts and workflow logs for full evidence.",
            "",
        ]
    )
    args.output.write_text(body, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
