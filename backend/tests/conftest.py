"""Backend pytest configuration (M0-T11)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from hypothesis import HealthCheck, settings

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

pytest_plugins = [
    "scripts.testing.pytest_trace",
]

settings.register_profile(
    "ci",
    derandomize=True,
    deadline=None,
    suppress_health_check=list(HealthCheck),
)
settings.register_profile("default", derandomize=False)


def pytest_configure(config: pytest.Config) -> None:
    os.environ.setdefault("TZ", "UTC")
    if hasattr(config, "_metadata"):
        config._metadata["TZ"] = os.environ.get("TZ", "")
    if os.environ.get("CI", "").lower() in {"1", "true", "yes"}:
        settings.load_profile("ci")
    else:
        settings.load_profile("default")
