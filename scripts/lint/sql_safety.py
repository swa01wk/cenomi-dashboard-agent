"""SQL safety lint — flags dynamic SQL passed to text() (ARCH-R033)."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = (REPO_ROOT / "backend" / "src", REPO_ROOT / "backend" / "migrations")


class SqlSafetyVisitor(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.violations: list[str] = []

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        is_text = (isinstance(func, ast.Name) and func.id == "text") or (
            isinstance(func, ast.Attribute) and func.attr == "text"
        )
        if is_text and node.args:
            arg0 = node.args[0]
            if isinstance(arg0, ast.JoinedStr):
                self.violations.append(
                    f"{self.path}:{arg0.lineno}: f-string passed to text() is forbidden"
                )
        self.generic_visit(node)


def scan_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    visitor = SqlSafetyVisitor(path)
    visitor.visit(tree)
    return visitor.violations


def main() -> int:
    paths = [p for root in SCAN_ROOTS if root.is_dir() for p in root.rglob("*.py")]

    violations: list[str] = []
    for path in sorted(set(paths)):
        violations.extend(scan_file(path))

    if violations:
        for item in violations:
            print(item, file=sys.stderr)
        return 1
    print("sql_safety: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
