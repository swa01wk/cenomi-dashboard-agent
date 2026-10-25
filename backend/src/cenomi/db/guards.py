"""Database safety guards DG-1 to DG-5 (ARCH-R064)."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlparse

from cenomi.db.urls import is_allowed_database_name, parse_database, parse_host

_ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "db", "postgres"})
_ALLOWED_ENVS = frozenset({"dev", "test", "ci"})


class GuardFailure(Exception):
    def __init__(self, guard: str, message: str) -> None:
        super().__init__(message)
        self.guard = guard
        self.message = message


class DbOperation(StrEnum):
    INIT = "init"
    MIGRATE = "migrate"
    SEED = "seed"
    DOWNGRADE = "downgrade"
    SEED_RESET = "seed_reset"


@dataclass(frozen=True)
class GuardContext:
    url: str
    operation: DbOperation
    require_confirm: bool = False


def _check_dg1(url: str) -> None:
    host = parse_host(url)
    if host not in _ALLOWED_HOSTS:
        raise GuardFailure("DG-1", f"host {host!r} is not allowed for local database operations")


def _check_dg2(url: str) -> None:
    name = parse_database(url)
    if not is_allowed_database_name(name):
        raise GuardFailure(
            "DG-2",
            f"database name {name!r} does not match ^cenomi_(dev|test)(_[a-z0-9]+)?$",
        )


def _check_dg3() -> None:
    env = os.environ.get("CENOMI_ENV", "").strip().lower()
    if env not in _ALLOWED_ENVS:
        raise GuardFailure("DG-3", f"CENOMI_ENV must be dev, test or ci (got {env!r})")


def _check_dg4(database_name: str) -> None:
    if os.environ.get("CONFIRM", "").strip().lower() == "yes":
        return
    if sys.stdin.isatty():
        typed = input(f"Type the database name to confirm ({database_name}): ").strip()
        if typed == database_name:
            return
    raise GuardFailure(
        "DG-4",
        "destructive operation requires CONFIRM=yes or interactive confirmation",
    )


def _role_from_url(url: str) -> str:
    user = urlparse(url).username
    if not user:
        raise GuardFailure("DG-5", "database URL must include a role name")
    return user


def _check_dg5(url: str, operation: DbOperation) -> None:
    role = _role_from_url(url)
    if operation in (DbOperation.INIT, DbOperation.SEED_RESET):
        if role not in ("postgres", "cenomi_admin"):
            raise GuardFailure("DG-5", f"operation {operation.value} requires a superuser role")
        return
    if operation in (DbOperation.MIGRATE, DbOperation.DOWNGRADE):
        if role != "cenomi_owner":
            raise GuardFailure("DG-5", f"operation {operation.value} requires role cenomi_owner")
        return
    if operation == DbOperation.SEED:
        if role != "cenomi_seed":
            raise GuardFailure("DG-5", f"operation {operation.value} requires role cenomi_seed")


def guards_for_operation(operation: DbOperation) -> tuple[str, ...]:
    if operation == DbOperation.INIT:
        return ("DG-1", "DG-3", "DG-5")
    if operation == DbOperation.MIGRATE:
        return ("DG-1", "DG-2", "DG-3", "DG-5")
    if operation == DbOperation.DOWNGRADE:
        return ("DG-1", "DG-2", "DG-3", "DG-4", "DG-5")
    if operation == DbOperation.SEED:
        return ("DG-1", "DG-2", "DG-3", "DG-5")
    if operation == DbOperation.SEED_RESET:
        return ("DG-1", "DG-2", "DG-3", "DG-4", "DG-5")
    raise AssertionError(f"unknown operation {operation!r}")


def enforce_guards(ctx: GuardContext) -> None:
    active = set(guards_for_operation(ctx.operation))
    if "DG-1" in active:
        _check_dg1(ctx.url)
    if "DG-2" in active:
        _check_dg2(ctx.url)
    if "DG-3" in active:
        _check_dg3()
    if "DG-4" in active and ctx.require_confirm:
        _check_dg4(parse_database(ctx.url))
    if "DG-5" in active:
        _check_dg5(ctx.url, ctx.operation)


def refuse_guard(guard: str, message: str) -> None:
    print(f"Guard {guard} failed: {message}", file=sys.stderr)
    raise SystemExit(2)
