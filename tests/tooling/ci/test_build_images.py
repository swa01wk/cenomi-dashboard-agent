"""HC-11 — ci/images build script (ARCH-R103)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci import build_images as bi


def _read_status(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R103"])
def test_web_absent_in_window_not_implemented_exit_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    status = tmp_path / "status.jsonl"
    spec = tmp_path / "spec_set.yaml"
    spec.write_text("active_milestone: M0\n", encoding="utf-8")
    web_df = tmp_path / "apps/web/Dockerfile"

    monkeypatch.setattr(bi, "STATUS_PATH", status)
    monkeypatch.setattr(bi, "SPEC_SET", spec)
    monkeypatch.setattr(bi, "WEB_DOCKERFILE", web_df)
    monkeypatch.setattr(bi, "REPO_ROOT", tmp_path)

    with patch.object(bi, "run_docker_build", return_value=True):
        code = bi.main()

    assert code == 0
    records = _read_status(status)
    web = next(r for r in records if r["item"] == "images-web")
    assert web["kind"] == "step"
    assert web["result"] == "NOT_IMPLEMENTED"
    assert web["milestone"] == "M0"


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R103"])
def test_web_absent_outside_window_failed_exit_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    status = tmp_path / "status.jsonl"
    spec = tmp_path / "spec_set.yaml"
    spec.write_text("active_milestone: M1\n", encoding="utf-8")
    web_df = tmp_path / "apps/web/Dockerfile"

    monkeypatch.setattr(bi, "STATUS_PATH", status)
    monkeypatch.setattr(bi, "SPEC_SET", spec)
    monkeypatch.setattr(bi, "WEB_DOCKERFILE", web_df)
    monkeypatch.setattr(bi, "REPO_ROOT", tmp_path)

    with patch.object(bi, "run_docker_build", return_value=True):
        code = bi.main()

    assert code == 1
    records = _read_status(status)
    web = next(r for r in records if r["item"] == "images-web")
    assert web["result"] == "FAILED"


@pytest.mark.trace("AT-M0-T07-04", reqs=["ARCH-R103"])
def test_api_build_failure_exit_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    status = tmp_path / "status.jsonl"
    spec = tmp_path / "spec_set.yaml"
    spec.write_text("active_milestone: M0\n", encoding="utf-8")

    monkeypatch.setattr(bi, "STATUS_PATH", status)
    monkeypatch.setattr(bi, "SPEC_SET", spec)
    monkeypatch.setattr(bi, "REPO_ROOT", tmp_path)

    with patch.object(bi, "run_docker_build", return_value=False):
        code = bi.main()

    assert code == 1
    api = next(r for r in _read_status(status) if r["item"] == "images-api")
    assert api["result"] == "FAILED"
