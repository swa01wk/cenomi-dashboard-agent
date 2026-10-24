"""Cenomi CLI entrypoint (ARCH-R034)."""

from __future__ import annotations

import argparse

from cenomi.cli import db as db_commands


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cenomi", description="Cenomi Dashboard Intelligence Agent CLI"
    )
    subparsers = parser.add_subparsers(dest="command")
    db_commands.register_subcommands(subparsers)

    args = parser.parse_args(argv)
    if args.command == "db":
        handler = getattr(args, "handler", None)
        if handler is None:
            parser.print_help()
            return 2
        return int(handler(args))
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
