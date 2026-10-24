"""Alembic environment (ARCH-R057): owner URL, version table in public."""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from cenomi.core.settings import load_settings
from cenomi.db.guards import DbOperation, GuardContext, GuardFailure, enforce_guards, refuse_guard
from cenomi.db.tables import metadata
from cenomi.db.urls import database_name_for, replace_database

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata


def include_object(
    object: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    """Ignore Alembic's own version table when metadata is empty (M0, ARCH-R058)."""
    if type_ == "table" and name == "alembic_version":
        return False
    return True


def _owner_url() -> str:
    db = os.environ.get("DB", "dev").strip().lower()
    settings = load_settings()
    name = database_name_for(db)
    url = replace_database(settings.database_url_owner.get_secret_value(), name)
    ctx = GuardContext(url=url, operation=DbOperation.MIGRATE)
    try:
        enforce_guards(ctx)
    except GuardFailure as exc:
        refuse_guard(exc.guard, exc.message)
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def run_migrations_offline() -> None:
    url = _owner_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema="public",
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _owner_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema="public",
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
