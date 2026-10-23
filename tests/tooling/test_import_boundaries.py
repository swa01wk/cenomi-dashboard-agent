"""Import boundary lint tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPO_ROOT / "backend"
ANALYTICS_INIT = BACKEND / "src/cenomi/analytics/__init__.py"


def _run_lint_imports() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "--directory", str(BACKEND), "import-linter", "lint"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.trace("AT-M0-T03-04", reqs=["ARCH-R006", "ARCH-R007"])
def test_lint_imports_passes() -> None:
    result = _run_lint_imports()
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.trace("AT-M0-T03-04", reqs=["ARCH-R006", "ARCH-R007"])
def test_forbidden_analytics_to_agent_import_fails_lint(tmp_path: Path) -> None:
    original = ANALYTICS_INIT.read_text(encoding="utf-8")
    patched = original + "\nimport cenomi.agent  # forbidden boundary probe\n"
    ANALYTICS_INIT.write_text(patched, encoding="utf-8")
    try:
        result = _run_lint_imports()
        assert result.returncode != 0
    finally:
        ANALYTICS_INIT.write_text(original, encoding="utf-8")
