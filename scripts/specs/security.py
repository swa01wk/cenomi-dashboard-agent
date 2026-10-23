"""Secret scan, dependency audit and licence report (M0-T10)."""

from __future__ import annotations

import importlib.metadata
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ADR-0003 §4: psycopg 3 LGPL-3.0 is accepted unmodified.
ACCEPTED_LGPL = {"psycopg", "psycopg-binary", "psycopg2", "psycopg2-binary"}
GPL_FAMILY = re.compile(r"(^GPL|[\s-]GPL|AGPL)", re.IGNORECASE)
HIGH_SEVERITIES = frozenset({"HIGH", "CRITICAL"})


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run(
    cmd: list[str], *, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    root = repo_root()
    print(f"+ {' '.join(cmd)}", flush=True)
    return subprocess.run(
        cmd,
        cwd=cwd or root,
        capture_output=True,
        text=True,
        check=False,
    )


def pip_audit_violations(payload: Any) -> list[str]:
    """Return package names that fail the pip-audit policy (high/critical + fix)."""
    violations: list[str] = []
    if not isinstance(payload, dict):
        return violations
    for dep in payload.get("dependencies") or []:
        if not isinstance(dep, dict):
            continue
        name = str(dep.get("name", ""))
        for vuln in dep.get("vulns") or []:
            if not isinstance(vuln, dict):
                continue
            severity = str(vuln.get("severity", "")).upper()
            fix_versions = vuln.get("fix_versions") or []
            if severity in HIGH_SEVERITIES and fix_versions:
                violations.append(name)
                break
    return sorted(set(violations))


def run_gitleaks() -> int:
    root = repo_root()
    in_ci = os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
    cmd = ["gitleaks", "detect", "--redact", "--source", str(root)]
    if not in_ci:
        cmd.append("--no-git")
    proc = _run(cmd)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


def run_pip_audit() -> int:
    proc = _run(
        ["uv", "run", "pip-audit", "--format", "json"],
        cwd=repo_root() / "backend",
    )
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    if proc.returncode != 0:
        return proc.returncode
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        print("pip-audit: invalid JSON output", file=sys.stderr)
        return 1
    violations = pip_audit_violations(payload)
    for name in violations:
        print(f"PIP-AUDIT: {name} has high/critical fixable vulnerability", file=sys.stderr)
    return 1 if violations else 0


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
    root = repo_root()
    py_rows = _python_licences()
    node_rows = _node_licences()
    report_path = root / "tests/reports/security/licenses.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Python packages", ""]
    for name, licence in py_rows:
        lines.append(f"{name}\t{licence}")
    lines.extend(["", "# Node packages", ""])
    for name, licence in node_rows:
        lines.append(f"{name}\t{licence}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Licence report: {report_path.relative_to(root)}")

    violations = _licence_violations(py_rows) + _licence_violations(node_rows)
    for item in violations:
        print(f"LICENSE: {item}", file=sys.stderr)
    return 1 if violations else 0


def main() -> int:
    if str(repo_root()) not in sys.path:
        sys.path.insert(0, str(repo_root()))
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
