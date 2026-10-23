"""Aggregate CI job results and enforce fail-closed rules (DEVENV-R020, R050)."""

from __future__ import annotations

import argparse
import json
import os
import re
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

from scripts.ci.changes import (  # type: ignore[import-not-found]
    compute_applicability,
    job_make_ci,
    load_ci_checks,
)
from scripts.ci.job_slug import artifact_slug_to_job  # type: ignore[import-not-found]
from scripts.make.report import (  # type: ignore[import-not-found]
    milestone_index,
    read_active_milestone,
)

SPEC_SET = REPO_ROOT / "specs/engineering/spec_set.yaml"
SUMMARY_MD = REPO_ROOT / "tests/reports/ci-summary.md"
STATUS_JSONL = REPO_ROOT / "tests/reports/status.jsonl"

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
        from scripts.ci import reports as reports_mod  # type: ignore[import-not-found]

        return cast(ModuleType, reports_mod)
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


def job_slug(name: str) -> str:
    return name.removeprefix("ci/")


def parse_card_from_branch(branch: str | None) -> str | None:
    if not branch:
        return None
    match = CARD_BRANCH.match(branch.strip())
    if not match:
        return None
    return f"M{match.group('m').upper()}-T{match.group('t')}"


def echarts_blocking(active_milestone: str) -> bool:
    return bool(milestone_index(active_milestone) >= milestone_index("M2"))


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
) -> SummaryOutcome:
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
        if not job_make_ci(job_name, ci):
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
            active_from = targets_active_from.get(item) or rec.get("active_from")
            if active_from and milestone_index(active_from) < milestone_index(active):
                outcome.success = False
                outcome.errors.append(
                    f"NOT_IMPLEMENTED outside build window: {item} ({active_from})"
                )
        if result == "SKIPPED" and not rec.get("reason"):
            outcome.success = False
            outcome.errors.append(f"SKIPPED without reason: {rec.get('item')}")

    card = parse_card_from_branch(head_branch)
    if card:
        env = os.environ.copy()
        env["CARD"] = card
        proc = subprocess.run(
            ["make", "trace-report"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            outcome.success = False
            outcome.errors.append(f"trace-report CARD={card} failed")

    return outcome


def render_summary_markdown(
    *,
    sha: str,
    spec_version: str,
    active_milestone: str,
    applicability: dict[str, Any],
    job_conclusions: dict[str, str | None],
    status_records: list[dict[str, Any]],
    outcome: SummaryOutcome,
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

    if reports is not None and hasattr(reports, "append_ci_summary_sections"):
        lines.extend(reports.append_ci_summary_sections())

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
        default=REPO_ROOT / "tests/reports/ci/status-artifacts",
        help="Directory of downloaded status-* artifacts",
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
    status_paths = list(job_status_files.values())
    if STATUS_JSONL.is_file():
        status_paths.append(STATUS_JSONL)
    status_records = merge_status_records(status_paths)

    outcome = evaluate(
        job_conclusions=job_conclusions,
        applicability=applicability,
        changed_files=changed_files,
        event_mode=event_mode,
        head_branch=args.head_branch or None,
        status_records=status_records,
        job_status_files=job_status_files,
        active_milestone=active,
    )

    md = render_summary_markdown(
        sha=args.sha,
        spec_version=spec_version,
        active_milestone=active,
        applicability=applicability,
        job_conclusions=job_conclusions,
        status_records=status_records,
        outcome=outcome,
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
