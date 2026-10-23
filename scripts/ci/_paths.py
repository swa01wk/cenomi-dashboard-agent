"""Glob matching for ci_checks path categories."""

from __future__ import annotations

import re


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def path_matches(path: str, pattern: str) -> bool:
    """Match a repository-relative POSIX path against a glob from ci_checks.yaml."""
    path = normalize_path(path)
    pattern = pattern.replace("\\", "/")

    if pattern.endswith("/**"):
        root = pattern[:-3]
        return path == root or path.startswith(root + "/")

    if "**" in pattern:
        rx = (
            "^"
            + re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
            + "$"
        )
        return re.match(rx, path) is not None

    if pattern.startswith("**/"):
        tail = pattern[3:]
        if re.fullmatch(re.escape(tail).replace(r"\*", "[^/]*"), path):
            return True
        base = path.rsplit("/", 1)[-1]
        return re.fullmatch(re.escape(tail).replace(r"\*", "[^/]*"), base) is not None

    return re.fullmatch(re.escape(pattern).replace(r"\*", "[^/]*"), path) is not None


def categories_for_path(path: str, category_globs: dict[str, list[str]]) -> set[str]:
    matched: set[str] = set()
    norm = normalize_path(path)
    for name, globs in category_globs.items():
        if name == "docs_only_candidates":
            continue
        for glob in globs:
            if path_matches(norm, glob):
                matched.add(name)
                break
    return matched
