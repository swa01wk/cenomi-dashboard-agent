"""SQL safety lint tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
NEGATIVE_FIXTURE = REPO_ROOT / "tests/fixtures/lint/sql_safety_negative.py"
SQL_SAFETY = REPO_ROOT / "scripts/lint/sql_safety.py"


@pytest.mark.trace("AT-M0-T03-09", reqs=["ARCH-R033"])
def test_sql_safety_flags_f_string_in_text() -> None:
    code = """
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("sql_safety", Path("scripts/lint/sql_safety.py"))
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
violations = module.scan_file(Path("tests/fixtures/lint/sql_safety_negative.py"))
raise SystemExit(1 if violations else 0)
"""
    result = subprocess.run(
        ["uv", "run", "python", "-c", code],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1


@pytest.mark.trace("AT-M0-T03-09", reqs=["ARCH-R033"])
def test_sql_safety_passes_on_backend_src() -> None:
    result = subprocess.run(
        [sys.executable, str(SQL_SAFETY)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
