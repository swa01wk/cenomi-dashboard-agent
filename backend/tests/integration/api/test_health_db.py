"""Real-database health endpoint tests (AT-M0-T02-11)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import psycopg
import pytest
import yaml
from httpx import ASGITransport, AsyncClient

from cenomi.api.app import create_app
from cenomi.api.services.health import DATASET_SKIPPED_DETAIL
from cenomi.core.settings import Settings
from cenomi.db.health import check_database
from cenomi.db.urls import replace_database

REPO_ROOT = Path(__file__).resolve().parents[4]
HEALTH_SCHEMA = json.loads(
    (REPO_ROOT / "specs/contracts/health_report.v1.schema.json").read_text(encoding="utf-8")
)
SPEC_SET_VERSION = yaml.safe_load(
    (REPO_ROOT / "specs/engineering/spec_set.yaml").read_text(encoding="utf-8")
)["version"]


def _base_settings(**overrides: object) -> Settings:
    payload = {
        "CENOMI_ENV": "test",
        "DATABASE_URL_ADMIN": "postgresql://postgres:change-me-dev-only-admin@127.0.0.1:5432/postgres",
        "DATABASE_URL_OWNER": "postgresql://cenomi_owner:change-me-dev-only-owner@127.0.0.1:5432/cenomi_test",
        "DATABASE_URL_SEED": "postgresql://cenomi_seed:change-me-dev-only-seed@127.0.0.1:5432/cenomi_test",
        "DATABASE_URL_READER": "postgresql://cenomi_reader:change-me-dev-only-reader@127.0.0.1:5432/cenomi_test",
        "DATABASE_URL_APP": "postgresql://cenomi_app:change-me-dev-only-app@127.0.0.1:5432/cenomi_test",
        "CENOMI_DATASET_ID": "sd-2026.10.20-01",
        "CENOMI_AS_OF": "2026-10-20",
        "CENOMI_TZ": "Asia/Riyadh",
        "AUTH_MODE": "dev_fixture",
        "SESSION_SECRET": "change-me-dev-only-session-secret-32b",
        "API_INTERNAL_URL": "http://localhost:8000",
    }
    payload.update(overrides)
    return Settings.model_validate(payload)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T02-11", reqs=["ARCH-R031"])
async def test_health_ok_against_migrated_test_database(test_database_name: str) -> None:
    _ = test_database_name
    settings = _base_settings()

    async def db_check() -> list:
        return await check_database(settings)

    app = create_app(settings, db_health_check=db_check)
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        jsonschema.validate(body, HEALTH_SCHEMA)
        assert body["status"] == "ok"
        assert body["app"]["specSet"] == SPEC_SET_VERSION
        for check in body["checks"]:
            if check["name"] in {
                "db_reader",
                "db_app",
                "schemas_present",
                "role_isolation",
                "migrations_at_head",
            }:
                assert check["status"] == "pass"
        dataset = next(item for item in body["checks"] if item["name"] == "dataset")
        assert dataset["status"] == "skipped"
        assert dataset["detail"] == DATASET_SKIPPED_DETAIL


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T02-11", reqs=["ARCH-R031"])
async def test_health_fail_when_reader_port_closed() -> None:
    settings = _base_settings(
        DATABASE_URL_READER="postgresql://cenomi_reader:change-me-dev-only-reader@127.0.0.1:59999/cenomi_test",
        DATABASE_URL_APP="postgresql://cenomi_app:change-me-dev-only-app@127.0.0.1:5432/cenomi_test",
    )

    async def db_check() -> list:
        return await check_database(settings)

    app = create_app(settings, db_health_check=db_check)
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 503
        body = response.json()
        jsonschema.validate(body, HEALTH_SCHEMA)
        assert body["status"] == "fail"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.trace("AT-M0-T02-11", reqs=["ARCH-R031"])
async def test_health_fail_when_migrations_not_at_head(
    test_database_name: str,
    db_connection: psycopg.Connection,
) -> None:
    db_connection.execute("UPDATE public.alembic_version SET version_num = '0000_not_head'")
    db_connection.commit()
    settings = _base_settings()
    reader_url = replace_database(
        settings.database_url_reader.get_secret_value(),
        test_database_name,
    )
    settings = _base_settings(
        DATABASE_URL_READER=reader_url,
        DATABASE_URL_APP=replace_database(
            settings.database_url_app.get_secret_value(),
            test_database_name,
        ),
    )

    async def db_check() -> list:
        return await check_database(settings)

    app = create_app(settings, db_health_check=db_check)
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "fail"
    db_connection.execute(
        "UPDATE public.alembic_version SET version_num = '0001_m0_schemas_and_grants'"
    )
    db_connection.commit()
