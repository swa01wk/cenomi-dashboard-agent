"""Common API response headers (ARCH-R013, ARCH-R020)."""

from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def json_response(
    *,
    status_code: int,
    content: dict[str, Any],
    request_ref: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers={
            "X-Request-Ref": request_ref,
            "Cache-Control": "no-store",
        },
    )
