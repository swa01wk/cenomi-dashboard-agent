"""Render DEVENV §5.2 and §7.2 tables from engineering YAML (M0-T10)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKE_TARGETS = REPO_ROOT / "specs/engineering/make_targets.yaml"
CI_CHECKS = REPO_ROOT / "specs/engineering/ci_checks.yaml"
DEVENV = REPO_ROOT / "docs/architecture/DEVELOPMENT_ENVIRONMENT.md"

GROUP_LABELS: dict[str, str] = {
    "environment": "Environment and development",
    "database": "Database",
    "synthetic_data": "Synthetic data",
    "backend": "Backend",
    "frontend": "Frontend",
    "agent": "Agent",
    "contracts_and_integration": "Contracts and integration",
    "verification": "Verification",
    "full_validation": "Full validation",
}


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _format_args(args: list[dict[str, Any]]) -> str:
    if not args:
        return "—"
    parts: list[str] = []
    for arg in args:
        name = arg.get("name", "")
        default = arg.get("default", "")
        if default in ("", None):
            parts.append(f"`{name}` (—)")
        else:
            parts.append(f"`{name}` ({default})")
    return "; ".join(parts)


def _format_ci_jobs(jobs: list[str]) -> str:
    if not jobs:
        return "—"
    if len(jobs) == 1:
        return f"`{jobs[0]}`"
    return ", ".join(f"`{j}`" for j in jobs)


def _format_in_check(in_check: bool, name: str) -> str:
    if not in_check:
        return "no"
    if name == "backend-test":
        return "yes (`SUITE=unit`)"
    return "yes"


def _target_summary(target: dict[str, Any]) -> str:
    summary = str(target["summary"])
    safety = target.get("safety")
    if safety:
        summary = f"{summary} *Safety:* {safety}"
    return summary


def render_make_targets(data: dict[str, Any]) -> str:
    groups: list[str] = data["groups"]
    targets: list[dict[str, Any]] = data["targets"]
    by_group: dict[str, list[dict[str, Any]]] = {g: [] for g in groups}
    for target in targets:
        by_group[target["group"]].append(target)

    lines: list[str] = []
    header = (
        "| Target | Active from | Destructive | Summary | Arguments (default) | "
        "Failure | In `check` | CI jobs |"
    )
    sep = "|---|---|---|---|---|---|---|---|"

    first = True
    for group in groups:
        if not first:
            lines.append("")
        first = False
        lines.append(f"**{GROUP_LABELS[group]}**")
        lines.append("")
        lines.append(header)
        lines.append(sep)
        for target in by_group[group]:
            destructive = "**yes**" if target.get("destructive") else "no"
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{target['name']}`",
                        target["active_from"],
                        destructive,
                        _cell(_target_summary(target)),
                        _format_args(target.get("args") or []),
                        _cell(str(target.get("failure", ""))),
                        _format_in_check(bool(target.get("in_check")), target["name"]),
                        _format_ci_jobs(target.get("ci_jobs") or []),
                    ]
                )
                + " |"
            )

    lines.append("")
    lines.append(
        "Full behaviour steps and prerequisites per target are in the YAML "
        "(`behaviour`, `prerequisites`)."
    )
    return "\n".join(lines) + "\n"


def _format_needs(needs: list[str]) -> str:
    if not needs:
        return "—"
    return ", ".join(f"`{n}`" for n in needs)


def _format_job_targets(job: dict[str, Any]) -> str:
    targets = job.get("targets") or []
    if targets:
        return ", ".join(f"`{t}`" for t in targets)
    if job.get("extra_steps"):
        return "extra steps only"
    return "—"


def _format_blocking(blocking: Any) -> str:
    if blocking is True:
        return "yes"
    if blocking is False:
        return "no"
    return str(blocking)


def render_ci_jobs(data: dict[str, Any]) -> str:
    header = (
        "| Job (stable name) | Runs when (PR) | Needs | Make targets | "
        "Timeout (min) | Blocking | Purpose |"
    )
    sep = "|---|---|---|---|---|---|---|"
    lines = [header, sep]
    for job in data["jobs"]:
        runs_when = job.get("runs_when", "")
        if runs_when != "always" and not str(runs_when).startswith('"'):
            runs_when = f"`{runs_when}`"
        else:
            runs_when = f"`{runs_when}`"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{job['name']}`",
                    runs_when,
                    _format_needs(job.get("needs") or []),
                    _format_job_targets(job),
                    str(job.get("timeout_minutes", "")),
                    _format_blocking(job.get("blocking")),
                    _cell(str(job.get("purpose", ""))),
                ]
            )
            + " |"
        )
    lines.append("")
    required = ", ".join(f"`{c}`" for c in data.get("required_checks", []))
    lines.append(f"Required check: {required}. Runner `{data.get('runner', '')}`.")
    return "\n".join(lines) + "\n"


def render_all() -> tuple[str, str]:
    make_data = yaml.safe_load(MAKE_TARGETS.read_text(encoding="utf-8"))
    ci_data = yaml.safe_load(CI_CHECKS.read_text(encoding="utf-8"))
    # Committed blocks include a leading newline after the GENERATED marker.
    return (
        "\n" + render_make_targets(make_data),
        "\n" + render_ci_jobs(ci_data),
    )


def extract_generated_block(doc: str, marker: str) -> str:
    start = doc.index(f"<!-- BEGIN GENERATED: {marker}")
    end = doc.index(f"<!-- END GENERATED: {marker}")
    inner_start = doc.index("-->", start) + 3
    return doc[inner_start:end]


def check_drift() -> list[str]:
    doc = DEVENV.read_text(encoding="utf-8")
    make_rendered, ci_rendered = render_all()
    errors: list[str] = []
    for marker, rendered in (("make_targets", make_rendered), ("ci_jobs", ci_rendered)):
        committed = extract_generated_block(doc, marker)
        if committed != rendered:
            errors.append(
                f"{DEVENV}: generated block {marker} drift "
                f"(committed {len(committed)} bytes, rendered {len(rendered)} bytes)"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if committed DEVENV tables differ from rendered output",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Replace generated blocks in DEVELOPMENT_ENVIRONMENT.md (not used in M0)",
    )
    args = parser.parse_args()
    if args.check:
        errors = check_drift()
        for err in errors:
            print(err, file=sys.stderr)
        return 1 if errors else 0
    make_out, ci_out = render_all()
    print(make_out, end="")
    print("---")
    print(ci_out, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
