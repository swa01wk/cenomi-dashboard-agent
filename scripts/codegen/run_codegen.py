"""Orchestrate `make codegen` (M0-T05)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def run_codegen(*, root: Path | None = None) -> None:
    target_root = root or REPO_ROOT
    env = os.environ.copy()
    env["CENOMI_CODEGEN_ROOT"] = str(target_root)

    if root is not None:
        (target_root / "specs" / "contracts").mkdir(parents=True, exist_ok=True)
        (target_root / "packages" / "contracts-ts" / "src" / "types").mkdir(
            parents=True, exist_ok=True
        )
        (target_root / "packages" / "contracts-ts" / "src" / "zod").mkdir(
            parents=True, exist_ok=True
        )

    from scripts.codegen.export_schemas import run_export

    if root is not None:
        from scripts.codegen.export_schemas import atomic_write_schemas

        atomic_write_schemas(target_root / "specs" / "contracts")
    else:
        run_export()

    steps = [
        [sys.executable, str(REPO_ROOT / "scripts" / "codegen" / "ts_types.py")],
        ["node", str(REPO_ROOT / "scripts" / "codegen" / "zod_from_schema.ts")],
    ]
    for cmd in steps:
        proc = subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"codegen failed: {' '.join(cmd)}")

    proc = subprocess.run(
        [
            "uv",
            "run",
            "--directory",
            str(REPO_ROOT / "backend"),
            "python",
            str(REPO_ROOT / "scripts" / "codegen" / "write_equivalence.py"),
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("equivalence corpus generation failed")


def main() -> int:
    try:
        run_codegen()
    except RuntimeError as exc:
        print(f"codegen failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
