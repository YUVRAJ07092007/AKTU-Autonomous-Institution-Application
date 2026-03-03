from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserRole(str, Enum):  # type: ignore[misc]
    INSTITUTION = "INSTITUTION"
    DEALING_HAND = "DEALING_HAND"
    REGISTRAR = "REGISTRAR"
    COMMITTEE = "COMMITTEE"
    AUTHORITY = "AUTHORITY"
    ACCOUNTS = "ACCOUNTS"


class DocumentType(str, Enum):  # type: ignore[misc]
    COVER_LETTER = "CoverLetter"
    APPLICATION_FORM = "ApplicationForm"
    ANNEXURE_IA = "AnnexureIA"
    ANNEXURE_II = "AnnexureII"
    ANNEXURE_III = "AnnexureIII"
    ANNEXURE_IV = "AnnexureIV"
    ANNEXURE_V = "AnnexureV"
    ANNEXURE_VII = "AnnexureVII"
    FEE_PROOF = "FeeProof"
    OFFICE_ORDER = "OfficeOrder"
    MOM = "MoM"
    DECISION_LETTER = "DecisionLetter"
    UGC_APPROVAL = "UGCApproval"
    ACK = "ACK"
    MEETING_NOTICE = "MeetingNotice"


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    institution_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True, index=True
    )

    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="actor")


class Institution(Base):
    __tablename__ = "institutions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(50), nullable=False)

    applications: Mapped[List["Application"]] = relationship(back_populates="institution")


class Application(Base):
    __tablename__ = "applications"

    # Use separate UUID column while keeping integer PK for joins/indexes.
    public_id: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    institution_id: Mapped[int] = mapped_column(
        ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="DRAFT", index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    requested_from_year: Mapped[int] = mapped_column(nullable=False)
    programmes_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    ugc_policy_mode: Mapped[str] = mapped_column(String(1), nullable=False, default="A")
    ugc_approval_recorded: Mapped[bool] = mapped_column(default=False)

    institution: Mapped[Institution] = relationship(back_populates="applications")
    dispatch_records: Mapped[List["DispatchTracking"]] = relationship(
        back_populates="application"
    )
    documents: Mapped[List["Document"]] = relationship(back_populates="application")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="application")
    committees: Mapped[List["Committee"]] = relationship(
        back_populates="application", order_by="Committee.id"
    )
    meetings: Mapped[List["Meeting"]] = relationship(
        back_populates="application", order_by="Meeting.date_time"
    )
    mom_versions: Mapped[List["MomContent"]] = relationship(
        back_populates="application", order_by="MomContent.version"
    )
    decision: Mapped[Optional["Decision"]] = relationship(
        back_populates="application", uselist=False
    )


class DispatchTracking(Base):
    __tablename__ = "dispatch_tracking"

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    speedpost_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dispatch_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    akt_diary_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    received_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    received_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    application: Mapped[Application] = relationship(back_populates="dispatch_records")

    __table_args__ = (
        UniqueConstraint("application_id", "speedpost_no", name="uq_dispatch_speedpost"),
    )


class CommitteeMemberRole(str, Enum):  # type: ignore[misc]
    CHAIR = "CHAIR"
    CONVENER = "CONVENER"
    MEMBER = "MEMBER"


class Committee(Base):
    __tablename__ = "committees"

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    office_order_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    application: Mapped[Application] = relationship(back_populates="committees")
    members: Mapped[List["CommitteeMember"]] = relationship(
        back_populates="committee", cascade="all, delete-orphan"
    )


class CommitteeMember(Base):
    __tablename__ = "committee_members"

    committee_id: Mapped[int] = mapped_column(
        ForeignKey("committees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[CommitteeMemberRole] = mapped_column(
        Enum(CommitteeMemberRole), nullable=False
    )

    committee: Mapped[Committee] = relationship(back_populates="members")
    user: Mapped[User] = relationship()


class MeetingMode(str, Enum):  # type: ignore[misc]
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    HYBRID = "HYBRID"


class Meeting(Base):
    __tablename__ = "meetings"

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mode: Mapped[MeetingMode] = mapped_column(Enum(MeetingMode), nullable=False)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    online_link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    agenda: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    application: Mapped[Application] = relationship(back_populates="meetings")


class MomContent(Base):
    """Versioned MoM structured content (Clause 6.29 sections)."""

    __tablename__ = "mom_content"

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(nullable=False)
    content_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    application: Mapped[Application] = relationship(back_populates="mom_versions")


class DecisionType(str, Enum):  # type: ignore[misc]
    GRANTED = "GRANTED"
    GRANTED_WITH_CONDITIONS = "GRANTED_WITH_CONDITIONS"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"
    RETURNED_WITHOUT_PROCESSING = "RETURNED_WITHOUT_PROCESSING"
    CLOSED_NON_COMPLIANCE = "CLOSED_NON_COMPLIANCE"


class Decision(Base):
    """Final decision on an application (one per application)."""

    __tablename__ = "decisions"

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    decision_type: Mapped[DecisionType] = mapped_column(Enum(DecisionType), nullable=False)
    tenure_years: Mapped[Optional[int]] = mapped_column(nullable=True)
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reasons: Mapped[str] = mapped_column(Text, nullable=False, default="")
    conditions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ugc_subject_to_flag: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )

    application: Mapped[Application] = relationship(back_populates="decision")


class Document(Base):
    __tablename__ = "documents"

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doc_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    version: Mapped[int] = mapped_column(default=1)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    application: Mapped[Application] = relationship(back_populates="documents")
    uploader: Mapped[User] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )
    ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    details_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    actor: Mapped[Optional[User]] = relationship(back_populates="audit_logs")
    application_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("applications.id", ondelete="SET NULL"), nullable=True, index=True
    )
    application: Mapped[Optional[Application]] = relationship(back_populates="audit_logs")

