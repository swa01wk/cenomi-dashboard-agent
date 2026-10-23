"""Health routes (ARCH-R031)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from cenomi.api.health_wiring import DbHealthCheckFn
from cenomi.api.services.health import build_health_report
from cenomi.core.settings import Settings

router = APIRouter(prefix="/api/v1", tags=["health"])


def _settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def _db_override(request: Request) -> DbHealthCheckFn | None:
    return getattr(request.app.state, "db_health_check", None)


@router.get("/health/live")
async def health_live(request: Request) -> JSONResponse:
    body, status = await build_health_report(_settings(request), live=True)
    return JSONResponse(content=body, status_code=status)


@router.get("/health")
async def health(request: Request) -> JSONResponse:
    body, status = await build_health_report(
        _settings(request),
        live=False,
        db_health_check=_db_override(request),
    )
    return JSONResponse(content=body, status_code=status)
