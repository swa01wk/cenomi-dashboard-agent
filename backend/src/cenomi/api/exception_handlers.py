"""Map exceptions to error_envelope.v1 (ARCH-R022, ARCH-R023)."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from cenomi.api.envelope import error_envelope, from_cenomi_error
from cenomi.api.response_headers import json_response
from cenomi.core.errors import CenomiError, Internal, ValidationDetail, ValidationFailed
from cenomi.core.request_context import get_request_context

logger = logging.getLogger(__name__)


def _request_ref(request: Request) -> str:
    ref = getattr(request.state, "request_ref", None)
    if isinstance(ref, str) and ref:
        return ref
    return get_request_context().request_ref


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(CenomiError)
    async def handle_cenomi_error(_request: Request, exc: CenomiError) -> JSONResponse:
        ref = _request_ref(_request)
        body = from_cenomi_error(exc, ref)
        return json_response(status_code=exc.http_status, content=body, request_ref=ref)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(_request: Request, exc: RequestValidationError) -> JSONResponse:
        ref = _request_ref(_request)
        details: list[ValidationDetail] = []
        for err in exc.errors():
            loc = err.get("loc", ())
            path_parts = [str(part) for part in loc if part != "body"]
            path = ".".join(path_parts) if path_parts else "body"
            rule = str(err.get("type", "invalid")).replace(".", "_")
            if len(rule) > 64 or not rule[0].isalpha():
                rule = "invalid"
            details.append(ValidationDetail(path=path[:200], rule=rule[:64]))
        body = from_cenomi_error(ValidationFailed(details=details), ref)
        return json_response(status_code=400, content=body, request_ref=ref)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        ref = _request_ref(_request)
        if exc.status_code == 404:
            body = error_envelope(
                code="NOT_AVAILABLE",
                message="This isn't available.",
                request_ref=ref,
                retryable=False,
            )
            return json_response(status_code=404, content=body, request_ref=ref)
        body = error_envelope(
            code="INTERNAL",
            message="Something went wrong.",
            request_ref=ref,
            retryable=False,
        )
        return json_response(status_code=exc.status_code, content=body, request_ref=ref)

    @app.exception_handler(Exception)
    async def handle_unhandled(_request: Request, exc: Exception) -> JSONResponse:
        ref = _request_ref(_request)
        logger.exception(
            "unhandled exception",
            extra={
                "event": "request_failed",
                "requestRef": ref,
                "traceId": get_request_context().trace_id or None,
            },
        )
        body = from_cenomi_error(Internal(), ref)
        return json_response(status_code=500, content=body, request_ref=ref)
