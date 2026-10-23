"""JSON logging with redaction (ARCH-R030, ARCH-R096, ARCH-R097)."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse, urlunparse

from pydantic import SecretStr

from cenomi.core.request_context import get_request_context

_URL_PASSWORD = re.compile(r"://([^:/@]+):([^@]+)@")


class JsonLogFormatter(logging.Formatter):
    def __init__(self, *, service: str, env: str) -> None:
        super().__init__()
        self._service = service
        self._env = env

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event", "log"),
            "msg": record.getMessage(),
            "service": self._service,
            "env": self._env,
        }
        ctx = get_request_context()
        if ctx.request_ref:
            payload["requestRef"] = ctx.request_ref
        if ctx.trace_id:
            payload["traceId"] = ctx.trace_id
        if ctx.span_id:
            payload["spanId"] = ctx.span_id

        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "event",
            }:
                continue
            payload[key] = _redact_value(value)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=_redact_value)


def _redact_value(value: Any) -> Any:
    if isinstance(value, SecretStr):
        return "[REDACTED]"
    if isinstance(value, str):
        return _redact_string(value)
    if isinstance(value, dict):
        return {k: _redact_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(v) for v in value]
    return value


def _redact_string(text: str) -> str:
    if _URL_PASSWORD.search(text):
        return _URL_PASSWORD.sub(r"://\1:[REDACTED]@", text)
    try:
        parsed = urlparse(text)
        if parsed.password:
            netloc = parsed.hostname or ""
            if parsed.username:
                netloc = f"{parsed.username}:[REDACTED]@{netloc}"
            if parsed.port:
                netloc = f"{netloc}:{parsed.port}"
            return urlunparse(
                (parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
            )
    except ValueError:
        pass
    return text


def configure_logging(*, service: str, env: str, level: str) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter(service=service, env=env))
    root.addHandler(handler)
    root.setLevel(level.upper())
