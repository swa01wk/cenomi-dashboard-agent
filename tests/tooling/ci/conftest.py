"""CI tooling pytest hooks (M0-T07)."""

from __future__ import annotations

import os

import pytest


def live_summary_test_selected() -> bool:
    gha = os.environ.get("GITHUB_ACTIONS", "").strip().lower() == "true"
    live = os.environ.get("CENOMI_CI_SUMMARY_LIVE", "").strip() == "1"
    return gha and live


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if live_summary_test_selected():
        return
    remaining: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        if item.path and item.path.name == "test_live_run.py":
            deselected.append(item)
        else:
            remaining.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = remaining
