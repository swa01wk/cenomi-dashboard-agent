"""security-check unit tests (M0-T10, no network)."""

from __future__ import annotations

import json
from subprocess import CompletedProcess

import pytest

from scripts.specs import security as sec
from scripts.specs.security import (
    _is_gpl_family,
    classify_node_licences,
    parse_pnpm_licenses_json,
    pip_audit_violations,
    run_pip_audit,
)


def test_pip_audit_blocks_any_fixable_vuln() -> None:
    payload = {
        "dependencies": [
            {
                "name": "certifi",
                "vulns": [{"id": "PYSEC-2026-4320", "fix_versions": ["2026.10.19"]}],
            }
        ]
    }
    fixable, unfixable = pip_audit_violations(payload)
    assert fixable == ["certifi"]
    assert unfixable == []


def test_pip_audit_warns_unfixable() -> None:
    payload = {
        "dependencies": [
            {"name": "pkg", "vulns": [{"id": "X", "fix_versions": []}]},
        ]
    }
    fixable, unfixable = pip_audit_violations(payload)
    assert fixable == []
    assert len(unfixable) == 1


def test_run_pip_audit_exit1_unfixable_only_returns_0(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "dependencies": [
            {"name": "pkg", "vulns": [{"id": "X", "fix_versions": []}]},
        ]
    }

    def fake_run(*_a, **_k):
        return CompletedProcess([], 1, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(sec, "_run", fake_run)
    assert run_pip_audit() == 0


def test_run_pip_audit_exit1_fixable_returns_1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "dependencies": [
            {
                "name": "certifi",
                "vulns": [{"id": "Y", "fix_versions": ["1.0.1"]}],
            }
        ]
    }

    def fake_run(*_a, **_k):
        return CompletedProcess([], 1, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(sec, "_run", fake_run)
    assert run_pip_audit() == 1


def test_run_pip_audit_exit0_clean_returns_0(monkeypatch: pytest.MonkeyPatch) -> None:
    payload: dict[str, list] = {"dependencies": []}

    def fake_run(*_a, **_k):
        return CompletedProcess([], 0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(sec, "_run", fake_run)
    assert run_pip_audit() == 0


def test_run_pip_audit_non_json_returns_1(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_a, **_k):
        return CompletedProcess([], 2, stdout="not json", stderr="")

    monkeypatch.setattr(sec, "_run", fake_run)
    assert run_pip_audit() == 1


def test_run_pip_audit_exit1_empty_stdout_returns_1(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_run(*_a, **_k):
        return CompletedProcess([], 1, stdout="", stderr="pip-audit crashed\n")

    monkeypatch.setattr(sec, "_run", fake_run)
    assert run_pip_audit() == 1
    assert "pip-audit crashed" in capsys.readouterr().err


def test_run_pip_audit_exit0_empty_stdout_returns_1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(*_a, **_k):
        return CompletedProcess([], 0, stdout="   ", stderr="")

    monkeypatch.setattr(sec, "_run", fake_run)
    assert run_pip_audit() == 1


def test_gpl_classifier_form() -> None:
    assert _is_gpl_family("GNU General Public License v3 (GPLv3)")


def test_lgpl_other_than_psycopg_is_gpl_family() -> None:
    assert _is_gpl_family("LGPL-3.0-or-later")


def test_psycopg_lgpl_not_violation() -> None:
    violations, _ = classify_node_licences([("psycopg", "LGPL-3.0-or-later")])
    assert violations == []


def test_gpl_software_violation_helper() -> None:
    violations, _ = classify_node_licences([("evil", "GPL-3.0-only")])
    assert violations == ["evil: GPL-3.0-only"]


def test_pnpm_licenses_json_shape() -> None:
    sample = {
        "MIT": [
            {"name": "@scope/pkg", "versions": ["1.0.0"], "license": "MIT"},
        ]
    }
    rows = parse_pnpm_licenses_json(sample)
    assert rows == [("@scope/pkg", "MIT")]


def test_pnpm_licenses_invalid_fails_parse() -> None:
    with pytest.raises(TypeError):
        parse_pnpm_licenses_json([])


def test_unknown_licence_listed_not_failing() -> None:
    violations, unknown = classify_node_licences([("mystery", "unknown")])
    assert violations == []
    assert unknown == ["mystery"]
