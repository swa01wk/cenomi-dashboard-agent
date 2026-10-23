"""Logging formatter tests."""

from __future__ import annotations

import json
import logging

import pytest
from pydantic import SecretStr

from cenomi.core.logging import JsonLogFormatter, configure_logging
from cenomi.core.request_context import RequestContext, set_request_context


@pytest.mark.trace("AT-M0-T03-07", reqs=["ARCH-R096", "ARCH-R097"])
def test_json_log_redacts_secrets_and_url_passwords() -> None:
    configure_logging(service="api", env="test", level="INFO")
    formatter = JsonLogFormatter(service="api", env="test")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="database url %s",
        args=(SecretStr("postgresql://reader:secret-pass@localhost:5432/cenomi_dev"),),
        exc_info=None,
    )
    record.event = "test_event"
    record.token = SecretStr("abc")
    line = formatter.format(record)
    payload = json.loads(line)
    assert payload["service"] == "api"
    assert payload["env"] == "test"
    assert payload["event"] == "test_event"
    assert "secret-pass" not in line
    assert "[REDACTED]" in line


def test_request_context_fields_emitted_in_json_logs() -> None:
    configure_logging(service="api", env="test", level="INFO")
    formatter = JsonLogFormatter(service="api", env="test")
    set_request_context(
        RequestContext(
            request_ref="req_0123456789abcdef",
            trace_id="4bf92f3577b34da6a3ce929d0e0e4736",
            span_id="00f067aa0ba902b7",
        )
    )
    record = logging.LogRecord(
        name="cenomi.api.request",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request handled",
        args=(),
        exc_info=None,
    )
    record.event = "request_completed"
    line = formatter.format(record)
    payload = json.loads(line)
    assert payload["traceId"] == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert payload["requestRef"] == "req_0123456789abcdef"
