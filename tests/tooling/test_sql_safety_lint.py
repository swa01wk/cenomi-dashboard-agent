"""SQL safety lint tests."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SQL_SAFETY = REPO_ROOT / "scripts/lint/sql_safety.py"


def _load_sql_safety_module():
    spec = importlib.util.spec_from_file_location("sql_safety", SQL_SAFETY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.trace("AT-M0-T03-09", reqs=["ARCH-R033"])
def test_sql_safety_flags_f_string_in_text(tmp_path: Path) -> None:
    negative = tmp_path / "sql_safety_negative.py"
    negative.write_text(
        'from sqlalchemy import text\n\n'
        'table = "users"\n'
        'query = text(f"SELECT 1 FROM {table}")  # noqa: F841\n',
        encoding="utf-8",
    )
    sql_safety = _load_sql_safety_module()
    violations = sql_safety.scan_file(negative)
    assert violations
    assert any("f-string passed to text()" in item for item in violations)


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
