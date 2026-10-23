"""AT-M0-T11-07 — pytest-socket, TZ and Hypothesis CI profile."""

from __future__ import annotations

import os
import socket
from pathlib import Path

import pytest
import pytest_socket
from hypothesis import settings

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND = REPO_ROOT / "backend"


@pytest.mark.unit
@pytest.mark.trace("AT-M0-T11-07", reqs=["ARCH-R085"])
def test_unit_outbound_socket_blocked() -> None:
    with pytest.raises(pytest_socket.SocketConnectBlockedError):
        socket.create_connection(("1.0.0.1", 80), timeout=0.2)


@pytest.mark.trace("AT-M0-T11-07", reqs=["ARCH-R085"])
def test_tz_is_utc_in_test_runs() -> None:
    assert os.environ.get("TZ") == "UTC"


@pytest.mark.trace("AT-M0-T11-07", reqs=["ARCH-R085"])
def test_hypothesis_ci_profile_derandomized() -> None:
    assert settings.get_profile("ci").derandomize is True
