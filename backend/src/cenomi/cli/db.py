"""Database CLI commands (ARCH-R034)."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg
from psycopg import sql

from cenomi.core.logging import configure_logging
from cenomi.core.settings import load_settings
from cenomi.db.guards import DbOperation, GuardContext, GuardFailure, enforce_guards, refuse_guard
from cenomi.db.urls import database_name_for, replace_database

REPO_ROOT = Path(__file__).resolve().parents[4]
ROLES_SQL = REPO_ROOT / "infra" / "postgres" / "bootstrap" / "roles.sql"
SCHEMAS: tuple[str, ...] = ("core", "meta", "snap", "seed_meta", "agent", "insights")

logger = logging.getLogger("cenomi.cli.db")


def _password_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.password or ""


def _connect(url: str) -> psycopg.Connection:
    return psycopg.connect(url, autocommit=True)


def cmd_init(_args: argparse.Namespace) -> int:
    settings = load_settings()
    configure_logging(service="cli", env=settings.cenomi_env, level=settings.log_level)
    admin_url = settings.database_url_admin.get_secret_value()
    ctx = GuardContext(url=admin_url, operation=DbOperation.INIT)
    try:
        enforce_guards(ctx)
    except GuardFailure as exc:
        logger.info(
            "guard refused",
            extra={"event": "db_init_guard", "guard": exc.guard, "role": "admin"},
        )
        refuse_guard(exc.guard, exc.message)

    role_passwords = {
        "cenomi_owner": _password_from_url(settings.database_url_owner.get_secret_value()),
        "cenomi_seed": _password_from_url(settings.database_url_seed.get_secret_value()),
        "cenomi_reader": _password_from_url(settings.database_url_reader.get_secret_value()),
        "cenomi_app": _password_from_url(settings.database_url_app.get_secret_value()),
    }

    try:
        with _connect(admin_url) as conn:
            sql_text = ROLES_SQL.read_text(encoding="utf-8")
            conn.execute(sql_text)
            for role, password in role_passwords.items():
                conn.execute(
                    sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                        sql.Identifier(role),
                        sql.Literal(password),
                    )
                )
            for db_name in ("cenomi_dev", "cenomi_test"):
                exists = conn.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (db_name,),
                ).fetchone()
                if not exists:
                    conn.execute(
                        sql.SQL("CREATE DATABASE {} OWNER cenomi_owner").format(
                            sql.Identifier(db_name)
                        )
                    )
                conn.execute(
                    sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(sql.Identifier(db_name))
                )
                for role in role_passwords:
                    conn.execute(
                        sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                            sql.Identifier(db_name),
                            sql.Identifier(role),
                        )
                    )
    except psycopg.Error as exc:
        print(f"Database unreachable or init failed: {exc}", file=sys.stderr)
        return 3

    logger.info("db init completed", extra={"event": "db_init", "role": "admin"})
    return 0


def _bool_priv(conn: psycopg.Connection, query: str, *args: object) -> bool:
    row = conn.execute(query, args).fetchone()
    if row is None:
        return False
    return bool(row[0])


def cmd_verify_roles(args: argparse.Namespace) -> int:
    settings = load_settings()
    configure_logging(service="cli", env=settings.cenomi_env, level=settings.log_level)
    db_name = database_name_for(args.db)
    owner_url = replace_database(
        settings.database_url_owner.get_secret_value(),
        db_name,
    )
    reader_url = replace_database(
        settings.database_url_reader.get_secret_value(),
        db_name,
    )
    app_url = replace_database(
        settings.database_url_app.get_secret_value(),
        db_name,
    )
    seed_url = replace_database(
        settings.database_url_seed.get_secret_value(),
        db_name,
    )

    ctx = GuardContext(url=owner_url, operation=DbOperation.MIGRATE)
    try:
        enforce_guards(ctx)
    except GuardFailure as exc:
        refuse_guard(exc.guard, exc.message)

    try:
        with (
            _connect(owner_url) as owner,
            _connect(reader_url) as reader,
            _connect(app_url) as app,
            _connect(seed_url) as seed,
        ):
            for schema in SCHEMAS:
                if not _bool_priv(
                    owner,
                    "SELECT has_schema_privilege('cenomi_owner', %s, 'USAGE')",
                    schema,
                ):
                    print(f"owner missing USAGE on {schema}", file=sys.stderr)
                    return 1
            for schema in ("core", "meta", "snap"):
                if not _bool_priv(
                    reader,
                    "SELECT has_schema_privilege(current_user, %s, 'USAGE')",
                    schema,
                ):
                    print(f"reader missing USAGE on {schema}", file=sys.stderr)
                    return 1
            for schema in ("seed_meta", "agent", "insights"):
                if _bool_priv(
                    reader,
                    "SELECT has_schema_privilege(current_user, %s, 'USAGE')",
                    schema,
                ):
                    print(f"reader must not have USAGE on {schema}", file=sys.stderr)
                    return 1
            for schema in ("core", "meta", "snap", "seed_meta"):
                if _bool_priv(
                    app,
                    "SELECT has_schema_privilege(current_user, %s, 'USAGE')",
                    schema,
                ):
                    print(f"app must not have USAGE on {schema}", file=sys.stderr)
                    return 1
            for schema in ("agent", "insights"):
                if not _bool_priv(
                    app,
                    "SELECT has_schema_privilege(current_user, %s, 'USAGE')",
                    schema,
                ):
                    print(f"app missing USAGE on {schema}", file=sys.stderr)
                    return 1
            for schema in ("core", "meta", "snap", "seed_meta"):
                if not _bool_priv(
                    seed,
                    "SELECT has_schema_privilege(current_user, %s, 'USAGE')",
                    schema,
                ):
                    print(f"seed missing USAGE on {schema}", file=sys.stderr)
                    return 1
            ro = reader.execute("SHOW transaction_read_only").fetchone()
            if ro is None or str(ro[0]).lower() not in ("on", "true"):
                print("reader default_transaction_read_only is not on", file=sys.stderr)
                return 1
            timeout = reader.execute("SHOW statement_timeout").fetchone()
            if timeout is None or str(timeout[0]) not in ("5000", "5000ms", "5s"):
                print(f"reader statement_timeout unexpected: {timeout}", file=sys.stderr)
                return 1
    except psycopg.Error as exc:
        print(f"verify-roles failed: {exc}", file=sys.stderr)
        return 1

    logger.info(
        "verify-roles passed",
        extra={"event": "db_verify_roles", "role": "owner", "database": db_name},
    )
    return 0


def register_subcommands(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    db_parser = subparsers.add_parser("db", help="Database bootstrap and verification")
    db_sub = db_parser.add_subparsers(dest="db_command", required=True)

    init_parser = db_sub.add_parser("init", help="Create roles and databases (idempotent)")
    init_parser.set_defaults(handler=cmd_init)

    verify = db_sub.add_parser(
        "verify-roles",
        help="Verify ADR-0006 roles and grants using has_*_privilege only",
    )
    verify.add_argument(
        "--db",
        dest="db",
        default="test",
        choices=("dev", "test"),
        help="Which cenomi database to verify (default: test)",
    )
    verify.set_defaults(handler=cmd_verify_roles)
