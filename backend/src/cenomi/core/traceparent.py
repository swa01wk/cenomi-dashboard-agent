"""W3C traceparent parsing (ARCH-R021)."""

from __future__ import annotations

import re

_TRACEPARENT = re.compile(
    r"^[\da-f]{2}-([\da-f]{32})-([\da-f]{16})-([\da-f]{2})$",
    re.IGNORECASE,
)


def parse_traceparent(value: str | None) -> tuple[str, str] | None:
    if not value:
        return None
    match = _TRACEPARENT.match(value.strip())
    if not match:
        return None
    trace_id, span_id, _flags = match.groups()
    return trace_id.lower(), span_id.lower()
