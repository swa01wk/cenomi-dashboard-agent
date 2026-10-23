"""Makefile contract acceptance tests (M0-T01)."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKE_TARGETS = REPO_ROOT / "specs/engineering/make_targets.yaml"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
SPEC_SET = REPO_ROOT / "specs/engineering/spec_set.yaml"

DEVENV_VARS = [
    "CENOMI_ENV",
    "DATABASE_URL_ADMIN",
    "DATABASE_URL_OWNER",
    "DATABASE_URL_SEED",
    "DATABASE_URL_READER",
    "DATABASE_URL_APP",
    "DB_READER_POOL_SIZE",
    "DB_APP_POOL_SIZE",
    "DB_READER_STATEMENT_TIMEOUT_MS",
    "CENOMI_DATASET_ID",
    "CENOMI_AS_OF",
    "CENOMI_TZ",
    "CENOMI_SEED",
    "AUTH_MODE",
    "SESSION_SECRET",
    "SESSION_TTL_MINUTES",
    "LLM_MODE",
    "LLM_PROVIDER",
    "LLM_PRIMARY_MODEL",
    "LLM_FALLBACK_MODEL",
    "LLM_API_KEY",
    "LLM_REPLAY_DIR",
    "AGENT_MAX_STEPS",
    "AGENT_MAX_SECONDS",
    "AGENT_MAX_TOKENS",
    "LIVE_EVAL_LLM_API_KEY",
    "LIVE_EVAL_MAX_CASES",
    "LIVE_EVAL_MAX_TOKENS",
    "LIVE_EVAL_MAX_COST_USD",
    "OTEL_EXPORTER",
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "LOG_LEVEL",
    "API_INTERNAL_URL",
]


def _run_make(*args: str, env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        ["make", *args],
        cwd=cwd or REPO_ROOT,
        env=merged,
        capture_output=True,
        text=True,
        check=False,
    )


def _yaml_targets() -> list[str]:
    data = yaml.safe_load(MAKE_TARGETS.read_text(encoding="utf-8"))
    return [entry["name"] for entry in data["targets"]]


def _last_status_line(target: str, jsonl_path: Path) -> dict | None:
    if not jsonl_path.is_file():
        return None
    last = None
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("item") == target and record.get("kind") == "target":
            last = record
    return last


def _clear_status() -> None:
    path = REPO_ROOT / "tests/reports/status.jsonl"
    if path.is_file():
        path.unlink()


@pytest.mark.trace("AT-M0-T01-01", reqs=["DEVENV-R002", "DEVENV-R003", "DEVENV-R052"])
def test_make_install_clean_git_status() -> None:
    proc = _run_make("install")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    assert status.returncode == 0
    assert status.stdout.strip() == "", f"git status not clean:\n{status.stdout}"


@pytest.mark.trace("AT-M0-T01-02", reqs=["DEVENV-R001"])
def test_make_doctor_toolchain() -> None:
    ok = _run_make("doctor")
    assert ok.returncode == 0, ok.stdout + ok.stderr

    shim_dir = REPO_ROOT / "tests/reports/tmp/node-shim"
    shim_dir.mkdir(parents=True, exist_ok=True)
    shim = shim_dir / "node"
    shim.write_text("#!/bin/sh\necho v20.0.0\n", encoding="utf-8")
    shim.chmod(0o755)
    bad = subprocess.run(
        ["python3", "scripts/make/invoke.py", "doctor"],
        cwd=REPO_ROOT,
        env={**os.environ, "PATH": f"{shim_dir}:{os.environ.get('PATH', '')}"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad.returncode == 3, bad.stdout + bad.stderr


@pytest.mark.trace("AT-M0-T01-03", reqs=["DEVENV-R011"])
def test_make_help_matches_yaml_order() -> None:
    proc = _run_make("help")
    assert proc.returncode == 0, proc.stderr
    help_names = re.findall(r"^\s{2}([a-z0-9-]+)\s", proc.stdout, re.MULTILINE)
    assert help_names == _yaml_targets()

    targets_path = REPO_ROOT / "scripts" / "make" / "targets.py"
    spec = importlib.util.spec_from_file_location("make_targets_module", targets_path)
    assert spec and spec.loader
    make_targets = importlib.util.module_from_spec(spec)
    sys.modules["make_targets_module"] = make_targets
    spec.loader.exec_module(make_targets)

    yaml_data = yaml.safe_load(MAKE_TARGETS.read_text(encoding="utf-8"))
    yaml_entries = yaml_data["targets"]
    assert len(make_targets.TARGETS) == len(yaml_entries)
    for meta, entry in zip(make_targets.TARGETS, yaml_entries, strict=True):
        assert meta.name == entry["name"]
        assert meta.group == entry["group"]
        assert meta.active_from == entry["active_from"]
        assert meta.summary == entry["summary"]


@pytest.mark.trace("AT-M0-T01-04", reqs=["DEVENV-R013", "ARCH-R103"])
def test_target_results_milestone_and_stubs() -> None:
    _clear_status()
    na_target = "seed"
    proc = _run_make(na_target)
    assert proc.returncode == 0
    assert f"NOT_APPLICABLE: {na_target} becomes active in M1" in proc.stdout.splitlines()[-1]
    record = _last_status_line(na_target, REPO_ROOT / "tests/reports/status.jsonl")
    assert record is not None
    assert record["result"] == "NOT_APPLICABLE"
    assert record["rule"] == "milestone"

    stub = "up"
    _clear_status()
    stub_proc = _run_make(stub)
    assert stub_proc.returncode == 0
    assert stub_proc.stdout.splitlines()[-1].startswith(f"NOT_IMPLEMENTED: {stub} —")
    gate_proc = subprocess.run(
        ["python3", "scripts/make/invoke.py", stub],
        cwd=REPO_ROOT,
        env={**os.environ, "GATE": "M0"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert gate_proc.returncode == 1

    tmp = REPO_ROOT / "tests/reports/tmp/spec_set_m1"
    tmp.mkdir(parents=True, exist_ok=True)
    spec_copy = tmp / "spec_set.yaml"
    spec_copy.write_text(
        SPEC_SET.read_text(encoding="utf-8").replace("active_milestone: M0", "active_milestone: M1"),
        encoding="utf-8",
    )
    m1_proc = subprocess.run(
        ["python3", "scripts/make/invoke.py", stub],
        cwd=REPO_ROOT,
        env={**os.environ, "CENOMI_SPEC_SET": str(spec_copy)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert m1_proc.returncode == 1

    help_proc = _run_make("help")
    help_record = _last_status_line("help", REPO_ROOT / "tests/reports/status.jsonl")
    assert help_record is not None and help_record["result"] == "PASSED"
    _run_make(stub)
    stub_record = _last_status_line(stub, REPO_ROOT / "tests/reports/status.jsonl")
    assert stub_record is not None and stub_record["result"] == "NOT_IMPLEMENTED"


@pytest.mark.trace("AT-M0-T01-05", reqs=["DEVENV-R012", "DEVENV-R014"])
def test_destructive_guards_exit_two() -> None:
    down = _run_make("down", env={"VOLUMES": "1", "CONFIRM": ""})
    assert down.returncode == 2
    downgrade = _run_make("db-downgrade", env={"REV": "", "CONFIRM": ""})
    assert downgrade.returncode == 2


@pytest.mark.trace("AT-M0-T01-06", reqs=["DEVENV-R011"])
def test_make_check_without_database() -> None:
    proc = _run_make("check")
    assert proc.returncode == 0, proc.stdout + proc.stderr


@pytest.mark.trace("AT-M0-T01-07", reqs=["DEVENV-R009", "DEVENV-R010"])
def test_env_example_catalogue_and_gitleaks() -> None:
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    for var in DEVENV_VARS:
        assert f"{var}=" in text, f"missing {var}"
    assert "change-me-dev-only" in text

    if shutil.which("gitleaks") is None:
        pytest.fail("gitleaks required — run make doctor")

    proc = subprocess.run(
        ["gitleaks", "detect", "--no-git", "--source", str(ENV_EXAMPLE), "--redact"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
