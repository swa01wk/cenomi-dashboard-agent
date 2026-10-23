"""Request logging and correlation middleware (ARCH-R096, ARCH-R098)."""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from cenomi.core.ids import new_request_ref
from cenomi.core.request_context import RequestContext, get_request_context, set_request_context
from cenomi.core.traceparent import parse_traceparent

logger = logging.getLogger("cenomi.api.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_ref = new_request_ref()
        trace = parse_traceparent(request.headers.get("traceparent"))
        trace_id = trace[0] if trace else ""
        span_id = trace[1] if trace else ""
        set_request_context(
            RequestContext(request_ref=request_ref, trace_id=trace_id, span_id=span_id)
        )
        request.state.request_ref = request_ref

        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - started) * 1000)
        ctx = get_request_context()
        status_code = response.status_code
        event = "request_failed" if status_code >= 400 else "request_completed"
        log_fn = logger.warning if status_code >= 400 else logger.info
        log_fn(
            "request handled",
            extra={
                "event": event,
                "route": request.url.path,
                "method": request.method,
                "status": status_code,
                "durationMs": duration_ms,
                "requestRef": ctx.request_ref,
                "traceId": ctx.trace_id or None,
            },
        )

        response.headers["X-Request-Ref"] = request_ref
        response.headers["Cache-Control"] = "no-store"
        return response
