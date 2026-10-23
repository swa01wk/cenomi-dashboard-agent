"""Dataset descriptor endpoint tests."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import jsonschema
import pytest
from httpx import ASGITransport, AsyncClient

from cenomi.api.app import create_app
from cenomi.core.settings import Settings

REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_SCHEMA = json.loads(
    (REPO_ROOT / "specs/contracts/dataset_descriptor.v1.schema.json").read_text(encoding="utf-8")
)
EXPECTED = DATASET_SCHEMA["examples"][0]


def _settings() -> Settings:
    return Settings.model_validate(
        {
            "CENOMI_ENV": "test",
            "DATABASE_URL_ADMIN": "postgresql://postgres:change-me-dev-only-admin@localhost:5432/postgres",
            "DATABASE_URL_OWNER": "postgresql://cenomi_owner:change-me-dev-only-owner@localhost:5432/cenomi_dev",
            "DATABASE_URL_SEED": "postgresql://cenomi_seed:change-me-dev-only-seed@localhost:5432/cenomi_dev",
            "DATABASE_URL_READER": "postgresql://cenomi_reader:change-me-dev-only-reader@localhost:5432/cenomi_dev",
            "DATABASE_URL_APP": "postgresql://cenomi_app:change-me-dev-only-app@localhost:5432/cenomi_dev",
            "CENOMI_DATASET_ID": EXPECTED["datasetId"],
            "CENOMI_AS_OF": EXPECTED["asOf"],
            "CENOMI_TZ": EXPECTED["timezone"],
            "AUTH_MODE": "dev_fixture",
            "SESSION_SECRET": "change-me-dev-only-session-secret-32b",
            "API_INTERNAL_URL": "http://localhost:8000",
        }
    )


@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T03-08", reqs=["ARCH-R028"])
async def test_dataset_descriptor_from_config() -> None:
    app = create_app(_settings())
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/dataset")
        assert response.status_code == 200
        body = response.json()
        jsonschema.validate(body, DATASET_SCHEMA)
        assert body == EXPECTED


@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T03-10", reqs=["ARCH-R021", "ARCH-R096"])
async def test_incoming_traceparent_appears_in_request_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="cenomi.api.request")
    app = create_app(_settings())
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.get("/api/v1/dataset", headers={"traceparent": traceparent})

    assert any(
        getattr(record, "traceId", None) == "4bf92f3577b34da6a3ce929d0e0e4736"
        for record in caplog.records
    )
