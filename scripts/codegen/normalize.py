"""Normalize exported JSON Schemas for bootstrap comparison (ADR-0004 §1)."""

from __future__ import annotations

from typing import Any


def _drop_annotation_keywords(node: Any, *, at_root: bool) -> Any:
    if isinstance(node, dict):
        out: dict[str, Any] = {}
        for key in sorted(node.keys()):
            if key in {"title", "description"}:
                continue
            if at_root and key == "x-generated-from":
                continue
            out[key] = _drop_annotation_keywords(node[key], at_root=False)
        return out
    if isinstance(node, list):
        return [_drop_annotation_keywords(item, at_root=False) for item in node]
    return node


def normalize_schema(schema: dict[str, Any]) -> dict[str, Any]:
    cleaned = _drop_annotation_keywords(schema, at_root=True)
    assert isinstance(cleaned, dict)
    return cleaned


def first_diff_path(left: Any, right: Any, path: str = "$") -> str | None:
    if type(left) is not type(right):
        return path
    if isinstance(left, dict):
        if not isinstance(right, dict):
            return path
        keys = sorted(set(left) | set(right))
        for key in keys:
            if key not in left or key not in right:
                return f"{path}.{key}"
            sub = first_diff_path(left[key], right[key], f"{path}.{key}")
            if sub:
                return sub
        return None
    if isinstance(left, list):
        if not isinstance(right, list):
            return path
        if len(left) != len(right):
            return f"{path}[length]"
        for idx, (a, b) in enumerate(zip(left, right, strict=True)):
            sub = first_diff_path(a, b, f"{path}[{idx}]")
            if sub:
                return sub
        return None
    if left != right:
        return path
    return None
