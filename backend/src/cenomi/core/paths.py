"""Repository path helpers."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "specs" / "engineering" / "spec_set.yaml").is_file():
            return parent
    raise FileNotFoundError("Could not locate repository root (spec_set.yaml missing)")
