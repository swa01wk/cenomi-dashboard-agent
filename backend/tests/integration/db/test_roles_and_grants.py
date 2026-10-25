"""ADR-0006 role and grant integration tests (AT-M0-T02-02 … AT-M0-T02-06)."""

from __future__ import annotations

from collections.abc import Iterator

import psycopg
import pytest
from psycopg import sql

from cenomi.core.settings import load_settings
from cenomi.db.urls import replace_database

SCHEMAS = ("core", "meta", "snap", "seed_meta", "agent", "insights")
_PROBE_TABLES = (
    ("core", "m0_probe"),
    ("core", "m0_later"),
    ("agent", "m0_probe"),
    ("seed_meta", "m0_probe"),
)


def _drop_probe_tables(conn: psycopg.Connection) -> None:
    for schema, table in _PROBE_TABLES:
        conn.execute(
            psycopg.sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(
                psycopg.sql.Identifier(schema),
                psycopg.sql.Identifier(table),
            )
        )
    conn.commit()


@pytest.fixture(autouse=True)
def _probe_table_cleanup(db_connection: psycopg.Connection) -> Iterator[None]:
    _drop_probe_tables(db_connection)
    yield
    _drop_probe_tables(db_connection)


def _url(role: str, database: str) -> str:
    settings = load_settings()
    mapping = {
        "owner": settings.database_url_owner.get_secret_value(),
        "reader": settings.database_url_reader.get_secret_value(),
        "app": settings.database_url_app.get_secret_value(),
        "seed": settings.database_url_seed.get_secret_value(),
    }
    return replace_database(mapping[role], database)


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.trace("AT-M0-T02-02", reqs=["ARCH-R062"])
def test_schemas_exist_without_tables(
    test_database_name: str,
    db_connection: psycopg.Connection,
) -> None:
    for schema in SCHEMAS:
        row = db_connection.execute(
            """
            SELECT n.nspname, pg_catalog.pg_get_userbyid(n.nspowner) AS owner
            FROM pg_catalog.pg_namespace n
            WHERE n.nspname = %s
            """,
            (schema,),
        ).fetchone()
        assert row is not None
        assert row[0] == schema
        assert row[1] == "cenomi_owner"
        count = db_connection.execute(
            """
            SELECT count(*) FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            """,
            (schema,),
        ).fetchone()
        assert count is not None
        assert int(count[0]) == 0


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.trace("AT-M0-T02-03", reqs=["ARCH-R032"])
def test_reader_read_only_and_schema_denials(
    test_database_name: str,
    db_connection: psycopg.Connection,
) -> None:
    db_connection.execute(
        sql.SQL("CREATE TABLE {}.m0_probe (id int PRIMARY KEY)").format(sql.Identifier("core"))
    )
    db_connection.commit()
    with psycopg.connect(_url("reader", test_database_name)) as reader:
        ro = reader.execute("SHOW transaction_read_only").fetchone()
        assert ro is not None and str(ro[0]).lower() in ("on", "true")
        timeout = reader.execute("SHOW statement_timeout").fetchone()
        assert timeout is not None and str(timeout[0]) in ("5000", "5000ms", "5s")
        for schema in ("seed_meta", "agent", "insights"):
            usage = reader.execute(
                "SELECT has_schema_privilege(current_user, %s, 'USAGE')",
                (schema,),
            ).fetchone()
            assert usage is not None and not usage[0]
        with pytest.raises(
            (psycopg.errors.InsufficientPrivilege, psycopg.errors.ReadOnlySqlTransaction)
        ):
            reader.execute("INSERT INTO core.m0_probe (id) VALUES (1)")


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.trace("AT-M0-T02-04", reqs=["ARCH-R062"])
def test_app_agent_default_privileges(
    test_database_name: str,
    db_connection: psycopg.Connection,
) -> None:
    db_connection.execute(
        sql.SQL("CREATE TABLE {}.m0_probe (id int PRIMARY KEY)").format(sql.Identifier("agent"))
    )
    db_connection.commit()
    with psycopg.connect(_url("app", test_database_name)) as app:
        for schema in ("core", "meta", "snap", "seed_meta"):
            usage = app.execute(
                "SELECT has_schema_privilege(current_user, %s, 'USAGE')",
                (schema,),
            ).fetchone()
            assert usage is not None and not usage[0]
        app.execute("INSERT INTO agent.m0_probe (id) VALUES (1)")


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.trace("AT-M0-T02-05", reqs=["ARCH-R062"])
def test_seed_meta_readable_only_by_seed_and_owner(
    test_database_name: str,
    db_connection: psycopg.Connection,
) -> None:
    db_connection.execute(
        sql.SQL("CREATE TABLE {}.m0_probe (id int PRIMARY KEY)").format(sql.Identifier("seed_meta"))
    )
    db_connection.execute("INSERT INTO seed_meta.m0_probe (id) VALUES (1)")
    db_connection.commit()

    with psycopg.connect(_url("seed", test_database_name)) as seed:
        row = seed.execute("SELECT id FROM seed_meta.m0_probe").fetchone()
        assert row == (1,)

    with psycopg.connect(_url("owner", test_database_name)) as owner:
        row = owner.execute("SELECT id FROM seed_meta.m0_probe").fetchone()
        assert row == (1,)

    with psycopg.connect(_url("reader", test_database_name)) as reader:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            reader.execute("SELECT id FROM seed_meta.m0_probe")

    with psycopg.connect(_url("app", test_database_name)) as app:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            app.execute("SELECT id FROM seed_meta.m0_probe")


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.trace("AT-M0-T02-06", reqs=["ARCH-R062"])
def test_reader_inherits_default_select_on_new_core_table(
    test_database_name: str,
    db_connection: psycopg.Connection,
) -> None:
    db_connection.execute(
        sql.SQL("CREATE TABLE {}.m0_later (id int PRIMARY KEY)").format(sql.Identifier("core"))
    )
    db_connection.execute("INSERT INTO core.m0_later (id) VALUES (42)")
    db_connection.commit()
    with psycopg.connect(_url("reader", test_database_name)) as reader:
        row = reader.execute("SELECT id FROM core.m0_later").fetchone()
        assert row == (42,)
