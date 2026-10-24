"""Refuse eval-live.yml when guards or budget inputs are missing (AT-M0-T07-08)."""

from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--ref-type", default=os.environ.get("GITHUB_REF_TYPE", ""))
    parser.add_argument(
        "--environment", default=os.environ.get("GITHUB_ENVIRONMENT", "")
    )
    parser.add_argument(
        "--require-environment",
        action="store_true",
        help="When set, live-eval environment must be active",
    )
    parser.add_argument(
        "--set", dest="eval_set", default=os.environ.get("INPUT_SET", "")
    )
    parser.add_argument(
        "--max-cases",
        default=os.environ.get(
            "INPUT_MAX_CASES", os.environ.get("LIVE_EVAL_MAX_CASES", "")
        ),
    )
    parser.add_argument(
        "--max-tokens",
        default=os.environ.get(
            "INPUT_MAX_TOKENS", os.environ.get("LIVE_EVAL_MAX_TOKENS", "")
        ),
    )
    parser.add_argument(
        "--max-cost-usd",
        default=os.environ.get(
            "INPUT_MAX_COST_USD", os.environ.get("LIVE_EVAL_MAX_COST_USD", "")
        ),
    )
    args = parser.parse_args()

    allowed_repo = "swa01wk/cenomi-dashboard-agent"
    if args.repository != allowed_repo:
        print(f"refused: repository must be {allowed_repo}", file=sys.stderr)
        return 1
    if args.ref_type not in ("branch", "tag"):
        print(
            "refused: ref must be a branch of this repository (not a fork)",
            file=sys.stderr,
        )
        return 1
    if args.require_environment and args.environment != "live-eval":
        print("refused: live-eval environment is required", file=sys.stderr)
        return 1
    if args.eval_set not in ("slice", "benchmark"):
        print("refused: set must be slice or benchmark", file=sys.stderr)
        return 1
    for name, val in (
        ("max_cases", args.max_cases),
        ("max_tokens", args.max_tokens),
        ("max_cost_usd", args.max_cost_usd),
    ):
        if not str(val).strip():
            print(f"refused: missing budget input {name}", file=sys.stderr)
            return 1
    print("eval-live guard: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
