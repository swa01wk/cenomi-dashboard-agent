"""Export Pydantic models to ADR-0004 JSON Schemas."""

from __future__ import annotations

import copy
from typing import Any

from pydantic import BaseModel

from cenomi.contracts.registry import BuiltContract
from cenomi.contracts.schema_generator import CenomiGenerateJsonSchema

JSON_SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"
SCOPE_EXTERNAL_REF = "scope_decision.v1.schema.json#/$defs/scope"


def _string_def(pattern: str) -> dict[str, Any]:
    return {"type": "string", "pattern": pattern}


def _scope_branch(*, kind: str, extra_props: dict[str, Any]) -> dict[str, Any]:
    props: dict[str, Any] = {"kind": {"const": kind}, **extra_props}
    required = ["kind", *extra_props.keys()]
    return {
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": props,
    }


def scope_defs_block() -> dict[str, Any]:
    """$defs block shared by scope_decision and referenced from principal."""
    return {
        "regionKey": _string_def(r"^[a-z][a-z0-9-]{1,40}$"),
        "mallKey": _string_def(r"^[a-z0-9][a-z0-9-]{1,60}$"),
        "tenantKey": _string_def(r"^[a-z0-9][a-z0-9-]{1,60}$"),
        "leaseKey": _string_def(r"^[A-Z]{1,3}-[0-9]{3,8}$"),
        "scope": {
            "description": (
                "An explicit access scope. Business keys are stable string keys, "
                "provisional until CF-1 (ARCH-R078)."
            ),
            "oneOf": [
                _scope_branch(kind="ALL", extra_props={}),
                _scope_branch(
                    kind="REGIONS",
                    extra_props={
                        "regionKeys": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 3,
                            "items": {"$ref": "#/$defs/regionKey"},
                        }
                    },
                ),
                _scope_branch(
                    kind="MALLS",
                    extra_props={
                        "mallKeys": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 50,
                            "items": {"$ref": "#/$defs/mallKey"},
                        }
                    },
                ),
                _scope_branch(
                    kind="TENANT",
                    extra_props={
                        "tenantKeys": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 10,
                            "items": {"$ref": "#/$defs/tenantKey"},
                        }
                    },
                ),
                _scope_branch(
                    kind="TENANT_LEASES",
                    extra_props={
                        "leaseKeys": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 100,
                            "items": {"$ref": "#/$defs/leaseKey"},
                        }
                    },
                ),
            ],
        },
    }


def _ref_scope() -> dict[str, Any]:
    return {"$ref": "#/$defs/scope"}


def _model_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    return model.model_json_schema(
        by_alias=True,
        mode="serialization",
        schema_generator=CenomiGenerateJsonSchema,
    )


def _merge_root_annotations(exported: dict[str, Any], model: type[BaseModel]) -> None:
    extra = model.model_config.get("json_schema_extra") or {}
    if isinstance(extra, dict):
        for key in ("title", "description", "examples"):
            if key in extra:
                exported[key] = extra[key]


def _resolve_local_refs(node: Any, defs: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        if set(node.keys()) == {"$ref"} and isinstance(node["$ref"], str):
            ref = node["$ref"]
            if ref.startswith("#/$defs/"):
                name = ref.removeprefix("#/$defs/")
                return _resolve_local_refs(copy.deepcopy(defs[name]), defs)
        return {k: _resolve_local_refs(v, defs) for k, v in node.items()}
    if isinstance(node, list):
        return [_resolve_local_refs(item, defs) for item in node]
    return node


def _tighten_const_schemas(node: Any) -> Any:
    if isinstance(node, dict):
        if "const" in node and set(node.keys()) <= {"const", "type", "title", "description"}:
            return {"const": node["const"]}
        return {k: _tighten_const_schemas(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_tighten_const_schemas(item) for item in node]
    return node


def _inline_defs(exported: dict[str, Any]) -> None:
    defs = exported.pop("$defs", {})
    if not defs:
        return
    inlined = _resolve_local_refs(exported, defs)
    exported.clear()
    exported.update(inlined)


def export_contract_schema(contract: BuiltContract) -> dict[str, Any]:
    exported = _model_json_schema(contract.model)
    _merge_root_annotations(exported, contract.model)

    if contract.stem == "scope_decision":
        defs = scope_defs_block()
        exported.pop("$defs", None)
        props = exported.get("properties", {})
        for key in ("requested", "effective"):
            if key in props:
                desc = props[key].get("description")
                props[key] = _ref_scope()
                if desc:
                    props[key]["description"] = desc
        exported["$defs"] = defs
    elif contract.stem == "principal":
        _inline_defs(exported)
        grants = exported["properties"]["grants"]
        grants["items"] = {"$ref": SCOPE_EXTERNAL_REF}
    else:
        _inline_defs(exported)

    tightened = _tighten_const_schemas(exported)
    if not isinstance(tightened, dict):
        raise TypeError("exported schema must remain an object")
    exported = tightened
    exported["$schema"] = JSON_SCHEMA_DRAFT
    exported["$id"] = contract.schema_id
    exported.setdefault("type", "object")
    exported.setdefault("additionalProperties", False)
    return exported
