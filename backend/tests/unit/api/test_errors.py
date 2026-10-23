"""API error envelope tests."""

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
ERROR_SCHEMA = json.loads(
    (REPO_ROOT / "specs/contracts/error_envelope.v1.schema.json").read_text(encoding="utf-8")
)
GENERIC_INTERNAL_MESSAGE = "Something went wrong."
VALIDATION_MESSAGE = "The request is not valid."


def _test_settings() -> Settings:
    return Settings.model_validate(
        {
            "CENOMI_ENV": "test",
            "DATABASE_URL_ADMIN": "postgresql://postgres:change-me-dev-only-admin@localhost:5432/postgres",
            "DATABASE_URL_OWNER": "postgresql://cenomi_owner:change-me-dev-only-owner@localhost:5432/cenomi_dev",
            "DATABASE_URL_SEED": "postgresql://cenomi_seed:change-me-dev-only-seed@localhost:5432/cenomi_dev",
            "DATABASE_URL_READER": "postgresql://cenomi_reader:change-me-dev-only-reader@localhost:5432/cenomi_dev",
            "DATABASE_URL_APP": "postgresql://cenomi_app:change-me-dev-only-app@localhost:5432/cenomi_dev",
            "CENOMI_DATASET_ID": "sd-2026.10.20-01",
            "CENOMI_AS_OF": "2026-10-20",
            "CENOMI_TZ": "Asia/Riyadh",
            "AUTH_MODE": "dev_fixture",
            "SESSION_SECRET": "change-me-dev-only-session-secret-32b",
            "API_INTERNAL_URL": "http://localhost:8000",
        }
    )


def _validate_envelope(body: dict) -> None:
    jsonschema.validate(body, ERROR_SCHEMA)


@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T03-05", reqs=["ARCH-R014", "ARCH-R015", "ARCH-R020"])
async def test_non_2xx_responses_are_valid_error_envelopes() -> None:
    app = create_app(_test_settings(), include_debug_routes=True)
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        unknown = await client.get("/api/v1/dataset", params={"unexpected": "secret-value-xyz"})
        assert unknown.status_code == 400
        assert unknown.status_code != 422
        body = unknown.json()
        _validate_envelope(body)
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert body["error"]["message"] == VALIDATION_MESSAGE
        assert body["error"]["requestRef"] == unknown.headers["X-Request-Ref"]
        assert "secret-value-xyz" not in json.dumps(body)
        assert body["error"]["details"][0]["path"] == "query.unexpected"
        assert body["error"]["details"][0]["rule"] == "unknown_field"

        missing = await client.get("/api/v1/does-not-exist")
        assert missing.status_code == 404
        missing_body = missing.json()
        _validate_envelope(missing_body)
        assert missing_body["error"]["requestRef"] == missing.headers["X-Request-Ref"]


@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T03-06", reqs=["ARCH-R023", "ARCH-R025"])
async def test_unhandled_exception_returns_internal_and_logs_stack(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.ERROR, logger="cenomi.api.exception_handlers")
    app = create_app(_test_settings(), include_debug_routes=True)
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/debug/unhandled")
        assert response.status_code == 500
        body = response.json()
        _validate_envelope(body)
        assert body["error"]["code"] == "INTERNAL"
        assert body["error"]["message"] == GENERIC_INTERNAL_MESSAGE
        assert body["error"]["requestRef"] == response.headers["X-Request-Ref"]
        assert "RuntimeError" not in json.dumps(body)
        assert "debug unhandled" not in json.dumps(body)

        request_ref = response.headers["X-Request-Ref"]
        assert any(
            request_ref in record.message or request_ref in str(record.__dict__)
            for record in caplog.records
        )
        assert any(record.exc_info is not None for record in caplog.records)
