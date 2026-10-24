"""Shared uv invocation for CI scripts (pyyaml via backend lockfile)."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPO_ROOT / "backend"


def uv_python(script: Path, *args: str) -> int:
    rel = script.relative_to(REPO_ROOT)
    cmd = [
        "uv",
        "run",
        "--directory",
        str(BACKEND),
        "python",
        str(rel),
        *args,
    ]
    print(f"+ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=REPO_ROOT, check=False).returncode


def uv_module(module: str, *args: str) -> int:
    cmd = ["uv", "run", "--directory", str(BACKEND), "python", "-m", module, *args]
    print(f"+ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=REPO_ROOT, check=False).returncode
