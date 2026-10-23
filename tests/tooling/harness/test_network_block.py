"""AT-M0-T11-07 — pytest-socket, TZ and Hypothesis CI profile."""

from __future__ import annotations

import socket
import time
from pathlib import Path

import pytest
import pytest_socket
from hypothesis import settings

@pytest.mark.unit
@pytest.mark.trace("AT-M0-T11-07", reqs=["ARCH-R085"])
def test_unit_outbound_socket_blocked() -> None:
    with pytest.raises(pytest_socket.SocketConnectBlockedError):
        socket.create_connection(("1.0.0.1", 80), timeout=0.2)


@pytest.mark.trace("AT-M0-T11-07", reqs=["ARCH-R085"])
def test_tz_is_utc_in_test_runs() -> None:
    assert time.localtime().tm_gmtoff == 0
    assert time.strftime("%Z") in {"UTC", "GMT"}


@pytest.mark.trace("AT-M0-T11-07", reqs=["ARCH-R085"])
def test_hypothesis_ci_profile_derandomized() -> None:
    profile = settings.get_profile("ci")
    assert profile.derandomize is True
    assert profile.deadline is None
