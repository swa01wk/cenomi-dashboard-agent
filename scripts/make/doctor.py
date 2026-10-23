"""Toolchain checks for `make doctor` (specs/engineering/make_targets.yaml)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPO_ROOT / "backend"
TOOLS_LOCK = REPO_ROOT / "scripts/tools.lock"


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip()
    except FileNotFoundError:
        return 127, ""


def _node_major() -> str | None:
    code, out = _run(["node", "--version"])
    if code != 0:
        return None
    match = re.match(r"v(\d+)", out.strip())
    return match.group(1) if match else None


def _pnpm_version() -> str | None:
    code, out = _run(["pnpm", "--version"])
    return out.strip() if code == 0 else None


def _read_package_manager() -> str | None:
    pkg = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    pm = pkg.get("packageManager", "")
    if pm.startswith("pnpm@"):
        return pm.split("@", 1)[1]
    return None


def _python_version_via_uv() -> str | None:
    code, out = _run(["uv", "python", "find", "3.12"])
    if code != 0 or not out.strip():
        return None
    code2, out2 = _run(["uv", "python", "list", "--only-installed"])
    if code2 == 0 and "3.12" in out2:
        match = re.search(r"3\.12\.\d+", out2)
        return match.group(0) if match else "3.12.x"
    return "3.12.x (available to uv)"


def _make_version() -> tuple[bool, str]:
    code, out = _run(["make", "--version"])
    if code != 0:
        return False, "missing"
    first = out.splitlines()[0] if out else ""
    match = re.search(r"GNU Make (\d+)", first)
    if not match:
        return False, first or "unknown"
    return int(match.group(1)) >= 4, first


def _docker_ok() -> tuple[bool, str]:
    code, _ = _run(["docker", "version"])
    if code != 0:
        return False, "docker not available"
    code2, out = _run(["docker", "compose", "version"])
    if code2 != 0:
        return False, "docker compose v2 not available"
    return True, out.splitlines()[0] if out else "ok"


def _ports_free() -> list[str]:
    issues: list[str] = []
    for port in (3000, 8000, 5432):
        code, out = _run(["lsof", "-i", f":{port}", "-sTCP:LISTEN"])
        if code == 0 and out.strip():
            issues.append(f"port {port} in use")
    return issues


def run_doctor() -> tuple[bool, list[str]]:
    mismatches: list[str] = []
    rows: list[tuple[str, str, str]] = []

    code, uv_out = _run(["uv", "--version"])
    rows.append(("uv", "installed", uv_out.splitlines()[0] if code == 0 else "missing"))
    if code != 0:
        mismatches.append("uv")

    py = _python_version_via_uv()
    rows.append(("Python", "3.12.x via uv", py or "missing"))
    if not py:
        mismatches.append("Python 3.12.x")

    node_major = _node_major()
    rows.append(("Node.js", "22.x", f"v{node_major}.x" if node_major else "missing"))
    if node_major != "22":
        mismatches.append("Node.js 22.x")

    expected_pnpm = _read_package_manager()
    found_pnpm = _pnpm_version()
    rows.append(("pnpm", expected_pnpm or "packageManager", found_pnpm or "missing"))
    if expected_pnpm and found_pnpm != expected_pnpm:
        mismatches.append("pnpm version")

    make_ok, make_label = _make_version()
    rows.append(("GNU Make", "≥ 4", make_label))
    if not make_ok:
        mismatches.append("GNU Make")

    docker_ok, docker_label = _docker_ok()
    rows.append(("Docker", "Engine + Compose v2", docker_label))
    if not docker_ok:
        mismatches.append("Docker")

    for name, path in (
        ("uv.lock", BACKEND / "uv.lock"),
        ("pnpm-lock.yaml", REPO_ROOT / "pnpm-lock.yaml"),
    ):
        exists = path.is_file()
        rows.append((name, "present", "yes" if exists else "missing"))
        if not exists:
            mismatches.append(name)

    env_path = REPO_ROOT / ".env"
    rows.append((".env", "optional", "present" if env_path.is_file() else "absent (warn)"))

    port_issues = _ports_free()
    rows.append(("ports 3000/8000/5432", "free or project", ", ".join(port_issues) if port_issues else "ok"))

    print(f"{'Component':<24} {'Expected':<22} Found")
    print("-" * 72)
    for component, expected, found in rows:
        print(f"{component:<24} {expected:<22} {found}")

    if mismatches:
        print("\nMismatches:", ", ".join(mismatches), file=sys.stderr)
        return False, mismatches
    return True, []
