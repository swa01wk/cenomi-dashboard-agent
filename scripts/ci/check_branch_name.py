"""Validate PR head branch names (DEVENV-R032)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ID_CONVENTIONS = REPO_ROOT / "specs/traceability/id_conventions.yaml"


def branch_pattern() -> re.Pattern[str]:
    data = yaml.safe_load(ID_CONVENTIONS.read_text(encoding="utf-8"))
    for family in data["families"]:
        if family["id"] == "branch":
            return re.compile(family["pattern"])
    raise RuntimeError("branch family not found in id_conventions.yaml")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check_branch_name.py <head-branch>", file=sys.stderr)
        return 2
    branch = sys.argv[1].strip()
    pattern = branch_pattern()
    if pattern.fullmatch(branch):
        print(f"branch OK: {branch}")
        return 0
    print(
        f"branch rejected: {branch!r} does not match {pattern.pattern}", file=sys.stderr
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
