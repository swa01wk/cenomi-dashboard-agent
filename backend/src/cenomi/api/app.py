"""FastAPI application factory (ARCH-R008)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from cenomi.api.exception_handlers import register_exception_handlers
from cenomi.api.health_wiring import DbHealthCheckFn
from cenomi.api.middleware.query_params import UnknownQueryParamsMiddleware
from cenomi.api.middleware.request_logging import RequestContextMiddleware
from cenomi.api.routers import dataset, health
from cenomi.core.logging import configure_logging
from cenomi.core.settings import Settings, load_settings
from cenomi.core.telemetry import configure_telemetry


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    configure_logging(service="api", env=settings.cenomi_env, level=settings.log_level)
    configure_telemetry(settings)
    yield


def create_app(
    settings: Settings | None = None,
    *,
    db_health_check: DbHealthCheckFn | None = None,
    include_debug_routes: bool = False,
) -> FastAPI:
    resolved = settings or load_settings()
    app = FastAPI(
        title="Cenomi API",
        lifespan=_lifespan,
        openapi_url=None,
    )
    app.state.settings = resolved
    app.state.db_health_check = db_health_check

    app.add_middleware(UnknownQueryParamsMiddleware)
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(dataset.router)

    if include_debug_routes:

        @app.get("/api/v1/debug/unhandled", include_in_schema=False)
        async def _debug_unhandled() -> None:
            raise RuntimeError("debug unhandled exception")

    return app
