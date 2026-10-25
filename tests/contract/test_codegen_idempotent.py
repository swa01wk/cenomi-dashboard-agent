"""AT-M0-T05-02 — codegen is idempotent."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.codegen.run_codegen import run_codegen


@pytest.mark.trace("AT-M0-T05-02", reqs=["ARCH-R015", "ARCH-R093"])
def test_codegen_twice_is_identical() -> None:
    a = Path(tempfile.mkdtemp())
    b = Path(tempfile.mkdtemp())
    try:
        run_codegen(root=a)
        run_codegen(root=b)
        for path in a.rglob("*"):
            if path.is_dir():
                continue
            rel = path.relative_to(a)
            other = b / rel
            assert other.is_file(), rel
            assert path.read_bytes() == other.read_bytes(), rel
    finally:
        shutil.rmtree(a, ignore_errors=True)
        shutil.rmtree(b, ignore_errors=True)
