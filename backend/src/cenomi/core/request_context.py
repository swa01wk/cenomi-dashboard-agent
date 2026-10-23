"""Per-request context (requestRef, trace ids)."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class RequestContext:
    request_ref: str = ""
    trace_id: str = ""
    span_id: str = ""


_context: ContextVar[RequestContext | None] = ContextVar("cenomi_request_context", default=None)


def get_request_context() -> RequestContext:
    ctx = _context.get()
    if ctx is None:
        return RequestContext()
    return ctx


def set_request_context(ctx: RequestContext) -> None:
    _context.set(ctx)
