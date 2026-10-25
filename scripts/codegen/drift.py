"""Compare committed GENERATED artefacts with a fresh codegen staging tree."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def compare_staging_to_committed(staging: Path) -> list[str]:
    stale: list[str] = []
    checks: list[tuple[Path, tuple[str, ...]]] = [
        (staging / "specs/contracts", ("*.v1.schema.json",)),
        (staging / "packages/contracts-ts/src/types", ("*.ts",)),
        (staging / "packages/contracts-ts/src/zod", ("**/*.ts", "**/*.json")),
    ]
    for gen_root, patterns in checks:
        for pattern in patterns:
            for path in gen_root.glob(pattern):
                if path.is_dir():
                    continue
                rel = path.relative_to(staging)
                committed = REPO_ROOT / rel
                if not committed.is_file():
                    stale.append(rel.as_posix())
                    continue
                if path.read_bytes() != committed.read_bytes():
                    stale.append(rel.as_posix())
    return stale


def find_stale_generated_files() -> list[str]:
    from scripts.codegen.run_codegen import run_codegen

    staging = Path(tempfile.mkdtemp(prefix="cenomi-codegen-staging-"))
    try:
        run_codegen(root=staging)
        return compare_staging_to_committed(staging)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
