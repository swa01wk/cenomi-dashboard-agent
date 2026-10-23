"""Request reference identifiers (ARCH-R020)."""

from __future__ import annotations

import secrets


def new_request_ref() -> str:
    return f"req_{secrets.token_hex(8)}"
