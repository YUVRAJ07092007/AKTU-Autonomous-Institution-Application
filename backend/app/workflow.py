"""Application lifecycle status machine and transition guards."""

from __future__ import annotations

from enum import Enum
from typing import Set, Tuple

from app.db.models import UserRole


class ApplicationStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED_ONLINE = "SUBMITTED_ONLINE"
    HARDCOPY_DISPATCHED = "HARDCOPY_DISPATCHED"
    HARDCOPY_RECEIVED = "HARDCOPY_RECEIVED"
    UNDER_SCRUTINY = "UNDER_SCRUTINY"
    DEFICIENCY_RAISED = "DEFICIENCY_RAISED"
    SCRUTINY_CLEARED = "SCRUTINY_CLEARED"
    COMMITTEE_CONSTITUTED = "COMMITTEE_CONSTITUTED"
    MEETING_SCHEDULED = "MEETING_SCHEDULED"
    MOM_DRAFT_GENERATED = "MOM_DRAFT_GENERATED"
    MOM_FINALIZED = "MOM_FINALIZED"
    DECISION_ISSUED = "DECISION_ISSUED"
    CLOSED = "CLOSED"


# (from_status, to_status, role) allowed. Role is UserRole.value.
_ALLOWED: Set[Tuple[str, str, str]] = {
    (ApplicationStatus.DRAFT.value, ApplicationStatus.SUBMITTED_ONLINE.value, UserRole.INSTITUTION.value),
    (ApplicationStatus.SUBMITTED_ONLINE.value, ApplicationStatus.HARDCOPY_DISPATCHED.value, UserRole.INSTITUTION.value),
    (ApplicationStatus.HARDCOPY_DISPATCHED.value, ApplicationStatus.HARDCOPY_RECEIVED.value, UserRole.DEALING_HAND.value),
    (ApplicationStatus.SUBMITTED_ONLINE.value, ApplicationStatus.HARDCOPY_RECEIVED.value, UserRole.DEALING_HAND.value),
    (ApplicationStatus.HARDCOPY_RECEIVED.value, ApplicationStatus.UNDER_SCRUTINY.value, UserRole.DEALING_HAND.value),
    (ApplicationStatus.UNDER_SCRUTINY.value, ApplicationStatus.DEFICIENCY_RAISED.value, UserRole.DEALING_HAND.value),
    (ApplicationStatus.DEFICIENCY_RAISED.value, ApplicationStatus.UNDER_SCRUTINY.value, UserRole.DEALING_HAND.value),
    (ApplicationStatus.UNDER_SCRUTINY.value, ApplicationStatus.SCRUTINY_CLEARED.value, UserRole.DEALING_HAND.value),
    (ApplicationStatus.HARDCOPY_RECEIVED.value, ApplicationStatus.SCRUTINY_CLEARED.value, UserRole.DEALING_HAND.value),
    (ApplicationStatus.SCRUTINY_CLEARED.value, ApplicationStatus.COMMITTEE_CONSTITUTED.value, UserRole.REGISTRAR.value),
    (ApplicationStatus.SCRUTINY_CLEARED.value, ApplicationStatus.COMMITTEE_CONSTITUTED.value, UserRole.AUTHORITY.value),
    (ApplicationStatus.COMMITTEE_CONSTITUTED.value, ApplicationStatus.MEETING_SCHEDULED.value, UserRole.REGISTRAR.value),
    (ApplicationStatus.MEETING_SCHEDULED.value, ApplicationStatus.MOM_DRAFT_GENERATED.value, UserRole.COMMITTEE.value),
    (ApplicationStatus.MOM_DRAFT_GENERATED.value, ApplicationStatus.MOM_FINALIZED.value, UserRole.COMMITTEE.value),
    (ApplicationStatus.MOM_FINALIZED.value, ApplicationStatus.DECISION_ISSUED.value, UserRole.AUTHORITY.value),
    (ApplicationStatus.MOM_FINALIZED.value, ApplicationStatus.CLOSED.value, UserRole.AUTHORITY.value),  # e.g. REJECTED / CLOSED_NON_COMPLIANCE
    (ApplicationStatus.DECISION_ISSUED.value, ApplicationStatus.CLOSED.value, UserRole.AUTHORITY.value),
}


def can_transition(from_status: str, to_status: str, role: UserRole | str) -> bool:
    """Return True if the role may move the application from from_status to to_status."""
    role_val = role.value if isinstance(role, UserRole) else role
    return (from_status, to_status, role_val) in _ALLOWED


def can_issue_granted(ugc_policy_mode: str, ugc_approval_recorded: bool) -> tuple[bool, str]:
    """
    UGC Policy: Mode A (Strict) blocks Decision "Granted" until UGC approval recorded.
    Mode B (Parallel) allows "Subject to UGC" / auto UGC packet.
    Returns (allowed, message).
    """
    if ugc_policy_mode == "A":
        if not ugc_approval_recorded:
            return False, "Mode A (Strict): Decision 'Granted' is blocked until UGC approval is recorded."
        return True, ""
    # Mode B: allow decision labeled "Subject to UGC"
    return True, ""
