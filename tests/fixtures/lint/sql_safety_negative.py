"""Negative fixture for sql_safety lint (AT-M0-T03-09)."""

from sqlalchemy import text

table = "users"
query = text(f"SELECT 1 FROM {table}")  # noqa: F841
