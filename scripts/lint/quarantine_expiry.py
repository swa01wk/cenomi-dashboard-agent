"""Fail when a quarantined test has an expired expiry date (ARCH-R088)."""

from __future__ import annotations

import ast
import re
import sys
from datetime import UTC, date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

QUARANTINE_KW = re.compile(
    r"quarantine\s*\(\s*defect\s*=\s*['\"](DEF-\d{4})['\"]\s*,\s*expires\s*=\s*['\"](\d{4}-\d{2}-\d{2})['\"]\s*\)"
)
QUARANTINE_TITLE = re.compile(
    r"\[QUARANTINE\s+(DEF-\d{4})\s+until\s+(\d{4}-\d{2}-\d{2})\]",
    re.IGNORECASE,
)

SCAN_ROOTS = (
    REPO_ROOT / "backend" / "tests",
    REPO_ROOT / "tests",
    REPO_ROOT / "apps" / "web",
    REPO_ROOT / "packages",
)


def _scan_python(path: Path, today: date) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for match in QUARANTINE_KW.finditer(text):
        defect, expires_s = match.group(1), match.group(2)
        expires = date.fromisoformat(expires_s)
        if expires < today:
            errors.append(f"{path}: quarantine {defect} expired on {expires_s}")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return errors
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "pytest"
            and func.attr == "mark"
        ):
            continue
        if not (isinstance(func, ast.Attribute) and func.attr == "quarantine"):
            continue
        kwargs = {
            kw.arg: kw.value for kw in node.keywords if kw.arg in {"defect", "expires"}
        }
        if not (
            "defect" in kwargs
            and "expires" in kwargs
            and isinstance(kwargs["defect"], ast.Constant)
            and isinstance(kwargs["expires"], ast.Constant)
        ):
            continue
        expires_s = str(kwargs["expires"].value)
        defect = str(kwargs["defect"].value)
        expires = date.fromisoformat(expires_s)
        if expires < today:
            errors.append(f"{path}: quarantine {defect} expired on {expires_s}")
    return errors


def _scan_text(path: Path, today: date) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for match in QUARANTINE_TITLE.finditer(text):
        defect, expires_s = match.group(1), match.group(2)
        expires = date.fromisoformat(expires_s)
        if expires < today:
            errors.append(f"{path}: quarantine {defect} expired on {expires_s}")
    return errors


def collect_expired(today: date | None = None) -> list[str]:
    today = today or datetime.now(tz=UTC).date()
    errors: list[str] = []
    for root in SCAN_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.suffix == ".py":
                errors.extend(_scan_python(path, today))
            elif path.suffix in {".ts", ".tsx", ".js", ".jsx", ".md"}:
                errors.extend(_scan_text(path, today))
    return errors


def main() -> int:
    errors = collect_expired()
    if errors:
        for err in sorted(errors):
            print(err, file=sys.stderr)
        return 1
    print("quarantine_expiry: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
