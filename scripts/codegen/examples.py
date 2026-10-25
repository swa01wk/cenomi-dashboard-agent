"""Validate schema examples with jsonschema Draft 2020-12 and format checking."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker  # type: ignore[import-untyped]
from jsonschema.exceptions import ValidationError  # type: ignore[import-untyped]
from referencing import Registry, Resource
from rfc3339_validator import validate_rfc3339  # type: ignore[import-untyped]

FORMAT_CHECKER = FormatChecker()


@FORMAT_CHECKER.checks("date-time")  # type: ignore[untyped-decorator]
def _check_date_time(instance: object) -> bool:
    return isinstance(instance, str) and validate_rfc3339(instance)


def _registry_for_contracts(contracts_dir: Path) -> Registry:
    resources: list[tuple[str, Resource[Any]]] = []

    def _retrieve(uri: str) -> Resource[Any]:
        name = uri.rsplit("/", 1)[-1]
        path = contracts_dir / name
        if not path.is_file():
            raise FileNotFoundError(uri)
        contents = json.loads(path.read_text(encoding="utf-8"))
        return Resource.from_contents(contents)

    for path in sorted(contracts_dir.glob("*.v1.schema.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        schema_id = contents.get("$id")
        if schema_id:
            resources.append((schema_id, Resource.from_contents(contents)))
        resources.append((path.as_uri(), Resource.from_contents(contents)))

    return Registry(retrieve=_retrieve).with_resources(resources)  # type: ignore[call-arg]


def validate_examples(schema_path: Path, *, contracts_dir: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    examples = schema.get("examples") or []
    registry = _registry_for_contracts(contracts_dir)
    validator = Draft202012Validator(
        schema, registry=registry, format_checker=FORMAT_CHECKER
    )
    errors: list[str] = []
    for idx, example in enumerate(examples):
        try:
            validator.validate(example)
        except ValidationError as exc:
            errors.append(f"{schema_path.name} examples[{idx}]: {exc.message}")
    return errors
