"""Unit test configuration."""

from __future__ import annotations


def pytest_configure(config: object) -> None:

    config.addinivalue_line(  # type: ignore[attr-defined]
        "markers",
        "trace(at_id, reqs): traceability marker for acceptance tests",
    )
