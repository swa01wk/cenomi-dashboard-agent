"""Health endpoint integration tests."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import jsonschema
import pytest
import yaml
from httpx import ASGITransport, AsyncClient

from cenomi.api.app import create_app
from cenomi.api.services.health import DATASET_SKIPPED_DETAIL
from cenomi.api.services.health_types import DbCheckResult
from cenomi.core.settings import Settings

REPO_ROOT = Path(__file__).resolve().parents[4]
HEALTH_SCHEMA = json.loads(
    (REPO_ROOT / "specs/contracts/health_report.v1.schema.json").read_text(encoding="utf-8")
)
SPEC_SET_VERSION = yaml.safe_load(
    (REPO_ROOT / "specs/engineering/spec_set.yaml").read_text(encoding="utf-8")
)["version"]


def _settings() -> Settings:
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


async def _all_pass_provider() -> list[DbCheckResult]:
    return [
        DbCheckResult(name="db_reader", required=True, status="pass", duration_ms=4),
        DbCheckResult(name="db_app", required=True, status="pass", duration_ms=3),
        DbCheckResult(name="schemas_present", required=True, status="pass", duration_ms=2),
        DbCheckResult(name="role_isolation", required=True, status="pass", duration_ms=6),
        DbCheckResult(name="migrations_at_head", required=True, status="pass", duration_ms=1),
    ]


@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T03-02", reqs=["ARCH-R031"])
async def test_health_ok_with_test_double() -> None:
    app = create_app(_settings(), db_health_check=_all_pass_provider)
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        jsonschema.validate(body, HEALTH_SCHEMA)
        assert body["status"] == "ok"
        assert body["app"]["specSet"] == SPEC_SET_VERSION
        dataset = next(item for item in body["checks"] if item["name"] == "dataset")
        assert dataset["status"] == "skipped"
        assert dataset["detail"] == DATASET_SKIPPED_DETAIL


@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T03-03", reqs=["ARCH-R031"])
async def test_health_fail_when_db_reader_fails() -> None:
    async def fail_reader() -> list[DbCheckResult]:
        return [
            DbCheckResult(
                name="db_reader",
                required=True,
                status="fail",
                duration_ms=2000,
                detail="connection refused",
            )
        ]

    app = create_app(_settings(), db_health_check=fail_reader)
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 503
        body = response.json()
        jsonschema.validate(body, HEALTH_SCHEMA)
        assert body["status"] == "fail"


@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T03-03", reqs=["ARCH-R031"])
async def test_health_fail_when_check_exceeds_two_seconds() -> None:
    async def slow_checks() -> list[DbCheckResult]:
        await asyncio.sleep(2.5)
        return [
            DbCheckResult(name="db_reader", required=True, status="pass", duration_ms=2500),
        ]

    app = create_app(_settings(), db_health_check=slow_checks)
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "fail"
