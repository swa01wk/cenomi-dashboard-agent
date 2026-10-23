"""Secret scan, dependency audit and licence report (M0-T10)."""

from __future__ import annotations

import importlib.metadata
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ADR-0003 §4: psycopg 3 LGPL-3.0 is accepted unmodified.
ACCEPTED_LGPL = {"psycopg", "psycopg-binary", "psycopg2", "psycopg2-binary"}
GPL_FAMILY = re.compile(r"(^GPL|[\s-]GPL|AGPL)", re.IGNORECASE)


def _run(
    cmd: list[str], *, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    print(f"+ {' '.join(cmd)}", flush=True)
    return subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def run_gitleaks() -> int:
    in_ci = os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
    cmd = ["gitleaks", "detect", "--redact", "--source", str(REPO_ROOT)]
    if not in_ci:
        cmd.append("--no-git")
    proc = _run(cmd)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


def run_pip_audit() -> int:
    proc = _run(["uv", "run", "pip-audit"], cwd=REPO_ROOT / "backend")
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


def run_pnpm_audit() -> int:
    proc = _run(["pnpm", "audit", "--audit-level", "high"])
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


def _python_licences() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name") or dist.name
        licence = dist.metadata.get("License") or ""
        if not licence:
            classifiers = dist.metadata.get_all("Classifier") or []
            for c in classifiers:
                if c.startswith("License"):
                    licence = c.split(":", 1)[-1].strip()
                    break
        rows.append((name, licence or "unknown"))
    return sorted(rows, key=lambda r: r[0].lower())


def _node_licences() -> list[tuple[str, str]]:
    proc = _run(["pnpm", "licenses", "list", "--json"])
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return []
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return []
    rows: list[tuple[str, str]] = []
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                rows.append(
                    (str(item.get("name", "")), str(item.get("license", "unknown")))
                )
    elif isinstance(payload, dict):
        for name, meta in payload.items():
            if isinstance(meta, dict):
                rows.append((name, str(meta.get("license", "unknown"))))
            else:
                rows.append((name, str(meta)))
    return sorted(rows, key=lambda r: r[0].lower())


def _licence_violations(rows: list[tuple[str, str]]) -> list[str]:
    violations: list[str] = []
    for name, licence in rows:
        if name in ACCEPTED_LGPL and "LGPL" in licence.upper():
            continue
        if GPL_FAMILY.search(licence):
            violations.append(f"{name}: {licence}")
    return violations


def run_licence_report() -> int:
    py_rows = _python_licences()
    node_rows = _node_licences()
    report_path = REPO_ROOT / "tests/reports/security/licenses.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Python packages", ""]
    for name, licence in py_rows:
        lines.append(f"{name}\t{licence}")
    lines.extend(["", "# Node packages", ""])
    for name, licence in node_rows:
        lines.append(f"{name}\t{licence}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Licence report: {report_path.relative_to(REPO_ROOT)}")

    violations = _licence_violations(py_rows) + _licence_violations(node_rows)
    for item in violations:
        print(f"LICENSE: {item}", file=sys.stderr)
    return 1 if violations else 0


def main() -> int:
    code = 0
    for step, fn in (
        ("gitleaks", run_gitleaks),
        ("pip-audit", run_pip_audit),
        ("pnpm-audit", run_pnpm_audit),
        ("licences", run_licence_report),
    ):
        rc = fn()
        if rc != 0:
            print(f"FAILED: security-check — {step} exited {rc}", file=sys.stderr)
            code = rc
    if code == 0:
        print("PASSED: security-check — scan, audit and licences clean")
    return code


if __name__ == "__main__":
    sys.exit(main())
