"""Finding format for specs-check (M0-T10)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    code: str
    message: str

    def format(self) -> str:
        loc = self.path if self.line <= 0 else f"{self.path}:{self.line}"
        return f"{loc}: {self.code} {self.message}"
