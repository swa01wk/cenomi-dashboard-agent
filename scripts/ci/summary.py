"""Aggregate CI job results and enforce fail-closed rules (DEVENV-R020, R050)."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml

from scripts.ci.changes import compute_applicability, job_make_ci, load_ci_checks
from scripts.ci.job_junit import (
    BASENAME_TO_REL,
    JOB_JUNIT,
    JUNIT_PRODUCER_TARGET,
)
from scripts.ci.job_slug import artifact_slug_to_job
from scripts.make.report import milestone_index, read_active_milestone
from scripts.trace.report import build_report

SPEC_SET = REPO_ROOT / "specs/engineering/spec_set.yaml"
SUMMARY_MD = REPO_ROOT / "tests/reports/ci-summary.md"
STATUS_JSONL = REPO_ROOT / "tests/reports/status.jsonl"
VERDICT_JSON = REPO_ROOT / "tests/reports/ci/summary-verdict.json"
STAGED_JUNIT_JSON = REPO_ROOT / "tests/reports/ci/staged-junit-paths.json"
SUMMARY_REPORT_DIR = REPO_ROOT / "tests/reports/ci/summary"
LIVE_JUNIT = SUMMARY_REPORT_DIR / "junit-live.xml"

JOBS_REQUIRING_STATUS = frozenset({"ci/images"})

BOOTSTRAP_CARDS = ("M0-T01", "M0-T03", "M0-T11", "M0-T10")

BLOCKING_CONCLUSIONS = frozenset({"success"})
FAILING_CONCLUSIONS = frozenset(
    {
        "failure",
        "cancelled",
        "timed_out",
        "neutral",
        "action_required",
        "stale",
    }
)


def _target_active_from_map() -> dict[str, str]:
    path = REPO_ROOT / "specs/engineering/make_targets.yaml"
    data = cast(dict[str, Any], yaml.safe_load(path.read_text(encoding="utf-8")))
    return {str(t["name"]): str(t["active_from"]) for t in data["targets"]}


CARD_BRANCH = re.compile(
    r"^(feat|fix|test|chore)/m(?P<m>\d+)-t(?P<t>\d{2})-",
    re.IGNORECASE,
)


@dataclass
class SummaryOutcome:
    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _load_reports_module() -> ModuleType | None:
    try:
        from scripts.ci import reports as reports_mod

        return reports_mod
    except ImportError:
        return None


def read_status_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def load_required_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"{label} missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise TypeError(f"{label} must be a JSON object: {path}")
    return data


def discover_job_status_files(status_root: Path) -> dict[str, Path]:
    """Map ci job name -> status.jsonl from downloaded status-* artifacts."""
    found: dict[str, Path] = {}
    if not status_root.is_dir():
        return found
    for child in status_root.rglob("status.jsonl"):
        parent = child.parent
        name = parent.name
        if name.startswith("status-"):
            slug = name.removeprefix("status-")
            job = artifact_slug_to_job(slug)
            found[job] = child
    for child in status_root.iterdir():
        if not child.is_dir():
            continue
        name = child.name
        if not name.startswith("status-"):
            continue
        slug = name.removeprefix("status-")
        job = artifact_slug_to_job(slug)
        candidate = child / "status.jsonl"
        if candidate.is_file():
            found[job] = candidate
    return found


def merge_status_records(paths: list[Path]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for path in paths:
        merged.extend(read_status_jsonl(path))
    return merged


def parse_card_from_branch(branch: str | None) -> str | None:
    if not branch:
        return None
    match = CARD_BRANCH.match(branch.strip())
    if not match:
        return None
    return f"M{match.group('m').upper()}-T{match.group('t')}"


def echarts_blocking(active_milestone: str) -> bool:
    return bool(milestone_index(active_milestone) >= milestone_index("M2"))


def _last_target_result(records: list[dict[str, Any]], target: str) -> str | None:
    last: str | None = None
    for rec in records:
        if rec.get("kind") == "target" and rec.get("item") == target:
            last = str(rec.get("result", ""))
    return last


def _last_step_result(records: list[dict[str, Any]], item: str) -> str | None:
    last: str | None = None
    for rec in records:
        if rec.get("kind") == "step" and rec.get("item") == item:
            last = str(rec.get("result", ""))
    return last


def stage_junit_artifacts(junit_root: Path) -> tuple[list[Path], list[str]]:
    """
    Copy JUnit files from downloaded CI artefacts into DEFAULT_JUNIT_REL locations.
    Maps by basename only (upload-artifact may strip directory prefixes).
    """
    if not junit_root.is_dir():
        return [], []

    sources = sorted(junit_root.rglob("junit*.xml"))
    dest_to_source: dict[Path, Path] = {}
    errors: list[str] = []

    for source in sources:
        basename = source.name
        rel = BASENAME_TO_REL.get(basename)
        if rel is None:
            errors.append(f"unknown JUnit basename {basename!r}: {source}")
            continue
        if rel in dest_to_source and dest_to_source[rel] != source:
            errors.append(
                f"duplicate JUnit basename {basename!r}: {dest_to_source[rel]} and {source}"
            )
            continue
        dest_to_source[rel] = source

    if errors:
        return [], errors

    canonical: list[Path] = []
    for rel, source in sorted(dest_to_source.items()):
        dest = REPO_ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        src_resolved = source.resolve()
        dest_resolved = dest.resolve()
        if src_resolved == dest_resolved:
            errors.append(
                "JUnit source equals destination (must not): "
                f"{rel.as_posix()} ({source})"
            )
            continue
        shutil.copyfile(source, dest)
        canonical.append(dest)
    return canonical, errors


def check_job_junit_requirements(
    *,
    job_conclusions: dict[str, str | None],
    applicability: dict[str, Any],
    job_status_files: dict[str, Path],
    ci: dict[str, Any] | None = None,
) -> list[str]:
    """Applicable jobs with PASSED producers must have staged JUnit files."""
    ci = ci or load_ci_checks()
    published = {r["job"]: r for r in applicability.get("jobs", [])}
    errors: list[str] = []

    for job_name, rel_paths in JOB_JUNIT.items():
        if not rel_paths:
            continue
        if not job_make_ci(job_name, ci):
            continue
        applicable = published.get(job_name, {}).get("applicable", True)
        conclusion = job_conclusions.get(job_name)
        if not applicable or conclusion != "success":
            continue
        status_path = job_status_files.get(job_name)
        records = read_status_jsonl(status_path) if status_path else []
        for rel in rel_paths:
            basename = Path(rel).name
            target = JUNIT_PRODUCER_TARGET.get(basename)
            if target is None:
                continue
            result = _last_target_result(records, target)
            if result in ("NOT_IMPLEMENTED", "NOT_APPLICABLE"):
                if (
                    target == "e2e"
                    and basename == "junit-playwright.xml"
                    and _last_step_result(records, "e2e-harness") == "PASSED"
                ):
                    dest = REPO_ROOT / rel
                    if not dest.is_file():
                        errors.append(
                            f"{job_name}: missing JUnit {rel} after e2e-harness "
                            "reported PASSED"
                        )
                continue
            if result != "PASSED":
                continue
            dest = REPO_ROOT / rel
            if not dest.is_file():
                errors.append(
                    f"{job_name}: missing JUnit {rel} after {target} reported PASSED"
                )
    return errors


def evaluate_verdict(
    *,
    job_conclusions: dict[str, str | None],
    applicability: dict[str, Any],
    changed_files: list[str] | None,
    event_mode: str,
    status_records: list[dict[str, Any]],
    job_status_files: dict[str, Path] | None = None,
    active_milestone: str | None = None,
    ci: dict[str, Any] | None = None,
) -> SummaryOutcome:
    """Every summary rule except the card rule (ARCH-R105 card scope)."""
    ci = ci or load_ci_checks()
    active = active_milestone or read_active_milestone(SPEC_SET)
    outcome = SummaryOutcome(success=True)
    job_status_files = job_status_files or {}

    published = {r["job"]: r for r in applicability.get("jobs", [])}
    recomputed = compute_applicability(
        changed_files=changed_files,
        event_mode=event_mode,
        ci=ci,
    )
    recomputed_map = {r["job"]: r for r in recomputed["jobs"]}

    for job_name, pub in published.items():
        rec = recomputed_map.get(job_name)
        if rec is None:
            outcome.success = False
            outcome.errors.append(f"missing recomputed record for {job_name}")
            continue
        if pub["applicable"] != rec["applicable"]:
            outcome.success = False
            outcome.errors.append(
                f"applicability disagreement for {job_name}: "
                f"published={pub['applicable']} recomputed={rec['applicable']}"
            )

    summary_needs = next(j for j in ci["jobs"] if j["name"] == "ci/summary")["needs"]
    all_tracked_jobs = ["ci/changes", *summary_needs]

    for need in all_tracked_jobs:
        if need not in job_conclusions:
            outcome.success = False
            outcome.errors.append(f"missing job result for {need}")

    changes_conclusion = job_conclusions.get("ci/changes")
    if changes_conclusion != "success":
        outcome.success = False
        outcome.errors.append(f"ci/changes: conclusion {changes_conclusion!r}")

    for job_name in all_tracked_jobs:
        needs_status = job_make_ci(job_name, ci) or job_name in JOBS_REQUIRING_STATUS
        if not needs_status:
            continue
        conclusion = job_conclusions.get(job_name)
        applicable = published.get(job_name, {}).get("applicable", True)
        if not applicable or conclusion == "skipped":
            continue
        status_path = job_status_files.get(job_name)
        if status_path is None or not status_path.is_file():
            outcome.success = False
            outcome.errors.append(
                f"missing status report for applicable job {job_name}"
            )

    for job in ci["jobs"]:
        name = job["name"]
        if name in ("ci/changes", "ci/summary", "ci/quarantine"):
            continue
        conclusion = job_conclusions.get(name)
        applicable = published.get(name, {}).get("applicable", True)
        blocking = job.get("blocking", True)
        if isinstance(blocking, str) and blocking.startswith("from"):
            blocking = echarts_blocking(active) if name == "ci/echarts-gate" else True

        if conclusion is None:
            if applicable:
                outcome.success = False
                outcome.errors.append(f"{name}: no result while applicable")
            continue

        if conclusion == "skipped":
            if applicable:
                outcome.success = False
                outcome.errors.append(f"{name}: skipped while applicable")
            continue

        if conclusion in FAILING_CONCLUSIONS:
            if blocking:
                outcome.success = False
                outcome.errors.append(f"{name}: conclusion {conclusion}")
            else:
                outcome.warnings.append(f"{name}: non-blocking {conclusion}")
            continue

        if conclusion not in BLOCKING_CONCLUSIONS and blocking:
            outcome.success = False
            outcome.errors.append(f"{name}: unexpected conclusion {conclusion!r}")

    targets_active_from = _target_active_from_map()
    for rec in status_records:
        result = rec.get("result")
        if result == "FAILED":
            outcome.success = False
            outcome.errors.append(f"status.jsonl FAILED: {rec.get('item')}")
        if result == "NOT_IMPLEMENTED":
            item = str(rec.get("item", ""))
            if rec.get("kind") == "step":
                active_from = rec.get("milestone") or rec.get("active_from")
            else:
                active_from = targets_active_from.get(item) or rec.get("active_from")
            if active_from and milestone_index(str(active_from)) < milestone_index(
                active
            ):
                outcome.success = False
                outcome.errors.append(
                    f"NOT_IMPLEMENTED outside build window: {item} ({active_from})"
                )
        if result == "SKIPPED" and not rec.get("reason"):
            outcome.success = False
            outcome.errors.append(f"SKIPPED without reason: {rec.get('item')}")

    return outcome


def evaluate_card_rule(*, card: str, junit_paths: list[Path]) -> SummaryOutcome:
    outcome = SummaryOutcome(success=True)
    try:
        _, errors, exit_code = build_report(
            REPO_ROOT, junit_paths=junit_paths, card=card
        )
    except ValueError as exc:
        outcome.success = False
        outcome.errors.append(str(exc))
        return outcome
    if exit_code != 0:
        outcome.success = False
        for err in errors:
            outcome.errors.append(f"trace CARD={card}: {err}")
        if not errors:
            outcome.errors.append(f"trace-report CARD={card} failed")
    return outcome


def write_verdict_json(outcome: SummaryOutcome, path: Path = VERDICT_JSON) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "success": outcome.success,
                "errors": outcome.errors,
                "warnings": outcome.warnings,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_staged_junit_manifest(junit_paths: list[Path]) -> Path:
    STAGED_JUNIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    rels = [p.relative_to(REPO_ROOT).as_posix() for p in junit_paths]
    STAGED_JUNIT_JSON.write_text(json.dumps(rels, indent=2) + "\n", encoding="utf-8")
    return STAGED_JUNIT_JSON


def run_live_summary_test(
    *, staged_junit_json: Path | None = None
) -> tuple[int, Path | None]:
    """AT-M0-T07-02 — runs only on GitHub Actions."""
    if os.environ.get("GITHUB_ACTIONS", "").strip().lower() != "true":
        return 0, None
    LIVE_JUNIT.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CENOMI_CI_SUMMARY_LIVE"] = "1"
    if staged_junit_json is not None and staged_junit_json.is_file():
        env["CENOMI_CI_STAGED_JUNIT_JSON"] = str(staged_junit_json)
    proc = subprocess.run(
        [
            "uv",
            "run",
            "--project",
            "backend",
            "pytest",
            "tests/tooling/ci/test_live_run.py::test_at_m0_t07_02_live_summary",
            f"--junitxml={LIVE_JUNIT}",
            "-q",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
    )
    return proc.returncode, LIVE_JUNIT if LIVE_JUNIT.is_file() else None


def write_card_trace_artifacts(
    *, card: str, junit_paths: list[Path], output_dir: Path = SUMMARY_REPORT_DIR
) -> SummaryOutcome:
    outcome = SummaryOutcome(success=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        payload, errors, exit_code = build_report(
            REPO_ROOT, junit_paths=junit_paths, card=card, output_dir=output_dir
        )
    except ValueError as exc:
        outcome.success = False
        outcome.errors.append(str(exc))
        return outcome

    from scripts.trace.report import _markdown

    (output_dir / "trace.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "trace.md").write_text(_markdown(payload), encoding="utf-8")
    if exit_code != 0:
        outcome.success = False
        outcome.errors.extend(errors)
    return outcome


def bootstrap_trace_lines(junit_paths: list[Path]) -> list[str]:
    lines = ["", "## EXC-001 C5 (a) — bootstrap card trace", ""]
    for card in BOOTSTRAP_CARDS:
        try:
            payload, errors, code = build_report(
                REPO_ROOT, junit_paths=junit_paths, card=card
            )
        except ValueError as exc:
            lines.append(f"- `{card}`: **FAILED** ({exc})")
            continue
        tests = payload.get("acceptanceTests")
        if not isinstance(tests, list):
            tests = []
        failed = [
            t for t in tests if isinstance(t, dict) and t.get("result") != "PASSED"
        ]
        if code != 0 or failed:
            lines.append(f"- `{card}`: **FAILED** ({len(failed)} non-PASSED AT(s))")
            for err in errors[:5]:
                lines.append(f"  - {err}")
        else:
            lines.append(f"- `{card}`: **PASSED** ({len(tests)} AT(s))")
    return lines


def security_evidence_line(job_conclusions: dict[str, str | None]) -> list[str]:
    conclusion = job_conclusions.get("ci/security", "—")
    return [
        "",
        "## EXC-002 C5 (a) — ci/security",
        "",
        f"- `ci/security` conclusion: **{conclusion}**",
    ]


def render_summary_markdown(
    *,
    sha: str,
    spec_version: str,
    active_milestone: str,
    applicability: dict[str, Any],
    job_conclusions: dict[str, str | None],
    status_records: list[dict[str, Any]],
    outcome: SummaryOutcome,
    junit_paths: list[Path] | None = None,
) -> str:
    reports = _load_reports_module()
    lines = [
        "# CI summary",
        "",
        f"- Commit: `{sha}`",
        f"- Specification set: `{spec_version}`",
        f"- Active milestone: `{active_milestone}`",
        "- Dataset: not seeded",
        "",
        "## Jobs",
        "",
        "| Job | Applicable | Conclusion |",
        "|---|---|---|",
    ]
    for rec in applicability.get("jobs", []):
        name = rec["job"]
        if name == "ci/changes":
            continue
        applicable = rec["applicable"]
        conclusion = job_conclusions.get(name, "—")
        lines.append(f"| `{name}` | {applicable} | {conclusion} |")

    lines.extend(["", "## Target results", ""])
    for rec in status_records:
        lines.append(
            f"- `{rec.get('item')}`: **{rec.get('result')}** — {rec.get('reason', '')}"
        )

    if junit_paths:
        lines.extend(bootstrap_trace_lines(junit_paths))
    lines.extend(security_evidence_line(job_conclusions))

    if reports is not None and hasattr(reports, "append_ci_summary_sections"):
        lines.extend(reports.append_ci_summary_sections(REPO_ROOT / "tests/reports"))

    lines.extend(["", "## Outcome", ""])
    if outcome.success:
        lines.append("**PASSED** — all blocking checks satisfied.")
    else:
        lines.append("**FAILED**")
        for err in outcome.errors:
            lines.append(f"- {err}")
    for warn in outcome.warnings:
        lines.append(f"- (warning) {warn}")
    lines.append("")
    return "\n".join(lines)


def evaluate(
    *,
    job_conclusions: dict[str, str | None],
    applicability: dict[str, Any],
    changed_files: list[str] | None,
    event_mode: str,
    head_branch: str | None,
    status_records: list[dict[str, Any]],
    job_status_files: dict[str, Path] | None = None,
    active_milestone: str | None = None,
    ci: dict[str, Any] | None = None,
    junit_paths: list[Path] | None = None,
) -> SummaryOutcome:
    """Full summary evaluation including card rule (for unit tests)."""
    verdict = evaluate_verdict(
        job_conclusions=job_conclusions,
        applicability=applicability,
        changed_files=changed_files,
        event_mode=event_mode,
        status_records=status_records,
        job_status_files=job_status_files,
        active_milestone=active_milestone,
        ci=ci,
    )
    card = parse_card_from_branch(head_branch)
    if not card:
        return verdict
    paths = junit_paths or []
    card_out = evaluate_card_rule(card=card, junit_paths=paths)
    return _merge_outcomes(verdict, card_out)


def _merge_outcomes(a: SummaryOutcome, b: SummaryOutcome) -> SummaryOutcome:
    return SummaryOutcome(
        success=a.success and b.success,
        errors=[*a.errors, *b.errors],
        warnings=[*a.warnings, *b.warnings],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate CI summary.")
    parser.add_argument("--applicability", type=Path, required=True)
    parser.add_argument(
        "--jobs-json",
        type=Path,
        help="JSON object mapping job name to conclusion",
    )
    parser.add_argument("--event", default="pull_request")
    parser.add_argument("--head-branch", default="")
    parser.add_argument("--sha", default=os.environ.get("GITHUB_SHA", "local"))
    parser.add_argument("--step-summary", type=Path)
    parser.add_argument(
        "--status-artifacts-dir",
        type=Path,
        default=REPO_ROOT / "tests/reports/ci/artifacts",
        help="Directory of downloaded status-* artefacts",
    )
    parser.add_argument(
        "--junit-artifacts-dir",
        type=Path,
        default=REPO_ROOT / "tests/reports/ci/artifacts",
        help="Directory of downloaded CI artefacts (junit-* subfolders)",
    )
    args = parser.parse_args()

    try:
        applicability = load_required_json(args.applicability, "applicability")
    except (FileNotFoundError, ValueError) as exc:
        print(f"ci/summary: FAILED — {exc}", file=sys.stderr)
        return 1

    if args.jobs_json is None:
        print("ci/summary: FAILED — --jobs-json is required", file=sys.stderr)
        return 1
    try:
        job_conclusions_raw = load_required_json(args.jobs_json, "job-conclusions")
    except (FileNotFoundError, ValueError) as exc:
        print(f"ci/summary: FAILED — {exc}", file=sys.stderr)
        return 1

    job_conclusions: dict[str, str | None] = {
        str(k): (None if v is None else str(v)) for k, v in job_conclusions_raw.items()
    }

    event_mode = args.event
    stored_files = applicability.get("changed_files")
    if event_mode == "pull_request":
        changed_files = stored_files
    else:
        changed_files = stored_files if stored_files is not None else []

    spec_text = SPEC_SET.read_text(encoding="utf-8")
    version_match = re.search(r'^version:\s*["\']?([^"\']+)', spec_text, re.MULTILINE)
    spec_version = version_match.group(1) if version_match else "unknown"
    active = read_active_milestone(SPEC_SET)

    job_status_files = discover_job_status_files(args.status_artifacts_dir)

    junit_paths, junit_errors = stage_junit_artifacts(args.junit_artifacts_dir)
    if junit_errors:
        for err in junit_errors:
            print(f"ci/summary: FAILED — {err}", file=sys.stderr)
        return 1

    junit_req_errors = check_job_junit_requirements(
        job_conclusions=job_conclusions,
        applicability=applicability,
        job_status_files=job_status_files,
    )
    if junit_req_errors:
        for err in junit_req_errors:
            print(f"ci/summary: FAILED — {err}", file=sys.stderr)
        return 1

    staged_junit_json = write_staged_junit_manifest(junit_paths)
    status_paths = list(job_status_files.values())
    if STATUS_JSONL.is_file():
        status_paths.append(STATUS_JSONL)
    status_records = merge_status_records(status_paths)

    verdict = evaluate_verdict(
        job_conclusions=job_conclusions,
        applicability=applicability,
        changed_files=changed_files,
        event_mode=event_mode,
        status_records=status_records,
        job_status_files=job_status_files,
        active_milestone=active,
    )
    write_verdict_json(verdict)

    live_code, live_junit = run_live_summary_test(staged_junit_json=staged_junit_json)
    if live_junit is not None and live_junit not in junit_paths:
        junit_paths = [*junit_paths, live_junit]
        write_staged_junit_manifest(junit_paths)

    outcome = verdict
    if live_code != 0:
        outcome = _merge_outcomes(
            outcome,
            SummaryOutcome(
                success=False,
                errors=["AT-M0-T07-02 live summary test failed"],
            ),
        )

    card = parse_card_from_branch(args.head_branch or None)
    if card:
        card_out = evaluate_card_rule(card=card, junit_paths=junit_paths)
        outcome = _merge_outcomes(outcome, card_out)
        trace_out = write_card_trace_artifacts(card=card, junit_paths=junit_paths)
        outcome = _merge_outcomes(outcome, trace_out)

    md = render_summary_markdown(
        sha=args.sha,
        spec_version=spec_version,
        active_milestone=active,
        applicability=applicability,
        job_conclusions=job_conclusions,
        status_records=status_records,
        outcome=outcome,
        junit_paths=junit_paths,
    )
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.write_text(md, encoding="utf-8")

    if args.step_summary:
        args.step_summary.write_text(md, encoding="utf-8")

    if outcome.success:
        print("ci/summary: PASSED")
        return 0
    for err in outcome.errors:
        print(f"ci/summary: FAILED — {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
