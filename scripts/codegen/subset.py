"""ADR-0004 §2 JSON Schema subset validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_ROOT = {
    "$schema",
    "$id",
    "title",
    "description",
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "enum",
    "const",
    "pattern",
    "format",
    "minLength",
    "maxLength",
    "minimum",
    "maximum",
    "minItems",
    "maxItems",
    "oneOf",
    "$ref",
    "$defs",
    "examples",
    "x-generated-from",
}

ALLOWED_NESTED = ALLOWED_ROOT - {"x-generated-from", "$schema", "$id", "examples"}

ALLOWED_TYPES = {"object", "array", "string", "integer", "number", "boolean", "null"}
ALLOWED_FORMATS = {"date", "date-time", "uuid"}


@dataclass(frozen=True)
class SubsetViolation:
    path: str
    reason: str


def _check_node(node: Any, *, path: str, at_root: bool) -> list[SubsetViolation]:
    violations: list[SubsetViolation] = []
    if not isinstance(node, dict):
        return violations

    allowed = ALLOWED_ROOT if at_root else ALLOWED_NESTED
    for key in node:
        if key not in allowed:
            violations.append(SubsetViolation(path, f"forbidden keyword {key!r}"))

    if at_root:
        if node.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            violations.append(SubsetViolation(path, "missing or wrong $schema"))
        id_val = node.get("$id", "")
        if not re.fullmatch(
            r"https://cenomi\.local/contracts/[a-z0-9_]+\.v[0-9]+\.schema\.json", id_val
        ):
            violations.append(SubsetViolation(path, f"invalid $id {id_val!r}"))
        if "x-generated-from" in node and not isinstance(node["x-generated-from"], str):
            violations.append(
                SubsetViolation(path, "x-generated-from must be a string")
            )
        examples = node.get("examples")
        if not examples or not isinstance(examples, list) or len(examples) < 1:
            violations.append(
                SubsetViolation(path, "at least one examples entry required")
            )

    if "type" in node:
        typ = node["type"]
        if isinstance(typ, list):
            violations.append(
                SubsetViolation(path, "type must not be a union with null")
            )
        elif typ not in ALLOWED_TYPES:
            violations.append(SubsetViolation(path, f"unsupported type {typ!r}"))

    if "additionalProperties" in node and node["additionalProperties"] is not False:
        violations.append(SubsetViolation(path, "additionalProperties must be false"))
    if (
        (node.get("type") == "object" or "properties" in node)
        and node.get("type", "object") == "object"
        and "additionalProperties" not in node
    ):
        violations.append(
            SubsetViolation(path, "object missing additionalProperties: false")
        )

    fmt = node.get("format")
    if fmt is not None and fmt not in ALLOWED_FORMATS:
        violations.append(SubsetViolation(path, f"unsupported format {fmt!r}"))

    forbidden_keys = (
        "anyOf",
        "allOf",
        "if",
        "then",
        "else",
        "patternProperties",
        "dependentSchemas",
    )
    for forbidden in forbidden_keys:
        if forbidden in node:
            violations.append(
                SubsetViolation(path, f"forbidden composition keyword {forbidden!r}")
            )

    ref = node.get("$ref")
    if ref is not None:
        if not isinstance(ref, str):
            violations.append(SubsetViolation(path, "$ref must be a string"))
        elif ref.startswith("#/$defs/") or re.fullmatch(
            r"[a-z0-9_]+\.v[0-9]+\.schema\.json#/\$defs/[A-Za-z0-9_]+", ref
        ):
            pass
        else:
            violations.append(SubsetViolation(path, f"invalid $ref {ref!r}"))

    one_of = node.get("oneOf")
    if one_of is not None:
        if not isinstance(one_of, list):
            violations.append(SubsetViolation(path, "oneOf must be an array"))
        else:
            for idx, branch in enumerate(one_of):
                if not isinstance(branch, dict):
                    continue
                props = branch.get("properties", {})
                kind = props.get("kind", {})
                if not (isinstance(kind, dict) and "const" in kind):
                    violations.append(
                        SubsetViolation(
                            f"{path}.oneOf[{idx}]",
                            "oneOf branch must discriminate with kind.const",
                        )
                    )
                violations.extend(
                    _check_node(branch, path=f"{path}.oneOf[{idx}]", at_root=False)
                )

    for key in ("properties", "$defs"):
        if key in node and isinstance(node[key], dict):
            for sub_key, sub_val in node[key].items():
                violations.extend(
                    _check_node(sub_val, path=f"{path}.{key}.{sub_key}", at_root=False)
                )

    if "items" in node:
        items = node["items"]
        if isinstance(items, dict):
            violations.extend(_check_node(items, path=f"{path}.items", at_root=False))
        elif isinstance(items, list):
            for idx, item in enumerate(items):
                violations.extend(
                    _check_node(item, path=f"{path}.items[{idx}]", at_root=False)
                )

    return violations


def validate_subset(
    schema: dict[str, Any], *, path: str = "$"
) -> list[SubsetViolation]:
    return _check_node(schema, path=path, at_root=True)


def validate_schema_file(path: Path) -> list[SubsetViolation]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return [SubsetViolation(str(path), "schema root must be an object")]
    return validate_subset(data, path=str(path))
