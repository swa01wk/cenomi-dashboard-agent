"""Health report assembly (ARCH-R031)."""

from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime
from importlib.metadata import version
from typing import Any, Literal

import yaml

from cenomi.api.health_wiring import DbHealthCheckFn, get_db_health_check
from cenomi.api.services.health_types import CheckName, DbCheckResult
from cenomi.core.paths import repo_root
from cenomi.core.settings import Settings

OverallStatus = Literal["ok", "degraded", "fail"]

HEALTH_TIMEOUT_SECONDS = 2.0
DATASET_SKIPPED_DETAIL = "dataset not seeded until M1"

REQUIRED_DB_CHECKS: tuple[CheckName, ...] = (
    "db_reader",
    "db_app",
    "schemas_present",
    "role_isolation",
    "migrations_at_head",
)


def _read_spec_set_version() -> str:
    path = repo_root() / "specs" / "engineering" / "spec_set.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return str(data["version"])


def _app_info() -> dict[str, str]:
    try:
        pkg_version = version("cenomi-backend")
    except Exception:
        pkg_version = "0.0.0"
    info: dict[str, str] = {
        "version": pkg_version,
        "specSet": _read_spec_set_version(),
    }
    return info


def _check_entry(
    name: CheckName,
    *,
    required: bool,
    status: Literal["pass", "fail", "skipped"],
    duration_ms: int,
    detail: str | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "name": name,
        "required": required,
        "status": status,
        "durationMs": duration_ms,
    }
    if detail is not None:
        entry["detail"] = detail[:200]
    return entry


def _overall_status(checks: list[dict[str, Any]]) -> OverallStatus:
    required_failed = any(c["required"] and c["status"] == "fail" for c in checks)
    if required_failed:
        return "fail"
    optional_failed = any(not c["required"] and c["status"] == "fail" for c in checks)
    if optional_failed:
        return "degraded"
    return "ok"


async def _run_db_checks_with_timeout(fn: DbHealthCheckFn) -> list[DbCheckResult]:
    started = time.perf_counter()

    async def _invoke() -> list[DbCheckResult]:
        return await fn()

    try:
        return await asyncio.wait_for(_invoke(), timeout=HEALTH_TIMEOUT_SECONDS)
    except TimeoutError:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return [
            DbCheckResult(
                name="db_reader",
                required=True,
                status="fail",
                duration_ms=max(elapsed_ms, int(HEALTH_TIMEOUT_SECONDS * 1000)),
                detail="health check timed out",
            )
        ]


async def build_health_report(
    settings: Settings,
    *,
    live: bool,
    db_health_check: DbHealthCheckFn | None = None,
) -> tuple[dict[str, Any], int]:
    checks: list[dict[str, Any]] = []
    checks.append(_check_entry("process", required=True, status="pass", duration_ms=0))

    if live:
        body = {
            "status": "ok",
            "checks": checks,
            "app": _app_info(),
            "checkedAt": datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        }
        return body, 200

    provider = db_health_check or get_db_health_check()
    db_results: list[DbCheckResult]
    if provider is None:
        db_results = [
            DbCheckResult(
                name=name,
                required=True,
                status="fail",
                duration_ms=0,
                detail="database health provider not configured",
            )
            for name in REQUIRED_DB_CHECKS
        ]
    else:
        db_results = await _run_db_checks_with_timeout(provider)

    for result in db_results:
        checks.append(
            _check_entry(
                result.name,
                required=result.required,
                status=result.status,
                duration_ms=result.duration_ms,
                detail=result.detail,
            )
        )

    checks.append(
        _check_entry(
            "dataset",
            required=False,
            status="skipped",
            duration_ms=0,
            detail=DATASET_SKIPPED_DETAIL,
        )
    )

    status = _overall_status(checks)
    http_status = 503 if status == "fail" else 200
    body = {
        "status": status,
        "checks": checks,
        "app": _app_info(),
        "checkedAt": datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
    }
    return body, http_status
