"""HC-12 — ci/e2e harness step (ARCH-R103)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci import e2e_harness as eh


def _read_status(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R103"])
def test_e2e_not_implemented_runs_harness_passed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    status = tmp_path / "status.jsonl"
    spec = tmp_path / "spec_set.yaml"
    spec.write_text("active_milestone: M0\n", encoding="utf-8")
    status.write_text(
        '{"item":"e2e","kind":"target","result":"NOT_IMPLEMENTED","reason":"stub"}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(eh, "STATUS_PATH", status)
    monkeypatch.setattr(eh, "SPEC_SET", spec)
    monkeypatch.setattr(eh, "REPO_ROOT", tmp_path)

    with patch.object(eh, "run_playwright_harness", return_value=True):
        code = eh.main()

    assert code == 0
    records = _read_status(status)
    harness = [r for r in records if r["item"] == "e2e-harness"]
    assert len(harness) == 1
    assert harness[0]["kind"] == "step"
    assert harness[0]["result"] == "PASSED"


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R103"])
def test_e2e_not_implemented_harness_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    status = tmp_path / "status.jsonl"
    spec = tmp_path / "spec_set.yaml"
    spec.write_text("active_milestone: M0\n", encoding="utf-8")
    status.write_text(
        '{"item":"e2e","kind":"target","result":"NOT_IMPLEMENTED","reason":"stub"}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(eh, "STATUS_PATH", status)
    monkeypatch.setattr(eh, "SPEC_SET", spec)
    monkeypatch.setattr(eh, "REPO_ROOT", tmp_path)

    with patch.object(eh, "run_playwright_harness", return_value=False):
        code = eh.main()

    assert code == 1
    harness = next(r for r in _read_status(status) if r["item"] == "e2e-harness")
    assert harness["result"] == "FAILED"


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R103"])
def test_e2e_passed_skips_harness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    status = tmp_path / "status.jsonl"
    spec = tmp_path / "spec_set.yaml"
    spec.write_text("active_milestone: M0\n", encoding="utf-8")
    status.write_text(
        '{"item":"e2e","kind":"target","result":"PASSED","reason":"ok"}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(eh, "STATUS_PATH", status)
    monkeypatch.setattr(eh, "SPEC_SET", spec)
    monkeypatch.setattr(eh, "REPO_ROOT", tmp_path)

    with patch.object(eh, "run_playwright_harness") as run_mock:
        code = eh.main()

    assert code == 0
    run_mock.assert_not_called()
    assert not any(r.get("item") == "e2e-harness" for r in _read_status(status))
