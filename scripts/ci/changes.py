"""Compute CI job applicability from changed paths (DEVENV-R047–R049)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml

from scripts.ci._paths import categories_for_path, normalize_path, path_matches

CI_CHECKS = REPO_ROOT / "specs/engineering/ci_checks.yaml"
APPLICABILITY_PATH = REPO_ROOT / "tests/reports/ci/applicability.json"

ALWAYS_JOBS = frozenset(
    {
        "ci/changes",
        "ci/specs",
        "ci/security",
        "ci/quarantine",
        "ci/summary",
    }
)


def load_ci_checks(path: Path = CI_CHECKS) -> dict[str, Any]:
    return cast(dict[str, Any], yaml.safe_load(path.read_text(encoding="utf-8")))


def job_make_ci(job_name: str, ci: dict[str, Any] | None = None) -> bool:
    ci = ci or load_ci_checks()
    for job in ci["jobs"]:
        if job["name"] == job_name:
            return bool(job.get("make_ci"))
    return False


def job_output_key(job_name: str) -> str:
    return "applicable_" + job_name.replace("/", "_").replace("-", "_")


def _is_docs_only_candidate(path: str, candidates: list[str]) -> bool:
    norm = normalize_path(path)
    return any(path_matches(norm, glob) for glob in candidates)


def classify_files(
    changed_files: list[str],
    ci: dict[str, Any],
) -> tuple[set[str], bool, bool]:
    """Return (categories_union, docs_only, force_all_jobs)."""
    path_categories = ci["path_categories"]
    docs_candidates = path_categories["docs_only_candidates"]
    shared_globs = path_categories["shared_contract"]

    categories: set[str] = set()
    force_all = False

    if not changed_files:
        return categories, True, False

    all_docs_only = True
    for raw in changed_files:
        path = normalize_path(raw)
        if not path:
            continue
        if any(path_matches(path, g) for g in shared_globs):
            force_all = True
        file_cats = categories_for_path(path, path_categories)
        if file_cats:
            categories |= file_cats
        elif _is_docs_only_candidate(path, docs_candidates):
            pass
        else:
            force_all = True
        if not _is_docs_only_candidate(path, docs_candidates):
            all_docs_only = False

    return categories, all_docs_only, force_all


def parse_runs_when(expr: str, categories: set[str], docs_only: bool) -> bool:
    expr = expr.strip()
    if expr == "always":
        return True
    if expr == "not docs_only":
        return not docs_only

    parts = [p.strip() for p in re.split(r"\s+or\s+", expr)]
    for part in parts:
        if part in categories:
            return True
    return False


def compute_applicability(
    *,
    changed_files: list[str] | None,
    event_mode: str,
    ci: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ci = ci or load_ci_checks()
    jobs = ci["jobs"]

    if event_mode in ("push", "workflow_call", "all"):
        records = []
        for job in jobs:
            records.append(
                {
                    "job": job["name"],
                    "applicable": True,
                    "categories": sorted({"all_paths"}),
                    "runs_when": job.get("runs_when", "always"),
                    "reason": event_mode,
                }
            )
        return {
            "jobs": records,
            "docs_only": False,
            "force_all": True,
            "changed_files": [],
        }

    if changed_files is None:
        records = []
        for job in jobs:
            records.append(
                {
                    "job": job["name"],
                    "applicable": True,
                    "categories": [],
                    "runs_when": job.get("runs_when", "always"),
                    "reason": "uncomputable_diff",
                }
            )
        return {
            "jobs": records,
            "docs_only": False,
            "force_all": True,
            "changed_files": None,
        }

    categories, docs_only, force_all = classify_files(changed_files, ci)
    records = []
    for job in jobs:
        name = job["name"]
        runs_when = job.get("runs_when", "always")
        if force_all:
            applicable = True
            reason = "shared_contract_or_uncategorized"
        elif name in ALWAYS_JOBS:
            applicable = True
            reason = "always_run"
        else:
            applicable = parse_runs_when(runs_when, categories, docs_only)
            reason = "runs_when"
        records.append(
            {
                "job": name,
                "applicable": applicable,
                "categories": sorted(categories),
                "runs_when": runs_when,
                "reason": reason,
            }
        )
    return {
        "jobs": records,
        "docs_only": docs_only,
        "force_all": force_all,
        "changed_files": changed_files,
    }


def git_changed_files(base_ref: str, head_ref: str = "HEAD") -> list[str] | None:
    try:
        subprocess.run(
            ["git", "fetch", "--no-tags", "--depth", "1", "origin", base_ref],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
        )
        merge_base = subprocess.run(
            ["git", "merge-base", head_ref, f"origin/{base_ref}"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        diff = subprocess.run(
            ["git", "diff", "--name-only", f"{merge_base}...{head_ref}"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return [line for line in diff.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        return None


def write_github_outputs(records: list[dict[str, Any]], output_path: Path) -> None:
    lines: list[str] = []
    for rec in records:
        key = job_output_key(rec["job"])
        val = "true" if rec["applicable"] else "false"
        lines.append(f"{key}={val}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute CI job applicability.")
    parser.add_argument(
        "--event",
        choices=("pull_request", "push", "workflow_call", "all"),
        default="pull_request",
    )
    parser.add_argument("--base-ref", default="main")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument(
        "--files",
        nargs="*",
        help="Changed paths (for tests). Omit on PR to use git diff.",
    )
    parser.add_argument(
        "--write-json",
        type=Path,
        default=APPLICABILITY_PATH,
    )
    parser.add_argument(
        "--github-output",
        type=Path,
        help="Write GITHUB_OUTPUT key=value lines (for workflows).",
    )
    args = parser.parse_args()

    changed: list[str] | None
    if args.files is not None:
        changed = list(args.files)
        event_mode = "pull_request"
    elif args.event == "pull_request":
        changed = git_changed_files(args.base_ref, args.head_ref)
        event_mode = "pull_request"
    else:
        changed = []
        event_mode = args.event

    result = compute_applicability(changed_files=changed, event_mode=event_mode)
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if args.github_output:
        write_github_outputs(result["jobs"], args.github_output)

    for rec in result["jobs"]:
        print(f"{rec['job']}: applicable={rec['applicable']} reason={rec['reason']}")

    from scripts.make.report import append_status, read_active_milestone

    APPLICABILITY_PATH.parent.mkdir(parents=True, exist_ok=True)
    append_status(
        item="ci/changes",
        result="PASSED",
        rule="path_classification",
        reason="wrote applicability.json",
        milestone=read_active_milestone(),
        duration_ms=0,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
