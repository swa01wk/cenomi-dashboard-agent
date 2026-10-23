"""Renderer drift checks (M0-T10, AT-M0-T10-03)."""

from __future__ import annotations

import pytest

from scripts.docs.render_engineering_tables import check_drift as engineering_drift
from scripts.docs.render_register import check_drift as register_drift

pytestmark = pytest.mark.trace("AT-M0-T10-03", reqs=["DEVENV-R011", "DREG-R002"])


def test_engineering_tables_match_committed() -> None:
    assert engineering_drift() == []


def test_decision_register_section2_matches_committed() -> None:
    assert register_drift() == []
