"""Validate specifications and engineering metadata (M0-T10)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.specs.check_lib import SUB_CHECKS, check_gate_mode
from scripts.specs.findings import Finding


def run_checks(
    repo: Path,
    *,
    gate: str = "",
    only: set[str] | None = None,
) -> tuple[list[Finding], list[str]]:
    notes: list[str] = []
    findings: list[Finding] = []
    workflow = repo / ".github/workflows/ci.yml"
    if not workflow.is_file():
        notes.append(
            "NOT_APPLICABLE: ci_jobs — .github/workflows/ci.yml not present on this branch"
        )

    for name, fn in SUB_CHECKS.items():
        if only is not None and name not in only:
            continue
        if name == "ci_jobs" and not workflow.is_file():
            continue
        try:
            findings.extend(fn(repo))
        except Exception as exc:
            print(f"specs-check: {name} crashed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc

    if gate:
        try:
            findings.extend(check_gate_mode(repo, gate))
        except Exception as exc:
            print(f"specs-check: gate_mode crashed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc

    return findings, notes


def main() -> int:
    gate = os.environ.get("GATE", "").strip()
    findings, notes = run_checks(REPO_ROOT, gate=gate)
    for note in notes:
        print(note)
    for finding in findings:
        print(finding.format())
    if findings:
        return 1
    print("PASSED: specs-check — all sub-checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
