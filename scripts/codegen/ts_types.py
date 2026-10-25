"""Generate TypeScript types from JSON Schemas."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _root() -> Path:
    return Path(os.environ.get("CENOMI_CODEGEN_ROOT", REPO_ROOT))


SCHEMAS = [
    "error_envelope.v1.schema.json",
    "principal.v1.schema.json",
    "scope_decision.v1.schema.json",
    "health_report.v1.schema.json",
    "dataset_descriptor.v1.schema.json",
]
BANNER = "// GENERATED — do not edit. Run `make codegen`.\n\n"


def generate_types() -> None:
    root = _root()
    out_dir = root / "packages" / "contracts-ts" / "src" / "types"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in SCHEMAS:
        stem = name.replace(".v1.schema.json", "")
        schema_path = root / "specs" / "contracts" / name
        out_path = out_dir / f"{stem}.v1.ts"
        cmd = [
            "pnpm",
            "--filter",
            "@cenomi/contracts-ts",
            "exec",
            "json2ts",
            schema_path.as_posix(),
        ]
        result = subprocess.run(
            cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)
        out_path.write_text(BANNER + result.stdout, encoding="utf-8")


def main() -> int:
    try:
        generate_types()
    except RuntimeError as exc:
        print(f"TS type generation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
