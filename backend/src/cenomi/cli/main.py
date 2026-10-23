"""Cenomi CLI entrypoint (ARCH-R034)."""

from __future__ import annotations

import argparse
import sys


def _cmd_db_verify_roles(_args: argparse.Namespace) -> int:
    print(
        "cenomi db verify-roles is implemented in M0-T02 (database roles and grants).",
        file=sys.stderr,
    )
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cenomi", description="Cenomi Dashboard Intelligence Agent CLI"
    )
    sub = parser.add_subparsers(dest="command", required=False)

    db = sub.add_parser("db", help="Database administration commands")
    db_sub = db.add_subparsers(dest="db_command", required=False)
    db_sub.add_parser("verify-roles", help="Verify PostgreSQL roles and grants (M0-T02)")

    seed = sub.add_parser("seed", help="Synthetic dataset commands (from M1)")
    seed_sub = seed.add_subparsers(dest="seed_command", required=False)
    seed_sub.add_parser("run")
    seed_sub.add_parser("verify")
    seed_sub.add_parser("hash")

    sub.add_parser("insights", help="Insight replay (M6)")
    sub.add_parser("eval", help="Evaluation harness (M5)")

    args = parser.parse_args(argv)
    if args.command == "db" and args.db_command == "verify-roles":
        return _cmd_db_verify_roles(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
