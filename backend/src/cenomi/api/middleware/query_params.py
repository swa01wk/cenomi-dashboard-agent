"""Reject unknown query parameters (ARCH-R014)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from cenomi.api.envelope import from_cenomi_error
from cenomi.api.response_headers import json_response
from cenomi.core.errors import ValidationDetail, ValidationFailed
from cenomi.core.request_context import get_request_context

ALLOWED_QUERY_PARAMS: dict[str, set[str]] = {
    "/api/v1/health": set(),
    "/api/v1/health/live": set(),
    "/api/v1/dataset": set(),
}


class UnknownQueryParamsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        allowed = ALLOWED_QUERY_PARAMS.get(request.url.path)
        if allowed is not None:
            for key in request.query_params:
                if key not in allowed:
                    ref = (
                        getattr(request.state, "request_ref", "")
                        or get_request_context().request_ref
                    )
                    exc = ValidationFailed(
                        details=[
                            ValidationDetail(path=f"query.{key}", rule="unknown_field"),
                        ]
                    )
                    return json_response(
                        status_code=400,
                        content=from_cenomi_error(exc, ref),
                        request_ref=ref,
                    )
        return await call_next(request)
