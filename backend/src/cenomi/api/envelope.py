"""Error envelope builders (error_envelope.v1)."""

from __future__ import annotations

from typing import Any

from cenomi.core.errors import CenomiError, ValidationDetail


def error_envelope(
    *,
    code: str,
    message: str,
    request_ref: str,
    retryable: bool,
    details: list[ValidationDetail] | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {
        "code": code,
        "message": message,
        "requestRef": request_ref,
        "retryable": retryable,
    }
    if details:
        error["details"] = [{"path": d.path, "rule": d.rule} for d in details]
    return {"error": error}


def from_cenomi_error(exc: CenomiError, request_ref: str) -> dict[str, Any]:
    return error_envelope(
        code=exc.code,
        message=exc.message,
        request_ref=request_ref,
        retryable=exc.retryable,
        details=exc.details,
    )
