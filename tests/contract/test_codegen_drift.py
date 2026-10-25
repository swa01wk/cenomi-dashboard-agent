"""AT-M0-T05-03 — drift detection for GENERATED artefacts."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.codegen.drift import compare_staging_to_committed, find_stale_generated_files
from scripts.codegen.run_codegen import run_codegen


@pytest.mark.trace("AT-M0-T05-03", reqs=["ARCH-R092", "ARCH-R093"])
def test_stale_generated_file_is_detected() -> None:
    staging = Path(tempfile.mkdtemp())
    try:
        run_codegen(root=staging)
        target = staging / "packages/contracts-ts/src/zod/error_envelope.v1.ts"
        target.write_text(target.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        stale = compare_staging_to_committed(staging)
        assert any("error_envelope.v1.ts" in item for item in stale)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


@pytest.mark.trace("AT-M0-T05-03", reqs=["ARCH-R015"])
def test_drift_scanner_lists_path() -> None:
    stale = find_stale_generated_files()
    assert isinstance(stale, list)
