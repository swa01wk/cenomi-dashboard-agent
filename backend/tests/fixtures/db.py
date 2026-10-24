"""Per-worker test databases and transactional rollback (ARCH-R065)."""

from __future__ import annotations

import os
import re
import secrets
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import psycopg
import pytest
from psycopg import sql

from cenomi.core.settings import get_settings, load_settings
from cenomi.db.engines import clear_engine_caches
from cenomi.db.guards import DbOperation, GuardContext, enforce_guards
from cenomi.db.urls import replace_database

REPO_ROOT = Path(__file__).resolve().parents[3]
_WORKER_DB = re.compile(r"^cenomi_test_gw\d+$")


def _load_repo_dotenv() -> None:
    dotenv = REPO_ROOT / ".env"
    if not dotenv.is_file():
        return
    for raw in dotenv.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        name = key.strip()
        val = value.strip()
        if val or name not in os.environ:
            os.environ[name] = val
    secret = os.environ.get("SESSION_SECRET", "")
    if len(secret.encode("utf-8")) < 32:
        os.environ["SESSION_SECRET"] = secrets.token_urlsafe(32)


def pytest_configure(config: pytest.Config) -> None:
    del config
    _load_repo_dotenv()
    get_settings.cache_clear()


def _worker_database_name(config: pytest.Config) -> str:
    worker = getattr(config, "workerinput", None)
    if worker is not None:
        wid = worker.get("workerid", "gw0")
        return f"cenomi_test_{wid}"
    return "cenomi_test"


def _admin_url() -> str:
    return load_settings().database_url_admin.get_secret_value()


def _owner_url(database: str) -> str:
    settings = load_settings()
    url = replace_database(settings.database_url_owner.get_secret_value(), database)
    ctx = GuardContext(url=url, operation=DbOperation.MIGRATE)
    enforce_guards(ctx)
    return url


def _ensure_worker_database(name: str) -> None:
    if not _WORKER_DB.fullmatch(name) and name != "cenomi_test":
        return
    admin = _admin_url()
    ctx = GuardContext(url=admin, operation=DbOperation.INIT)
    enforce_guards(ctx)
    with psycopg.connect(admin, autocommit=True) as conn:
        stale = conn.execute(
            """
            SELECT datname FROM pg_database
            WHERE datname LIKE 'cenomi_test_gw%%'
            """
        ).fetchall()
        for (stale_name,) in stale:
            if stale_name == name:
                continue
            conn.execute(
                sql.SQL(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = %s AND pid <> pg_backend_pid()"
                ),
                (stale_name,),
            )
            conn.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(stale_name)))

        template_exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = 'cenomi_test'"
        ).fetchone()
        if name != "cenomi_test" and template_exists:
            exists = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (name,),
            ).fetchone()
            if not exists:
                conn.execute(
                    sql.SQL("CREATE DATABASE {} TEMPLATE cenomi_test").format(sql.Identifier(name))
                )


def _set_test_database_env(database: str) -> None:
    settings = load_settings()
    for key, url in (
        ("DATABASE_URL_OWNER", settings.database_url_owner.get_secret_value()),
        ("DATABASE_URL_SEED", settings.database_url_seed.get_secret_value()),
        ("DATABASE_URL_READER", settings.database_url_reader.get_secret_value()),
        ("DATABASE_URL_APP", settings.database_url_app.get_secret_value()),
    ):
        os.environ[key] = replace_database(url, database)
    get_settings.cache_clear()
    clear_engine_caches()


@pytest.fixture(scope="session")
def test_database_name(pytestconfig: pytest.Config) -> str:
    name = _worker_database_name(pytestconfig)
    _ensure_worker_database(name)
    _set_test_database_env(name)
    return name


@pytest.fixture
def db_connection(test_database_name: str) -> Iterator[psycopg.Connection]:
    owner_url = _owner_url(test_database_name)
    with psycopg.connect(owner_url, autocommit=False) as conn:
        yield conn
        conn.rollback()


@pytest.fixture
async def reader_connection(test_database_name: str) -> AsyncIterator[None]:
    _ = test_database_name
    yield
