"""Tests for application status transition guard can_transition."""

from __future__ import annotations

import pytest

from app.db.models import UserRole
from app.workflow import ApplicationStatus, can_transition


@pytest.mark.parametrize(
    ("from_s", "to_s", "role", "expected"),
    [
        ("DRAFT", "SUBMITTED_ONLINE", UserRole.INSTITUTION, True),
        ("DRAFT", "SUBMITTED_ONLINE", UserRole.DEALING_HAND, False),
        ("SUBMITTED_ONLINE", "HARDCOPY_DISPATCHED", UserRole.INSTITUTION, True),
        ("HARDCOPY_DISPATCHED", "HARDCOPY_RECEIVED", UserRole.DEALING_HAND, True),
        ("SUBMITTED_ONLINE", "HARDCOPY_RECEIVED", UserRole.DEALING_HAND, True),
        ("HARDCOPY_RECEIVED", "UNDER_SCRUTINY", UserRole.DEALING_HAND, True),
        ("UNDER_SCRUTINY", "DEFICIENCY_RAISED", UserRole.DEALING_HAND, True),
        ("DEFICIENCY_RAISED", "UNDER_SCRUTINY", UserRole.DEALING_HAND, True),
        ("UNDER_SCRUTINY", "SCRUTINY_CLEARED", UserRole.DEALING_HAND, True),
        ("HARDCOPY_RECEIVED", "SCRUTINY_CLEARED", UserRole.DEALING_HAND, True),
        ("DRAFT", "HARDCOPY_RECEIVED", UserRole.DEALING_HAND, False),
        ("MOM_FINALIZED", "DECISION_ISSUED", UserRole.AUTHORITY, True),
        ("MOM_FINALIZED", "DECISION_ISSUED", UserRole.DEALING_HAND, False),
    ],
)
def test_can_transition(from_s: str, to_s: str, role: UserRole, expected: bool) -> None:
    assert can_transition(from_s, to_s, role) is expected
