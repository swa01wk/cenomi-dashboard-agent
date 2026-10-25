"""Orchestrate `make contracts-check` (M0-T05)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.codegen.drift import find_stale_generated_files
from scripts.codegen.examples import validate_examples
from scripts.codegen.export_schemas import (
    atomic_write_schemas,
    compare_to_bootstrap,
)
from scripts.codegen.subset import validate_schema_file


def main() -> int:

    stale = find_stale_generated_files()
    if stale:
        print("Stale GENERATED files:", file=sys.stderr)
        for item in stale:
            print(f"  - {item}", file=sys.stderr)

    contracts_dir = REPO_ROOT / "specs" / "contracts"
    subset_errors: list[str] = []
    for path in sorted(contracts_dir.glob("*.v1.schema.json")):
        for violation in validate_schema_file(path):
            subset_errors.append(f"{path.name}: {violation.path} — {violation.reason}")
        subset_errors.extend(validate_examples(path, contracts_dir=contracts_dir))
    if subset_errors:
        print("Schema subset/example errors:", file=sys.stderr)
        for err in subset_errors:
            print(f"  - {err}", file=sys.stderr)

    import tempfile

    temp = Path(tempfile.mkdtemp())
    schemas = atomic_write_schemas(temp)
    boot_errors = compare_to_bootstrap(schemas)

    reports = REPO_ROOT / "tests" / "reports" / "contracts"
    reports.mkdir(parents=True, exist_ok=True)
    code = subprocess.run(
        [
            "uv",
            "run",
            "--directory",
            str(REPO_ROOT / "backend"),
            "pytest",
            "-c",
            "pyproject.toml",
            "--rootdir=..",
            "--confcutdir=..",
            "../tests/contract",
            "-m",
            "not db",
            f"--junitxml={reports / 'junit-contracts.xml'}",
        ],
        cwd=REPO_ROOT,
        check=False,
    ).returncode

    vitest = subprocess.run(
        ["pnpm", "--filter", "@cenomi/contracts-ts", "test"],
        cwd=REPO_ROOT,
        check=False,
    )

    if stale or subset_errors or boot_errors or code != 0 or vitest.returncode != 0:
        if boot_errors:
            print("Bootstrap equivalence errors:", file=sys.stderr)
            for err in boot_errors:
                print(f"  - {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
