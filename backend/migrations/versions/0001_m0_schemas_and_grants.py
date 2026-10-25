"""M0 baseline schemas and grants (ADR-0006 §3, ARCH-R062)."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0001_m0_schemas_and_grants"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCHEMAS = ("core", "meta", "snap", "seed_meta", "agent", "insights")
_SEED_SCHEMAS = ("core", "meta", "snap", "seed_meta")
_READER_SCHEMAS = ("core", "meta", "snap")
_APP_SCHEMAS = ("agent", "insights")


def _grant_seed(schema: str) -> None:
    op.execute(f"GRANT USAGE ON SCHEMA {schema} TO cenomi_seed")
    op.execute(
        f"GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA {schema} "
        "TO cenomi_seed"
    )
    op.execute(f"GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA {schema} TO cenomi_seed")
    op.execute(
        f"ALTER DEFAULT PRIVILEGES FOR ROLE cenomi_owner IN SCHEMA {schema} "
        "GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO cenomi_seed"
    )
    op.execute(
        f"ALTER DEFAULT PRIVILEGES FOR ROLE cenomi_owner IN SCHEMA {schema} "
        "GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO cenomi_seed"
    )


def _grant_reader(schema: str) -> None:
    op.execute(f"GRANT USAGE ON SCHEMA {schema} TO cenomi_reader")
    op.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO cenomi_reader")
    op.execute(
        f"ALTER DEFAULT PRIVILEGES FOR ROLE cenomi_owner IN SCHEMA {schema} "
        "GRANT SELECT ON TABLES TO cenomi_reader"
    )


def _grant_app(schema: str) -> None:
    op.execute(f"GRANT USAGE ON SCHEMA {schema} TO cenomi_app")
    op.execute(
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {schema} TO cenomi_app"
    )
    op.execute(f"GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA {schema} TO cenomi_app")
    op.execute(
        f"ALTER DEFAULT PRIVILEGES FOR ROLE cenomi_owner IN SCHEMA {schema} "
        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO cenomi_app"
    )
    op.execute(
        f"ALTER DEFAULT PRIVILEGES FOR ROLE cenomi_owner IN SCHEMA {schema} "
        "GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO cenomi_app"
    )


def upgrade() -> None:
    for schema in _SCHEMAS:
        op.execute(f"CREATE SCHEMA {schema} AUTHORIZATION cenomi_owner")

    for schema in _SEED_SCHEMAS:
        _grant_seed(schema)
    for schema in _READER_SCHEMAS:
        _grant_reader(schema)
    for schema in _APP_SCHEMAS:
        _grant_app(schema)

    op.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA public TO cenomi_reader")
    op.execute("GRANT SELECT ON TABLE public.alembic_version TO cenomi_reader")


def downgrade() -> None:
    op.execute("REVOKE SELECT ON TABLE public.alembic_version FROM cenomi_reader")
    op.execute("REVOKE USAGE ON SCHEMA public FROM cenomi_reader")
    for schema in reversed(_SCHEMAS):
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
