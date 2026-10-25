"""Database URL helpers (DEVENV-R010)."""

from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

_DB_NAME = re.compile(r"^cenomi_(dev|test)(_[a-z0-9]+)?$")


def database_name_for(db: str) -> str:
    token = db.strip().lower()
    if token not in ("dev", "test"):
        raise ValueError(f"DB must be dev or test, got {db!r}")
    return f"cenomi_{token}"


def replace_database(url: str, database: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(path=f"/{database}"))


def parse_host(url: str) -> str:
    host = urlparse(url).hostname
    if host is None:
        raise ValueError("database URL must include a host")
    return host


def parse_database(url: str) -> str:
    path = urlparse(url).path.lstrip("/")
    if not path:
        raise ValueError("database URL must include a database name")
    return path


def is_allowed_database_name(name: str) -> bool:
    return _DB_NAME.fullmatch(name) is not None
