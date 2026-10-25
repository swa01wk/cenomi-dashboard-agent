"""AT-M0-T05-05 — error code registry scan."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = REPO_ROOT / "backend" / "src" / "cenomi"
REGISTRY = REPO_ROOT / "specs/contracts/error_codes.v1.yaml"


def _scan_raised_codes(root: Path) -> set[str]:
    codes: set[str] = set()
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name != "CenomiError":
                    continue
                for kw in node.keywords:
                    if kw.arg == "code" and isinstance(kw.value, ast.Constant):
                        codes.add(str(kw.value.value))
            if isinstance(node, ast.ClassDef):
                for stmt in node.body:
                    if not isinstance(stmt, ast.FunctionDef) or stmt.name != "__init__":
                        continue
                    for call in ast.walk(stmt):
                        if not isinstance(call, ast.Call):
                            continue
                        if isinstance(call.func, ast.Attribute) and call.func.attr == "__init__":
                            for kw in call.keywords:
                                if kw.arg == "code" and isinstance(kw.value, ast.Constant):
                                    codes.add(str(kw.value.value))
    return codes


def _subclass_codes(root: Path) -> set[str]:
    codes: set[str] = set()
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "CenomiError":
                        for stmt in node.body:
                            if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                                for call in ast.walk(stmt):
                                    if isinstance(call, ast.Call) and isinstance(
                                        call.func, ast.Attribute
                                    ):
                                        for kw in call.keywords:
                                            if kw.arg == "code" and isinstance(
                                                kw.value, ast.Constant
                                            ):
                                                codes.add(str(kw.value.value))
    return codes


def _load_registry() -> dict[str, dict]:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    return {entry["code"]: entry for entry in data["codes"]}


@pytest.mark.trace("AT-M0-T05-05", reqs=["ARCH-R015", "ARCH-R022"])
def test_raised_codes_are_active_in_registry() -> None:
    registry = _load_registry()
    raised = _scan_raised_codes(BACKEND_SRC) | _subclass_codes(BACKEND_SRC)
    for code in sorted(raised):
        assert code in registry, code
        assert registry[code]["status"] == "active", code


@pytest.mark.trace("AT-M0-T05-05", reqs=["ARCH-R015"])
def test_active_http_codes_are_raised() -> None:
    registry = _load_registry()
    raised = _scan_raised_codes(BACKEND_SRC) | _subclass_codes(BACKEND_SRC)
    for code, entry in registry.items():
        if entry["status"] != "active" or entry.get("channel") != "http":
            continue
        assert code in raised, f"missing raiser for active http code {code}"


@pytest.mark.trace("AT-M0-T05-05", reqs=["ARCH-R015"])
def test_scanner_rejects_unknown_fixture_code() -> None:
    fixture = REPO_ROOT / "tests/contract/fixtures/error_registry/unknown_code.py"
    tree = ast.parse(fixture.read_text(encoding="utf-8"))
    codes: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for stmt in node.body:
                if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                    for call in ast.walk(stmt):
                        if isinstance(call, ast.Call):
                            for kw in call.keywords:
                                if kw.arg == "code" and isinstance(kw.value, ast.Constant):
                                    codes.add(str(kw.value.value))
    registry = _load_registry()
    assert any(c not in registry or registry[c]["status"] != "active" for c in codes)


@pytest.mark.trace("AT-M0-T05-05", reqs=["ARCH-R015"])
def test_scanner_detects_unraised_active_code(tmp_path: Path) -> None:
    registry = _load_registry()
    active_http = {
        c
        for c, e in registry.items()
        if e["status"] == "active" and e.get("channel") == "http"
    }
    raised = _scan_raised_codes(BACKEND_SRC) | _subclass_codes(BACKEND_SRC)
    # QUERY_TIMEOUT must be raised in real tree
    assert "QUERY_TIMEOUT" in raised
    assert active_http.issubset(raised)
