"""Write equivalence corpus (invoked under uv)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.codegen.equivalence_cases import write_corpus


def main() -> int:
    write_corpus()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
