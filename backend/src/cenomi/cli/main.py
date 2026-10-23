"""Cenomi CLI entrypoint (ARCH-R034)."""

from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cenomi", description="Cenomi Dashboard Intelligence Agent CLI"
    )
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
