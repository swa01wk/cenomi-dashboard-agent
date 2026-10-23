"""security-check unit tests (M0-T10, no network)."""

from __future__ import annotations

import pytest

from scripts.specs.security import _licence_violations, pip_audit_violations

pytestmark = pytest.mark.trace("AT-M0-T10-01", reqs=["DEVENV-R046"])


def test_pip_audit_violations_high_with_fix() -> None:
    payload = {
        "dependencies": [
            {
                "name": "certifi",
                "vulns": [
                    {
                        "id": "PYSEC-2026-4320",
                        "severity": "HIGH",
                        "fix_versions": ["2026.10.19"],
                    }
                ],
            }
        ]
    }
    assert pip_audit_violations(payload) == ["certifi"]


def test_pip_audit_ignores_low_severity() -> None:
    payload = {
        "dependencies": [
            {
                "name": "pkg",
                "vulns": [{"severity": "LOW", "fix_versions": ["1.0.1"]}],
            }
        ]
    }
    assert pip_audit_violations(payload) == []


def test_pip_audit_ignores_no_fix() -> None:
    payload = {
        "dependencies": [
            {
                "name": "pkg",
                "vulns": [{"severity": "CRITICAL", "fix_versions": []}],
            }
        ]
    }
    assert pip_audit_violations(payload) == []


def test_lgpl_psycopg_accepted() -> None:
    assert _licence_violations([("psycopg", "LGPL-3.0")]) == []


def test_gpl_family_rejected() -> None:
    assert _licence_violations([("badpkg", "GPL-3.0")]) == ["badpkg: GPL-3.0"]
