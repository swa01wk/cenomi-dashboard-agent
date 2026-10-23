"""AT-M0-T07 — make ci safety (make_targets.yaml ci behaviour)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.make_ci import (
    caller_is_real_ci,
    sanitized_job_env,
    trim_specs_status_after_tooling_backend_test,
    validate_target,
)


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R026"])
def test_caller_is_real_ci_github_actions() -> None:
    assert caller_is_real_ci({"GITHUB_ACTIONS": "true", "CENOMI_ENV": "dev"})


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R026"])
def test_caller_is_real_ci_cenomi_env_only_when_set_by_caller() -> None:
    assert caller_is_real_ci({"CENOMI_ENV": "ci"})
    assert not caller_is_real_ci({"CENOMI_ENV": "dev"})


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R026"])
def test_job_env_does_not_self_authorize_ci_or_confirm() -> None:
    job_env = {"CENOMI_ENV": "ci", "CONFIRM": "yes", "DB": "test"}
    assert sanitized_job_env(job_env, real_ci=False) == {"DB": "test"}
    assert sanitized_job_env(job_env, real_ci=True)["CONFIRM"] == "yes"


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R026"])
def test_forbidden_targets() -> None:
    assert validate_target("db-downgrade", {}, True) is not None
    assert validate_target("agent-test-live", {}, True) is not None


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R026"])
def test_seed_reset_requires_test_db() -> None:
    err = validate_target(
        "seed-reset",
        {"DB": "dev", "CONFIRM": "yes"},
        real_ci=True,
    )
    assert err is not None
    assert "DB=test" in err


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R026"])
def test_trim_specs_status_after_tooling_backend_test(tmp_path: Path) -> None:
    status = tmp_path / "status.jsonl"
    nested = (
        '{"item":"down","kind":"target","result":"FAILED","reason":"guard"}\n'
        '{"item":"backend-test","kind":"target","result":"PASSED","reason":"tooling"}\n'
    )
    status.write_text(nested, encoding="utf-8")
    trim_specs_status_after_tooling_backend_test(status, lines_before=0)
    lines = status.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert "backend-test" in lines[0]


@pytest.mark.trace("AT-M0-T07-04", reqs=["DEVENV-R026"])
def test_seed_reset_outside_ci_requires_tty_and_confirm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    err = validate_target("seed-reset", {"DB": "test", "CONFIRM": "yes"}, real_ci=False)
    assert err is not None
