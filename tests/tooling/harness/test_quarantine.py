"""AT-M0-T11-03 — quarantine marker and expiry lint."""

from __future__ import annotations

import subprocess
import textwrap
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND = REPO_ROOT / "backend"


def _run_pytest(test_path: Path) -> subprocess.CompletedProcess[str]:
    import os

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    env.setdefault("TZ", "UTC")
    return subprocess.run(
        [
            "uv",
            "run",
            "--directory",
            str(BACKEND),
            "pytest",
            f"--rootdir={BACKEND}",
            f"--config-file={BACKEND / 'pyproject.toml'}",
            "-p",
            "scripts.testing.pytest_trace",
            "--strict-markers",
            str(test_path),
            "-q",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.trace("AT-M0-T11-03", reqs=["ARCH-R088"])
def test_quarantine_without_defect_or_expires_fails_collection(tmp_path: Path) -> None:
    test_file = tmp_path / "test_quarantine_bad.py"
    test_file.write_text(
        textwrap.dedent(
            """
            import pytest

            @pytest.mark.quarantine(defect="DEF-0001")
            def test_flaky():
                assert True
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    proc = _run_pytest(test_file)
    assert proc.returncode != 0
    assert (
        "defect" in proc.stdout + proc.stderr or "expires" in proc.stdout + proc.stderr
    )


@pytest.mark.trace("AT-M0-T11-03", reqs=["ARCH-R088"])
def test_expired_quarantine_makes_lint_exit_one(tmp_path: Path) -> None:
    expired = (date.today() - timedelta(days=1)).isoformat()
    test_file = tmp_path / "expired_quarantine.py"
    test_file.write_text(
        f'@pytest.mark.quarantine(defect="DEF-0099", expires="{expired}")\n',
        encoding="utf-8",
    )
    proc = subprocess.run(
        [
            "uv",
            "run",
            "--directory",
            str(BACKEND),
            "python",
            "-c",
            textwrap.dedent(
                f"""
                from datetime import date
                from pathlib import Path
                from scripts.lint import quarantine_expiry as q
                errors = q._scan_python(Path({str(test_file)!r}), date.today())
                raise SystemExit(1 if errors else 0)
                """
            ).strip(),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
