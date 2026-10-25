"""Export cenomi.contracts models to specs/contracts (ADR-0004)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BACKEND_SRC = REPO_ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from cenomi.contracts.export import export_contract_schema
from cenomi.contracts.registry import BUILT_CONTRACTS

from scripts.codegen.normalize import first_diff_path, normalize_schema


def _contracts_dir() -> Path:
    root = Path(os.environ.get("CENOMI_CODEGEN_ROOT", REPO_ROOT))
    return root / "specs" / "contracts"


CONTRACTS_DIR = REPO_ROOT / "specs" / "contracts"
BOOTSTRAP_DIR = REPO_ROOT / "tests" / "contract" / "fixtures" / "bootstrap"


def _serialize(schema: dict[str, Any]) -> str:
    return json.dumps(schema, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def export_all_schemas(*, out_dir: Path) -> dict[str, dict[str, Any]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    exported: dict[str, dict[str, Any]] = {}
    for contract in BUILT_CONTRACTS:
        schema = export_contract_schema(contract)
        schema["x-generated-from"] = contract.dotted_path
        path = out_dir / contract.filename
        path.write_text(_serialize(schema), encoding="utf-8")
        exported[contract.filename] = schema
    return exported


def compare_to_bootstrap(schemas: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for contract in BUILT_CONTRACTS:
        bootstrap_path = BOOTSTRAP_DIR / contract.filename
        if not bootstrap_path.is_file():
            errors.append(f"missing bootstrap fixture {bootstrap_path}")
            continue
        bootstrap = json.loads(bootstrap_path.read_text(encoding="utf-8"))
        generated = schemas[contract.filename]
        norm_boot = normalize_schema(bootstrap)
        norm_gen = normalize_schema(generated)
        diff = first_diff_path(norm_boot, norm_gen)
        if diff:
            errors.append(f"{contract.filename}: first difference at {diff}")
    return errors


def atomic_write_schemas(out_dir: Path) -> dict[str, dict[str, Any]]:
    schemas = export_all_schemas(out_dir=out_dir)
    return schemas


def swap_generated_contracts(temp_dir: Path) -> None:
    dest_dir = _contracts_dir()
    for contract in BUILT_CONTRACTS:
        src = temp_dir / contract.filename
        dest = dest_dir / contract.filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def run_export(*, dry_run_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    if dry_run_dir is not None:
        return atomic_write_schemas(dry_run_dir)

    temp_root = Path(tempfile.mkdtemp(prefix="cenomi-codegen-schemas-"))
    try:
        schemas = atomic_write_schemas(temp_root)
        errors = compare_to_bootstrap(schemas)
        if errors:
            raise RuntimeError("bootstrap equivalence failed:\n" + "\n".join(errors))
        swap_generated_contracts(temp_root)
        return schemas
    finally:
        for path in temp_root.glob("*"):
            path.unlink(missing_ok=True)
        temp_root.rmdir()


def main() -> int:
    try:
        run_export()
    except RuntimeError as exc:
        print(f"codegen schema export failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
