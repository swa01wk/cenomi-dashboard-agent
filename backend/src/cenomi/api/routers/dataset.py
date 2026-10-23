"""Dataset descriptor route."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from cenomi.core.settings import Settings

router = APIRouter(prefix="/api/v1", tags=["dataset"])


@router.get("/dataset")
async def dataset_descriptor(request: Request) -> JSONResponse:
    settings: Settings = request.app.state.settings
    body = {
        "datasetId": settings.cenomi_dataset_id,
        "asOf": settings.cenomi_as_of.isoformat(),
        "timezone": settings.cenomi_tz,
        "synthetic": True,
        "source": "config",
        "state": "declared",
    }
    return JSONResponse(content=body)
