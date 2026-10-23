"""AT-M0-T11-06 and AT-M0-T11-08 — CI report parsers and summary sections."""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.reports import (
    acceptance_result_from_junit,
    append_ci_summary_sections,
    expected_report_result,
    map_junit_outcome,
    parse_junit,
    read_status_jsonl,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "reports"


@pytest.mark.trace("AT-M0-T11-08", reqs=["ARCH-R102", "ARCH-R104"])
@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        ("passed", "PASSED"),
        ("failure", "FAILED"),
        ("error", "FAILED"),
        ("skipped", "SKIPPED"),
    ],
)
def test_map_junit_outcome(outcome: str, expected: str) -> None:
    assert map_junit_outcome(outcome) == expected


@pytest.mark.trace("AT-M0-T11-08", reqs=["ARCH-R102"])
def test_parse_junit_fixture_counts() -> None:
    path = FIXTURES / "junit-mixed.xml"
    counts, cases = parse_junit(path)
    assert counts.passed == 2
    assert counts.failed == 1
    assert counts.errors == 1
    assert counts.skipped == 1
    at_cases = [c for c in cases if c.at_id == "AT-M0-T11-08"]
    assert len(at_cases) == 2
    assert any(c.result == "SKIPPED" for c in at_cases)
    assert acceptance_result_from_junit(path, "AT-M0-T11-08") == "SKIPPED"


@pytest.mark.trace("AT-M0-T11-08", reqs=["ARCH-R102"])
def test_missing_or_unparseable_report_is_failed(tmp_path: Path) -> None:
    missing = tmp_path / "missing.xml"
    assert expected_report_result(missing) == "FAILED"
    bad = tmp_path / "bad.xml"
    bad.write_text("not xml", encoding="utf-8")
    assert expected_report_result(bad) == "FAILED"


@pytest.mark.trace("AT-M0-T11-08", reqs=["ARCH-R102"])
def test_read_status_jsonl_fixture() -> None:
    records = read_status_jsonl(FIXTURES / "status.jsonl")
    assert records[0]["result"] == "PASSED"
    assert records[1]["item"] == "backend-test"


@pytest.mark.trace("AT-M0-T11-06", reqs=["DEVENV-R031"])
def test_ci_summary_sections_include_m0_applicable_blocks(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    (reports / "backend").mkdir(parents=True)
    (reports / "frontend").mkdir(parents=True)
    (reports / "e2e").mkdir(parents=True)
    (reports / "ci").mkdir(parents=True)

    for name in ("junit-unit.xml", "junit-integration.xml"):
        (reports / "backend" / name).write_text(
            (FIXTURES / "junit-mixed.xml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    (reports / "frontend" / "junit-vitest.xml").write_text(
        textwrap.dedent(
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <testsuites>
              <testsuite tests="1" failures="0" errors="0" skipped="0">
                <testcase classname="vitest" name="[AT-M0-T11-02] title sample" time="0.01"/>
              </testsuite>
            </testsuites>
            """
        ).strip(),
        encoding="utf-8",
    )
    (reports / "ci" / "trace-report-excerpt.md").write_text(
        "AT-M0-T11-06: PASSED",
        encoding="utf-8",
    )
    (reports / "backend" / "coverage.xml").write_text(
        textwrap.dedent(
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <coverage line-rate="0.5" branch-rate="0.0" lines-covered="1" lines-valid="2"/>
            """
        ).strip(),
        encoding="utf-8",
    )

    header = "# CI summary\n\n- Dataset: not seeded\n"
    sections = header + "\n".join(append_ci_summary_sections(reports))
    assert "Dataset: not seeded" in sections
    assert "## Backend, frontend and integration test counts" in sections
    assert "## Agent mock and replay results" in sections
    assert "Not applicable in M0" in sections
    assert "## Database invariant and canonical-figure results" in sections
    assert "## Contract and specification check results" in sections
    assert "## Playwright results" in sections
    assert "## Accessibility findings by severity" in sections
    assert "## Evaluation metrics" in sections
    assert "## Coverage (informational)" in sections
    assert "## ECharts gate result" in sections
    assert "## Trace-report excerpt" in sections
    assert "## Failing E2E request references" in sections


@pytest.mark.trace("AT-M0-T11-02", reqs=["ARCH-R083"])
def test_vitest_junit_at_title_fixture() -> None:
    path = FIXTURES / "junit-vitest-at.xml"
    _, cases = parse_junit(path)
    assert cases[0].at_id == "AT-M0-T11-02"
