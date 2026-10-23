"""Parse the root Makefile ## summaries for `make help` (DEVENV-R011)."""

from __future__ import annotations

import re
from pathlib import Path

from targets import GROUP_LABELS, TARGETS

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = REPO_ROOT / "Makefile"
TARGET_LINE = re.compile(r"^([a-z0-9-]+):\s*##\s*(.+)$")


def parse_makefile_summaries() -> dict[str, str]:
    summaries: dict[str, str] = {}
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        match = TARGET_LINE.match(line.strip())
        if match:
            summaries[match.group(1)] = match.group(2).strip()
    return summaries


def render_help() -> str:
    summaries = parse_makefile_summaries()
    lines: list[str] = []
    current_group = None
    for meta in TARGETS:
        if meta.group != current_group:
            current_group = meta.group
            if lines:
                lines.append("")
            lines.append(GROUP_LABELS[current_group])
        summary = summaries.get(meta.name, meta.summary)
        lines.append(f"  {meta.name:<22} {summary}")
    return "\n".join(lines) + "\n"
