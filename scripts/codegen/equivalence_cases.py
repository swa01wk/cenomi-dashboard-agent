"""Generate jsonschema vs zod equivalence corpus (CA-05)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from jsonschema.exceptions import ValidationError  # type: ignore[import-untyped]

from scripts.codegen.examples import FORMAT_CHECKER, _registry_for_contracts

CORPUS_REL = Path("packages/contracts-ts/src/zod/__fixtures__/equivalence.cases.json")


def _validate(schema: dict[str, Any], instance: Any, *, contracts_dir: Path) -> bool:
    registry = _registry_for_contracts(contracts_dir)
    validator = Draft202012Validator(
        schema, registry=registry, format_checker=FORMAT_CHECKER
    )
    try:
        validator.validate(instance)
        return True
    except ValidationError:
        return False


def _mutations_for_schema(
    schema: dict[str, Any], example: dict[str, Any]
) -> list[tuple[str, Any]]:
    cases: list[tuple[str, Any]] = []

    def walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            cases.append((f"{path}:unknown_field", {**obj, "__bad": True}))
            for key, val in list(obj.items()):
                without = copy.deepcopy(obj)
                del without[key]
                cases.append((f"{path}:drop_{key}", without))
                if isinstance(val, (bool, int)):
                    cases.append((f"{path}:{key}_wrong_type", {**obj, key: "x"}))
                elif isinstance(val, str):
                    cases.append((f"{path}:{key}_wrong_type", {**obj, key: 1}))
                elif isinstance(val, list):
                    cases.append((f"{path}:{key}_wrong_type", {**obj, key: {}}))
                walk(val, f"{path}.{key}")
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                walk(item, f"{path}[{idx}]")

    walk(example, "$")

    cases.append(("null_root", None))
    return cases


def build_corpus(*, repo_root: Path | None = None) -> dict[str, Any]:
    import os

    default_root = Path(__file__).resolve().parents[2]
    root = repo_root or Path(os.environ.get("CENOMI_CODEGEN_ROOT", default_root))
    contracts_dir = root / "specs" / "contracts"
    out: dict[str, Any] = {"schemas": {}}
    for path in sorted(contracts_dir.glob("*.v1.schema.json")):
        if path.name == "error_codes.v1.yaml":
            continue
        schema = json.loads(path.read_text(encoding="utf-8"))
        stem = path.name.removesuffix(".v1.schema.json")
        entries: list[dict[str, Any]] = []
        for example in schema.get("examples", []):
            entries.append(
                {
                    "id": f"{stem}:example:{len(entries)}",
                    "payload": example,
                    "jsonschemaValid": _validate(
                        schema, example, contracts_dir=contracts_dir
                    ),
                }
            )
        for label, payload in _mutations_for_schema(schema, schema["examples"][0]):
            entries.append(
                {
                    "id": f"{stem}:mut:{label}",
                    "payload": payload,
                    "jsonschemaValid": _validate(
                        schema, payload, contracts_dir=contracts_dir
                    ),
                }
            )
        accepted = sum(1 for e in entries if e["jsonschemaValid"])
        rejected = len(entries) - accepted
        if accepted < 1 or rejected < 1:
            raise RuntimeError(f"{stem}: need accepted and rejected cases")
        out["schemas"][stem] = entries
    return out


def write_corpus(*, repo_root: Path | None = None) -> Path:
    import os

    default_root = Path(__file__).resolve().parents[2]
    root = repo_root or Path(os.environ.get("CENOMI_CODEGEN_ROOT", default_root))
    corpus = build_corpus(repo_root=root)
    dest = root / CORPUS_REL
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(corpus, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return dest
