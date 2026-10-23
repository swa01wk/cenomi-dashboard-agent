"""AT-M0-T11-01 — pytest trace marker and strict markers."""

from __future__ import annotations

import subprocess
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND = REPO_ROOT / "backend"
HARNESS = Path(__file__).resolve().parent


def _run_pytest(
    args: list[str], *, cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    import os

    merged = os.environ.copy()
    merged.setdefault("TZ", "UTC")
    merged["PYTHONPATH"] = str(REPO_ROOT)
    if env:
        merged.update(env)
    cmd = [
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
        "--disable-socket",
        "--allow-hosts=127.0.0.1,localhost,::1",
        *args,
    ]
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=merged,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.trace("AT-M0-T11-01", reqs=["ARCH-R083", "ARCH-R102"])
def test_trace_marker_writes_junit_properties(tmp_path: Path) -> None:
    test_file = tmp_path / "test_trace_sample.py"
    junit = tmp_path / "junit.xml"
    test_file.write_text(
        textwrap.dedent(
            """
            import pytest

            @pytest.mark.trace("AT-M0-T11-01", reqs=["ARCH-R083"])
            def test_sample():
                assert True
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    proc = _run_pytest(
        [str(test_file), f"--junitxml={junit}", "-q"],
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    root = ET.parse(junit).getroot()
    props = {
        (prop.attrib.get("name"), prop.attrib.get("value"))
        for case in root.iter("testcase")
        for prop in case.findall("properties/property")
    }
    assert ("at_id", "AT-M0-T11-01") in props
    assert ("req_id", "ARCH-R083") in props


@pytest.mark.trace("AT-M0-T11-01", reqs=["ARCH-R083"])
def test_unregistered_marker_fails_collection(tmp_path: Path) -> None:
    test_file = tmp_path / "test_bad_marker.py"
    test_file.write_text(
        textwrap.dedent(
            """
            import pytest

            @pytest.mark.not_a_registered_marker
            def test_bad():
                assert True
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    proc = _run_pytest([str(test_file), "-q"], cwd=REPO_ROOT)
    assert proc.returncode != 0
    assert "not_a_registered_marker" in proc.stdout + proc.stderr
