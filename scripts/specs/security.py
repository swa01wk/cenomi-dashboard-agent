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

# ADR-0003 §4: psycopg 3 LGPL is accepted unmodified (including psycopg-binary).
ACCEPTED_LGPL = frozenset({"psycopg", "psycopg-binary"})

AUTHORITY_NOTE_PRINTED = False

# SPDX and classifier forms for GPL-family (includes LGPL/AGPL).
_GPL_SPDX = re.compile(
    r"^(GPL|LGPL|AGPL)(-|\s|$)|"
    r"-only$|-or-later$",
    re.IGNORECASE,
)
_GPL_CLASSIFIER = re.compile(
    r"GNU (General Public|Lesser General Public|Affero General Public) License|"
    r"\(GPLv[0-9]\)",
    re.IGNORECASE,
)


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


def pip_audit_violations(payload: Any) -> tuple[list[str], list[str]]:
    """Return (fixable package names, unfixable advisory summaries)."""
    fixable: list[str] = []
    unfixable: list[str] = []
    if not isinstance(payload, dict):
        return fixable, unfixable
    for dep in payload.get("dependencies") or []:
        if not isinstance(dep, dict):
            continue
        name = str(dep.get("name", ""))
        for vuln in dep.get("vulns") or []:
            if not isinstance(vuln, dict):
                continue
            fix_versions = vuln.get("fix_versions") or []
            vid = str(vuln.get("id", "unknown"))
            if fix_versions:
                fixable.append(name)
            else:
                unfixable.append(f"{name}: {vid} (no fix version published)")
    return sorted(set(fixable)), unfixable


def _is_gpl_family(licence: str) -> bool:
    text = licence.strip()
    if not text or text.lower() == "unknown":
        return False
    upper = text.upper()
    if "LGPL" in upper and any(p in upper for p in ("LGPL-2", "LGPL-3", "GNU LESSER")):
        return True
    if _GPL_SPDX.search(text) or _GPL_CLASSIFIER.search(text):
        return True
    return bool(re.search(r"\bGPL\b|\bAGPL\b", text, re.IGNORECASE))


def _python_licence_for_dist(dist: importlib.metadata.Distribution) -> str:
    meta = dist.metadata
    expr = meta.get("License-Expression")
    if expr:
        return str(expr).strip()
    lic = meta.get("License")
    if lic:
        return str(lic).splitlines()[0].strip()
    for c in meta.get_all("Classifier") or []:
        if str(c).startswith("License"):
            return str(c).split(":", 1)[-1].strip()
    return "unknown"


def classify_python_licences() -> tuple[list[tuple[str, str]], list[str], list[str]]:
    rows: list[tuple[str, str]] = []
    violations: list[str] = []
    unknown: list[str] = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name") or dist.name
        licence = _python_licence_for_dist(dist)
        rows.append((name, licence))
        if licence == "unknown":
            unknown.append(name)
            continue
        if name in ACCEPTED_LGPL and "LGPL" in licence.upper():
            continue
        if _is_gpl_family(licence):
            violations.append(f"{name}: {licence}")
    return sorted(rows, key=lambda r: r[0].lower()), violations, sorted(unknown)


def parse_pnpm_licenses_json(payload: Any) -> list[tuple[str, str]]:
    """Parse `pnpm licenses list --json` (licence name → package list)."""
    if not isinstance(payload, dict):
        raise TypeError("pnpm licenses JSON must be an object")
    rows: list[tuple[str, str]] = []
    for licence_name, packages in payload.items():
        if not isinstance(packages, list):
            continue
        for pkg in packages:
            if isinstance(pkg, dict):
                name = str(pkg.get("name", ""))
                rows.append((name, str(licence_name)))
            elif isinstance(pkg, str):
                rows.append((pkg, str(licence_name)))
    return sorted(rows, key=lambda r: r[0].lower())


def classify_node_licences(
    rows: list[tuple[str, str]],
) -> tuple[list[str], list[str]]:
    violations: list[str] = []
    unknown: list[str] = []
    for name, licence in rows:
        if licence.lower() == "unknown":
            unknown.append(name)
            continue
        if name in ACCEPTED_LGPL and "LGPL" in licence.upper():
            continue
        if _is_gpl_family(licence):
            violations.append(f"{name}: {licence}")
    return violations, sorted(unknown)


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
    global AUTHORITY_NOTE_PRINTED
    proc = _run(
        ["uv", "run", "pip-audit", "--format", "json"],
        cwd=repo_root() / "backend",
    )
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end="")
        return proc.returncode
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        print("pip-audit: invalid JSON output", file=sys.stderr)
        return 1
    fixable, unfixable = pip_audit_violations(payload)
    if not AUTHORITY_NOTE_PRINTED:
        print(
            "Note: PyPI advisory data from pip-audit carries no severity; "
            "every vulnerability with a published fix version blocks this step.",
            flush=True,
        )
        AUTHORITY_NOTE_PRINTED = True
    for msg in unfixable:
        print(f"PIP-AUDIT (warning): {msg}", file=sys.stderr)
    for name in fixable:
        print(
            f"PIP-AUDIT: {name} has a fixable vulnerability",
            file=sys.stderr,
        )
    return 1 if fixable else 0


def run_pnpm_audit() -> int:
    proc = _run(["pnpm", "audit", "--audit-level", "high"])
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


def run_licence_report() -> int:
    root = repo_root()
    py_rows, py_violations, py_unknown = classify_python_licences()
    proc = _run(["pnpm", "licenses", "list", "--json"])
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        print("FAILED: pnpm licenses list", file=sys.stderr)
        return proc.returncode or 1
    try:
        node_payload = json.loads(proc.stdout or "{}")
        node_rows = parse_pnpm_licenses_json(node_payload)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"pnpm licenses: unparsable output ({exc})", file=sys.stderr)
        return 1

    node_violations, node_unknown = classify_node_licences(node_rows)

    report_path = root / "tests/reports/security/licenses.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Python packages", ""]
    for name, licence in py_rows:
        lines.append(f"{name}\t{licence}")
    if py_unknown:
        lines.extend(["", "# Python unknown licence", "", *list(py_unknown)])
    lines.extend(["", "# Node packages", ""])
    for name, licence in node_rows:
        lines.append(f"{name}\t{licence}")
    if node_unknown:
        lines.extend(["", "# Node unknown licence", "", *list(node_unknown)])
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Licence report: {report_path.relative_to(root)}")

    violations = py_violations + node_violations
    for item in violations:
        print(f"LICENSE: {item}", file=sys.stderr)
    return 1 if violations else 0


def main() -> int:
    root = repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
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
