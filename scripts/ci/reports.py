"""Parse test reports for ci/summary (M0-T11, ARCH-R102, DEVENV-R031)."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_ROOT = REPO_ROOT / "tests" / "reports"

Result = Literal["PASSED", "FAILED", "SKIPPED"]

AT_TITLE = re.compile(r"^\[(AT-M[0-6]-T[0-9]{2}-[0-9]{2})\]")
AT_PROPERTY = "at_id"


@dataclass(frozen=True)
class JUnitCounts:
    passed: int
    failed: int
    errors: int
    skipped: int

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.errors + self.skipped


@dataclass(frozen=True)
class TestCaseResult:
    name: str
    classname: str
    result: Result
    at_id: str | None
    skipped_by_pytest: bool


def map_junit_outcome(outcome: str) -> Result:
    normalized = outcome.lower()
    if normalized == "passed":
        return "PASSED"
    if normalized in {"failure", "error"}:
        return "FAILED"
    if normalized == "skipped":
        return "SKIPPED"
    return "FAILED"


def _parse_junit_counts(root: ET.Element) -> JUnitCounts:
    passed = failed = errors = skipped = 0
    for case in root.iter("testcase"):
        if case.find("skipped") is not None:
            skipped += 1
        elif case.find("failure") is not None:
            failed += 1
        elif case.find("error") is not None:
            errors += 1
        else:
            passed += 1
    return JUnitCounts(passed=passed, failed=failed, errors=errors, skipped=skipped)


def _case_at_id(case: ET.Element) -> str | None:
    if AT_PROPERTY in case.attrib:
        return case.attrib.get(AT_PROPERTY)
    for prop in case.findall("properties/property"):
        if prop.attrib.get("name") == AT_PROPERTY:
            return prop.attrib.get("value")
    name = case.attrib.get("name", "")
    match = AT_TITLE.match(name)
    if match:
        return match.group(1)
    classname = case.attrib.get("classname", "")
    match = AT_TITLE.match(classname)
    if match:
        return match.group(1)
    return None


def _case_result(case: ET.Element) -> tuple[Result, bool]:
    if case.find("skipped") is not None:
        return "SKIPPED", True
    if case.find("failure") is not None or case.find("error") is not None:
        return "FAILED", False
    return "PASSED", False


def parse_junit(path: Path) -> tuple[JUnitCounts, list[TestCaseResult]]:
    if not path.is_file():
        raise FileNotFoundError(str(path))
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"unparseable JUnit XML: {path}") from exc
    counts = _parse_junit_counts(root)
    cases: list[TestCaseResult] = []
    for case in root.iter("testcase"):
        result, skipped_by_pytest = _case_result(case)
        cases.append(
            TestCaseResult(
                name=case.attrib.get("name", ""),
                classname=case.attrib.get("classname", ""),
                result=result,
                at_id=_case_at_id(case),
                skipped_by_pytest=skipped_by_pytest,
            )
        )
    return counts, cases


def acceptance_result_from_junit(path: Path, at_id: str) -> Result:
    try:
        _, cases = parse_junit(path)
    except (FileNotFoundError, ValueError):
        return "FAILED"
    matched = [c for c in cases if c.at_id == at_id]
    if not matched:
        return "FAILED"
    if any(c.result == "FAILED" for c in matched):
        return "FAILED"
    if all(c.result == "SKIPPED" for c in matched):
        return "SKIPPED"
    if any(c.result == "SKIPPED" for c in matched):
        return "SKIPPED"
    return "PASSED"


def read_status_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(str(path))
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"unparseable status.jsonl line {line_no}: {path}"
            ) from exc
        if not isinstance(record, dict):
            raise TypeError(f"status.jsonl line {line_no} is not an object: {path}")
        records.append(record)
    return records


def target_result_from_status(records: list[dict[str, Any]], item: str) -> Result:
    last: dict[str, Any] | None = None
    for record in records:
        if record.get("item") == item and record.get("kind") == "target":
            last = record
    if last is None:
        return "FAILED"
    result = str(last.get("result", ""))
    if result in {"PASSED", "FAILED", "SKIPPED", "NOT_APPLICABLE", "NOT_IMPLEMENTED"}:
        return result  # type: ignore[return-value]
    return "FAILED"


def expected_report_result(path: Path) -> Result:
    try:
        parse_junit(path)
    except FileNotFoundError:
        return "FAILED"
    except ValueError:
        return "FAILED"
    return "PASSED"


def _read_coverage_percent(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None
    line_rate = root.attrib.get("line-rate")
    if line_rate is None:
        return None
    return f"{float(line_rate) * 100:.1f}%"


def _format_counts(label: str, counts: JUnitCounts | None) -> str:
    if counts is None:
        return f"- {label}: **FAILED** (report missing or unparseable)"
    return (
        f"- {label}: passed {counts.passed}, failed {counts.failed + counts.errors}, "
        f"skipped {counts.skipped}, total {counts.total}"
    )


def _safe_junit(path: Path) -> JUnitCounts | None:
    try:
        counts, _ = parse_junit(path)
        return counts
    except (FileNotFoundError, ValueError):
        return None


def dataset_summary_line(reports_root: Path) -> str:
    """DEVENV-R031 item 3 — dataset id and seed hash, or not seeded before M1."""
    descriptor = reports_root / "dataset" / "descriptor.json"
    seed_hash = reports_root / "dataset" / "seed-hash.txt"
    if descriptor.is_file() and seed_hash.is_file():
        try:
            payload = json.loads(descriptor.read_text(encoding="utf-8"))
            dataset_id = payload.get("datasetId") or payload.get("dataset_id")
            seed = seed_hash.read_text(encoding="utf-8").strip()
            if dataset_id and seed:
                return f"Dataset: `{dataset_id}` (seed hash `{seed}`)"
        except (json.JSONDecodeError, OSError):
            return "Dataset: **FAILED** (unparseable dataset report)"
    return "Dataset: not seeded"


def append_ci_summary_sections(
    reports_root: Path | None = None,
) -> list[str]:
    """Markdown sections for DEVENV-R031 M0-applicable content (dataset + items 5–15)."""
    root = reports_root or REPORTS_ROOT
    backend_unit = _safe_junit(root / "backend" / "junit-unit.xml")
    backend_integration = _safe_junit(root / "backend" / "junit-integration.xml")
    frontend = _safe_junit(root / "frontend" / "junit-vitest.xml")
    playwright = _safe_junit(root / "e2e" / "junit-playwright.xml")

    coverage = _read_coverage_percent(root / "backend" / "coverage.xml")

    lines = [
        "",
        "## Dataset",
        "",
        f"- {dataset_summary_line(root)}",
        "",
        "## Backend, frontend and integration test counts",
        "",
        _format_counts("Backend unit", backend_unit),
        _format_counts("Backend integration", backend_integration),
        _format_counts("Frontend (Vitest)", frontend),
        _format_counts(
            "Integration (cross-component)",
            _safe_junit(root / "integration" / "junit.xml"),
        ),
        "",
        "## Agent mock and replay results",
        "",
        "- Not applicable in M0 (active from M3).",
        "",
        "## Database invariant and canonical-figure results",
        "",
        "- Not applicable in M0 (active from M1).",
        "",
        "## Contract and specification check results",
        "",
    ]

    specs_path = root / "ci" / "specs-check.json"
    contracts_path = root / "ci" / "contracts-check.json"
    for label, path in (
        ("specs-check", specs_path),
        ("contracts-check", contracts_path),
    ):
        if path.is_file():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                lines.append(f"- {label}: **{payload.get('result', 'PASSED')}**")
            except json.JSONDecodeError:
                lines.append(f"- {label}: **FAILED** (unparseable report)")
        else:
            lines.append(f"- {label}: not run in this workspace")

    lines.extend(
        [
            "",
            "## Playwright results",
            "",
            _format_counts("Playwright E2E", playwright),
        ]
    )

    trace_dir = root / "e2e" / "traces"
    if trace_dir.is_dir():
        traces = sorted(trace_dir.glob("**/*"))
        if traces:
            lines.append(
                f"- Failure artefacts: `{trace_dir.relative_to(REPO_ROOT)}` ({len(traces)} files)"
            )

    lines.extend(
        [
            "",
            "## Accessibility findings by severity",
            "",
        ]
    )
    axe_path = root / "e2e" / "axe-summary.json"
    if axe_path.is_file():
        try:
            axe = json.loads(axe_path.read_text(encoding="utf-8"))
            for severity in ("critical", "serious", "moderate", "minor"):
                lines.append(f"- {severity}: {axe.get(severity, 0)}")
        except json.JSONDecodeError:
            lines.append("- **FAILED** (unparseable axe summary)")
    else:
        lines.append("- No axe summary uploaded for this run.")

    lines.extend(
        [
            "",
            "## Evaluation metrics",
            "",
            "- Not applicable in M0 (active from M3).",
            "",
            "## Coverage (informational)",
            "",
            f"- Backend line coverage: {coverage or 'not available'}",
            "",
            "## ECharts gate result",
            "",
        ]
    )
    echarts_path = root / "echarts-gate.json"
    if echarts_path.is_file():
        try:
            payload = json.loads(echarts_path.read_text(encoding="utf-8"))
            lines.append(f"- Result: **{payload.get('result', 'unknown')}**")
        except json.JSONDecodeError:
            lines.append("- **FAILED** (unparseable echarts gate report)")
    else:
        lines.append("- Not run in M0 bootstrap CI.")

    lines.extend(
        [
            "",
            "## Trace-report excerpt",
            "",
        ]
    )
    trace_excerpt = root / "ci" / "trace-report-excerpt.md"
    if trace_excerpt.is_file():
        excerpt = trace_excerpt.read_text(encoding="utf-8").strip()
        lines.append(excerpt if excerpt else "- (empty excerpt)")
    else:
        lines.append("- Trace report not generated for this workspace.")

    lines.extend(
        [
            "",
            "## Failing E2E request references",
            "",
        ]
    )
    refs_path = root / "e2e" / "request-refs.json"
    if refs_path.is_file():
        try:
            refs = json.loads(refs_path.read_text(encoding="utf-8"))
            if isinstance(refs, list) and refs:
                for ref in refs:
                    lines.append(f"- `{ref}`")
            else:
                lines.append("- None recorded.")
        except json.JSONDecodeError:
            lines.append("- **FAILED** (unparseable request-refs.json)")
    else:
        lines.append("- None recorded.")

    lines.append("")
    return lines
