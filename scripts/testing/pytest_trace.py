"""Pytest trace and quarantine markers (M0-T11, ARCH-R083, ARCH-R088)."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ID_CONVENTIONS = REPO_ROOT / "specs/traceability/id_conventions.yaml"

STRICT_MARKERS: dict[str, str] = {
    "unit": "Unit tests — no database or external network",
    "integration": "Integration tests against cenomi_test or the local stack",
    "db": "Database-focused tests",
    "contract": "Contract validation tests",
    "security": "Security and authorization tests",
    "agent_mock": "Agent tests with the mock provider (M3+)",
    "agent_replay": "Agent tests with the replay provider (M3+)",
    "agent_live": "Live-model agent tests (manual / eval-live only)",
    "slow": "Slow tests (may be deselected in fast CI)",
    "trace": "Acceptance-test traceability marker",
    "quarantine": "Flaky test quarantine (ARCH-R088)",
}


def _convention_patterns() -> dict[str, re.Pattern[str]]:
    data = yaml.safe_load(ID_CONVENTIONS.read_text(encoding="utf-8"))
    families = {entry["id"]: entry["pattern"] for entry in data["families"]}
    return {
        "acceptance_test": re.compile(families["acceptance_test"]),
        "spec_requirement": re.compile(families["spec_requirement"]),
        "defect": re.compile(families["defect"]),
    }


_PATTERNS: dict[str, re.Pattern[str]] | None = None


def _patterns() -> dict[str, re.Pattern[str]]:
    global _PATTERNS
    if _PATTERNS is None:
        _PATTERNS = _convention_patterns()
    return _PATTERNS


def _validate_at_id(at_id: str, nodeid: str) -> None:
    if not _patterns()["acceptance_test"].fullmatch(at_id):
        raise pytest.UsageError(f"{nodeid}: invalid acceptance test id {at_id!r}")


def _validate_req_id(req_id: str, nodeid: str) -> None:
    if not _patterns()["spec_requirement"].fullmatch(req_id):
        raise pytest.UsageError(f"{nodeid}: invalid requirement id {req_id!r}")


def _parse_expires(value: str, nodeid: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise pytest.UsageError(
            f"{nodeid}: quarantine expires must be YYYY-MM-DD, got {value!r}"
        ) from exc


def _validate_quarantine(marker: pytest.Mark, nodeid: str) -> None:
    defect = marker.kwargs.get("defect")
    expires = marker.kwargs.get("expires")
    if not defect or not expires:
        raise pytest.UsageError(
            f"{nodeid}: quarantine marker requires defect= and expires= keyword arguments"
        )
    if not _patterns()["defect"].fullmatch(str(defect)):
        raise pytest.UsageError(f"{nodeid}: invalid defect id {defect!r}")
    _parse_expires(str(expires), nodeid)


def pytest_configure(config: pytest.Config) -> None:
    for name, description in STRICT_MARKERS.items():
        config.addinivalue_line("markers", f"{name}: {description}")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    del config
    for item in items:
        path = Path(str(item.fspath))
        parts = path.parts
        if "tests" in parts:
            idx = parts.index("tests")
            rel = parts[idx + 1 :] if idx + 1 < len(parts) else ()
            if rel[:1] == ("unit",):
                item.add_marker(pytest.mark.unit)
            elif rel[:1] == ("integration",):
                item.add_marker(pytest.mark.integration)

        trace = item.get_closest_marker("trace")
        if trace is not None:
            if not trace.args:
                raise pytest.UsageError(
                    f"{item.nodeid}: trace marker requires an AT id argument"
                )
            at_id = str(trace.args[0])
            _validate_at_id(at_id, item.nodeid)
            reqs = trace.kwargs.get("reqs") or []
            if not isinstance(reqs, list):
                raise pytest.UsageError(f"{item.nodeid}: trace reqs= must be a list")
            for req in reqs:
                _validate_req_id(str(req), item.nodeid)

        quarantine = item.get_closest_marker("quarantine")
        if quarantine is not None:
            _validate_quarantine(quarantine, item.nodeid)


@pytest.fixture(autouse=True)
def _junit_trace_properties(request: pytest.FixtureRequest) -> None:
    trace = request.node.get_closest_marker("trace")
    if trace is None:
        return
    record_property = request.getfixturevalue("record_property")
    record_property("at_id", str(trace.args[0]))
    for req in trace.kwargs.get("reqs") or []:
        record_property("req_id", str(req))
