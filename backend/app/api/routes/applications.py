"""Application lifecycle endpoints with status transitions and audit."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, log_audit, require_roles
from app.core.config import get_settings
from app.db.models import (
    Application,
    AuditLog,
    Committee,
    CommitteeMember,
    Decision,
    DispatchTracking,
    Document,
    Institution,
    Meeting,
    MeetingMode,
    MomContent,
    User,
    UserRole,
)
from app.db.models import DocumentType, CommitteeMemberRole, DecisionType
from app.db.session import get_db
from app.schemas.application import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationUpdate,
    DispatchIn,
    ReceiveIn,
    DeficiencyIn,
)
from app.schemas.committee import CommitteeCreate, CommitteeMemberOut, CommitteeOut
from app.schemas.meeting import MeetingCreate, MeetingOut
from app.schemas.mom import MomContentIn, MomContentOut
from app.schemas.decision import DecisionCreate, DecisionOut
from app.services.office_order import generate_office_order_docx
from app.services.meeting_notice import generate_meeting_notice_docx
from app.services.mom_docx import generate_mom_draft_docx, render_mom_final_docx
from app.services.decision_letter import generate_decision_letter_docx
from app.workflow import ApplicationStatus, can_transition, can_issue_granted


router = APIRouter(prefix="/api/applications", tags=["applications"])

# Mandatory annexures before submit (cannot skip).
MANDATORY_DOC_TYPES_BEFORE_SUBMIT = {
    DocumentType.ANNEXURE_IA,
    DocumentType.ANNEXURE_II,
    DocumentType.ANNEXURE_III,
    DocumentType.ANNEXURE_IV,
    DocumentType.ANNEXURE_V,
    DocumentType.ANNEXURE_VII,
    DocumentType.FEE_PROOF,
}


async def _get_application(
    db: AsyncSession,
    application_id: int,
    user: User,
) -> Application:
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = result.scalar_one_or_none()
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if user.role == UserRole.INSTITUTION and user.institution_id is not None:
        if app.institution_id != user.institution_id:
            raise HTTPException(status_code=403, detail="Forbidden: not your institution's application")
    return app


def _ensure_transition(
    current: str,
    to_status: str,
    role: UserRole,
) -> None:
    if not can_transition(current, to_status, role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transition from {current} to {to_status} not allowed for role {role.value}",
        )


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    request: Request,
    user: User = Depends(require_roles([UserRole.INSTITUTION])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    if user.institution_id is not None and payload.institution_id != user.institution_id:
        raise HTTPException(status_code=403, detail="Forbidden: cannot create for another institution")
    app = Application(
        institution_id=payload.institution_id,
        status=ApplicationStatus.DRAFT.value,
        requested_from_year=payload.requested_from_year,
        programmes_json=payload.programmes_json,
        ugc_policy_mode=payload.ugc_policy_mode,
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    await log_audit(
        db,
        actor=user,
        action="APPLICATION_CREATED",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={"public_id": app.public_id},
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


@router.get("", response_model=list[ApplicationOut])
async def list_applications(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
) -> list[ApplicationOut]:
    """List applications. Institution sees only their own; others see all (capped)."""
    q = select(Application).order_by(Application.updated_at.desc()).limit(limit)
    if user.role == UserRole.INSTITUTION and user.institution_id is not None:
        q = q.where(Application.institution_id == user.institution_id)
    result = await db.execute(q)
    apps = result.scalars().all()
    return [ApplicationOut.model_validate(a) for a in apps]


@router.get("/{application_id}", response_model=ApplicationOut)
async def get_application(
    application_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    app = await _get_application(db, application_id, user)
    return ApplicationOut.model_validate(app)


@router.patch("/{application_id}", response_model=ApplicationOut)
async def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    request: Request,
    user: User = Depends(require_roles([UserRole.INSTITUTION])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    app = await _get_application(db, application_id, user)
    if app.status != ApplicationStatus.DRAFT.value:
        raise HTTPException(
            status_code=400,
            detail="Only draft applications can be updated",
        )
    if payload.requested_from_year is not None:
        app.requested_from_year = payload.requested_from_year
    if payload.programmes_json is not None:
        app.programmes_json = payload.programmes_json
    if payload.ugc_policy_mode is not None:
        app.ugc_policy_mode = payload.ugc_policy_mode
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(app)
    await log_audit(
        db,
        actor=user,
        action="APPLICATION_UPDATED",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={"updated_fields": payload.model_dump(exclude_unset=True)},
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


@router.post("/{application_id}/submit", response_model=ApplicationOut)
async def submit_application(
    application_id: int,
    request: Request,
    user: User = Depends(require_roles([UserRole.INSTITUTION])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.SUBMITTED_ONLINE.value
    _ensure_transition(from_status, to_status, user.role)

    # Cannot skip mandatory annexures before submit.
    docs_result = await db.execute(
        select(Document.doc_type).where(Document.application_id == app.id)
    )
    present = {row[0] for row in docs_result.fetchall()}
    missing = MANDATORY_DOC_TYPES_BEFORE_SUBMIT - present
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Mandatory annexures missing before submit: {[t.value for t in missing]}",
        )

    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(app)
    await log_audit(
        db,
        actor=user,
        action="STATUS_CHANGE",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={"from_status": from_status, "to_status": to_status},
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


@router.post("/{application_id}/dispatch", response_model=ApplicationOut)
async def record_dispatch(
    application_id: int,
    payload: DispatchIn,
    request: Request,
    user: User = Depends(require_roles([UserRole.INSTITUTION])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.HARDCOPY_DISPATCHED.value
    _ensure_transition(from_status, to_status, user.role)

    dispatch_dt: datetime | None = None
    if payload.dispatch_date:
        try:
            dispatch_dt = datetime.fromisoformat(payload.dispatch_date.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            dispatch_dt = datetime.now(timezone.utc)

    dispatch = DispatchTracking(
        application_id=app.id,
        speedpost_no=payload.speedpost_no,
        dispatch_date=dispatch_dt or datetime.now(timezone.utc),
    )
    db.add(dispatch)
    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(app)
    await log_audit(
        db,
        actor=user,
        action="STATUS_CHANGE",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={"from_status": from_status, "to_status": to_status, "speedpost_no": payload.speedpost_no},
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


def _generate_ack_content(
    application_id: int,
    public_id: str,
    institution_name: str,
    received_date: datetime,
    akt_diary_no: str,
) -> str:
    return (
        f"AKTU ACADEMIC AUTONOMY PORTAL — HARDCOPY RECEIPT ACKNOWLEDGEMENT\n"
        f"{'=' * 60}\n\n"
        f"Application ID: {public_id} (internal id: {application_id})\n"
        f"Institution: {institution_name}\n"
        f"AKTU Diary/Inward No.: {akt_diary_no}\n"
        f"Received Date: {received_date.isoformat()}\n\n"
        f"This is a system-generated acknowledgement of receipt of hardcopy documents.\n"
    )


@router.post("/{application_id}/receive", response_model=ApplicationOut)
async def record_receive(
    application_id: int,
    payload: ReceiveIn,
    request: Request,
    user: User = Depends(require_roles([UserRole.DEALING_HAND])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    """Record hardcopy receipt (diary no + date). Backward-compat alias for ack-received."""
    return await _ack_received_impl(application_id, payload, request, user, db)


@router.post("/{application_id}/ack-received", response_model=ApplicationOut)
async def ack_received(
    application_id: int,
    payload: ReceiveIn,
    request: Request,
    user: User = Depends(require_roles([UserRole.DEALING_HAND])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    """AKTU: record diary no and received date; generate and store Acknowledgement document."""
    return await _ack_received_impl(application_id, payload, request, user, db)


async def _ack_received_impl(
    application_id: int,
    payload: ReceiveIn,
    request: Request,
    user: User,
    db: AsyncSession,
) -> ApplicationOut:
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.HARDCOPY_RECEIVED.value
    _ensure_transition(from_status, to_status, user.role)

    received_dt = datetime.now(timezone.utc)

    disp_result = await db.execute(
        select(DispatchTracking)
        .where(DispatchTracking.application_id == app.id)
        .order_by(DispatchTracking.id.desc())
        .limit(1)
    )
    disp = disp_result.scalar_one_or_none()
    if disp is not None:
        disp.akt_diary_no = payload.akt_diary_no
        disp.received_date = received_dt
        disp.received_by_user_id = user.id
        disp.remarks = payload.remarks
    else:
        disp = DispatchTracking(
            application_id=app.id,
            akt_diary_no=payload.akt_diary_no,
            received_date=received_dt,
            received_by_user_id=user.id,
            remarks=payload.remarks,
        )
        db.add(disp)

    app.status = to_status
    app.updated_at = received_dt
    await db.flush()

    # Load institution for ACK content
    inst_result = await db.execute(select(Institution).where(Institution.id == app.institution_id))
    institution = inst_result.scalar_one_or_none()
    institution_name = institution.name if institution else "—"

    ack_content = _generate_ack_content(
        application_id=app.id,
        public_id=app.public_id,
        institution_name=institution_name,
        received_date=received_dt,
        akt_diary_no=payload.akt_diary_no,
    )
    settings = get_settings()
    ack_dir = Path(settings.upload_dir) / str(app.id) / DocumentType.ACK.value
    ack_dir.mkdir(parents=True, exist_ok=True)
    ack_filename = f"ack_{received_dt.strftime('%Y%m%d_%H%M%S')}.txt"
    ack_path = ack_dir / ack_filename
    ack_path.write_text(ack_content, encoding="utf-8")
    sha256 = hashlib.sha256(ack_content.encode("utf-8")).hexdigest()

    ack_doc = Document(
        application_id=app.id,
        doc_type=DocumentType.ACK,
        filename=ack_filename,
        storage_path=str(ack_path),
        uploaded_by=user.id,
        uploaded_at=received_dt,
        version=1,
        sha256=sha256,
    )
    db.add(ack_doc)
    await db.flush()
    ack_doc_id = ack_doc.id
    await db.commit()
    await db.refresh(app)
    await log_audit(
        db,
        actor=user,
        action="STATUS_CHANGE",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={
            "from_status": from_status,
            "to_status": to_status,
            "akt_diary_no": payload.akt_diary_no,
            "ack_document_id": ack_doc_id,
        },
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


@router.post("/{application_id}/start-scrutiny", response_model=ApplicationOut)
async def start_scrutiny(
    application_id: int,
    request: Request,
    user: User = Depends(require_roles([UserRole.DEALING_HAND])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.UNDER_SCRUTINY.value
    _ensure_transition(from_status, to_status, user.role)

    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(app)
    await log_audit(
        db,
        actor=user,
        action="STATUS_CHANGE",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={"from_status": from_status, "to_status": to_status},
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


@router.post("/{application_id}/deficiency", response_model=ApplicationOut)
async def raise_deficiency(
    application_id: int,
    payload: DeficiencyIn,
    request: Request,
    user: User = Depends(require_roles([UserRole.DEALING_HAND])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.DEFICIENCY_RAISED.value
    _ensure_transition(from_status, to_status, user.role)

    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(app)
    await log_audit(
        db,
        actor=user,
        action="STATUS_CHANGE",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={"from_status": from_status, "to_status": to_status, "remarks": payload.remarks},
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


@router.post("/{application_id}/scrutiny-clear", response_model=ApplicationOut)
async def scrutiny_clear(
    application_id: int,
    request: Request,
    user: User = Depends(require_roles([UserRole.DEALING_HAND])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.SCRUTINY_CLEARED.value
    _ensure_transition(from_status, to_status, user.role)

    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(app)
    await log_audit(
        db,
        actor=user,
        action="STATUS_CHANGE",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={"from_status": from_status, "to_status": to_status},
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


# --- Committee & Office Order ---

@router.post("/{application_id}/committee", response_model=CommitteeOut, status_code=status.HTTP_201_CREATED)
async def create_committee(
    application_id: int,
    payload: CommitteeCreate,
    request: Request,
    user: User = Depends(require_roles([UserRole.REGISTRAR, UserRole.AUTHORITY])),
    db: AsyncSession = Depends(get_db),
) -> CommitteeOut:
    app = await _get_application(db, application_id, user)
    if app.status != ApplicationStatus.SCRUTINY_CLEARED.value:
        raise HTTPException(
            status_code=400,
            detail="Committee can be created only when application status is SCRUTINY_CLEARED",
        )
    existing = await db.execute(
        select(Committee).where(Committee.application_id == app.id)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="Committee already exists for this application")

    committee = Committee(
        application_id=app.id,
        created_by_user_id=user.id,
    )
    db.add(committee)
    await db.flush()
    for m in payload.members:
        db.add(CommitteeMember(committee_id=committee.id, user_id=m.user_id, role=m.role))
    await db.commit()
    await db.refresh(committee)
    result = await db.execute(
        select(CommitteeMember).where(CommitteeMember.committee_id == committee.id)
    )
    members = result.scalars().all()
    await log_audit(
        db,
        actor=user,
        action="COMMITTEE_CREATED",
        entity_type="committee",
        entity_id=str(committee.id),
        request=request,
        details={"application_id": app.id, "member_count": len(members)},
        application_id=app.id,
    )
    return CommitteeOut(
        id=committee.id,
        application_id=committee.application_id,
        office_order_no=committee.office_order_no,
        created_at=committee.created_at,
        created_by_user_id=committee.created_by_user_id,
        members=[CommitteeMemberOut.model_validate(m) for m in members],
    )


@router.post("/{application_id}/committee/approve", response_model=ApplicationOut)
async def approve_committee(
    application_id: int,
    request: Request,
    user: User = Depends(require_roles([UserRole.AUTHORITY])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.COMMITTEE_CONSTITUTED.value
    _ensure_transition(from_status, to_status, user.role)

    committee_result = await db.execute(
        select(Committee).where(Committee.application_id == app.id)
    )
    committee = committee_result.scalar_one_or_none()
    if committee is None:
        raise HTTPException(status_code=404, detail="No committee found for this application")
    if committee.office_order_no:
        raise HTTPException(status_code=400, detail="Committee already approved")

    office_order_no = f"OO/{datetime.now(timezone.utc).strftime('%Y')}/{app.id:04d}"
    committee.office_order_no = office_order_no

    inst_result = await db.execute(select(Institution).where(Institution.id == app.institution_id))
    institution = inst_result.scalar_one_or_none()
    institution_name = institution.name if institution else "—"

    members_result = await db.execute(
        select(CommitteeMember, User).join(User, CommitteeMember.user_id == User.id).where(CommitteeMember.committee_id == committee.id)
    )
    member_rows = members_result.all()
    members_list = [(row[1].name, row[0].role.value) for row in member_rows]

    settings = get_settings()
    oo_dir = Path(settings.upload_dir) / str(app.id) / DocumentType.OFFICE_ORDER.value
    oo_dir.mkdir(parents=True, exist_ok=True)
    oo_filename = f"office_order_{office_order_no.replace('/', '_')}.docx"
    oo_path = oo_dir / oo_filename
    generate_office_order_docx(
        office_order_no=office_order_no,
        institution_name=institution_name,
        application_public_id=app.public_id,
        members_list=members_list,
        output_path=oo_path,
    )

    content = oo_path.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    doc = Document(
        application_id=app.id,
        doc_type=DocumentType.OFFICE_ORDER,
        filename=oo_filename,
        storage_path=str(oo_path),
        uploaded_by=user.id,
        uploaded_at=datetime.now(timezone.utc),
        version=1,
        sha256=sha256,
    )
    db.add(doc)
    await db.flush()
    doc_id = doc.id

    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(app)

    # Notification stub: log only (MVP)
    import logging
    logger = logging.getLogger("aktu-autonomy-portal")
    for _cm, u in member_rows:
        logger.info("notification_stub", extra={"action": "committee_approved", "email": u.email, "application_id": app.id})

    await log_audit(
        db,
        actor=user,
        action="STATUS_CHANGE",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={
            "from_status": from_status,
            "to_status": to_status,
            "office_order_no": office_order_no,
            "office_order_document_id": doc_id,
        },
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


# --- Meeting notice ---

@router.post("/{application_id}/meetings", response_model=MeetingOut, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    application_id: int,
    payload: MeetingCreate,
    request: Request,
    user: User = Depends(require_roles([UserRole.REGISTRAR])),
    db: AsyncSession = Depends(get_db),
) -> MeetingOut:
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.MEETING_SCHEDULED.value
    _ensure_transition(from_status, to_status, user.role)

    committee_result = await db.execute(
        select(Committee).where(Committee.application_id == app.id)
    )
    committee = committee_result.scalar_one_or_none()
    if committee is None:
        raise HTTPException(status_code=400, detail="No committee constituted for this application")

    meeting = Meeting(
        application_id=app.id,
        mode=payload.mode,
        date_time=payload.date_time,
        venue=payload.venue,
        online_link=payload.online_link,
        agenda=payload.agenda,
        created_by=user.id,
    )
    db.add(meeting)
    await db.flush()

    inst_result = await db.execute(select(Institution).where(Institution.id == app.institution_id))
    institution = inst_result.scalar_one_or_none()
    institution_name = institution.name if institution else "—"

    settings = get_settings()
    notice_dir = Path(settings.upload_dir) / str(app.id) / DocumentType.MEETING_NOTICE.value
    notice_dir.mkdir(parents=True, exist_ok=True)
    notice_filename = f"meeting_notice_{meeting.id}.docx"
    notice_path = notice_dir / notice_filename
    generate_meeting_notice_docx(
        application_public_id=app.public_id,
        institution_name=institution_name,
        mode=payload.mode.value,
        date_time_str=payload.date_time.isoformat(),
        venue=payload.venue,
        online_link=payload.online_link,
        agenda=payload.agenda,
        output_path=notice_path,
    )
    content = notice_path.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    doc = Document(
        application_id=app.id,
        doc_type=DocumentType.MEETING_NOTICE,
        filename=notice_filename,
        storage_path=str(notice_path),
        uploaded_by=user.id,
        uploaded_at=datetime.now(timezone.utc),
        version=1,
        sha256=sha256,
    )
    db.add(doc)

    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(meeting)

    # Auto-notify committee members (stub: log only)
    members_result = await db.execute(
        select(User).join(CommitteeMember, CommitteeMember.user_id == User.id).where(CommitteeMember.committee_id == committee.id)
    )
    import logging
    logger = logging.getLogger("aktu-autonomy-portal")
    for row in members_result.all():
        u = row[0]
        logger.info("notification_stub", extra={"action": "meeting_scheduled", "email": u.email, "application_id": app.id})

    await log_audit(
        db,
        actor=user,
        action="MEETING_SCHEDULED",
        entity_type="meeting",
        entity_id=str(meeting.id),
        request=request,
        details={"application_id": app.id, "date_time": payload.date_time.isoformat()},
        application_id=app.id,
    )
    return MeetingOut.model_validate(meeting)


@router.get("/{application_id}/meetings", response_model=list[MeetingOut])
async def list_meetings(
    application_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MeetingOut]:
    app = await _get_application(db, application_id, user)
    settings = get_settings()
    if user.role == UserRole.INSTITUTION and not settings.meeting_visible_to_institution:
        return []
    result = await db.execute(
        select(Meeting).where(Meeting.application_id == app.id).order_by(Meeting.date_time)
    )
    meetings = result.scalars().all()
    return [MeetingOut.model_validate(m) for m in meetings]


# --- MoM draft, content, finalize ---

@router.post("/{application_id}/mom/draft", response_model=ApplicationOut)
async def mom_generate_draft(
    application_id: int,
    request: Request,
    user: User = Depends(require_roles([UserRole.COMMITTEE])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    """Generate MoM draft DOCX and set status to MOM_DRAFT_GENERATED (from MEETING_SCHEDULED)."""
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.MOM_DRAFT_GENERATED.value
    _ensure_transition(from_status, to_status, user.role)

    inst_result = await db.execute(select(Institution).where(Institution.id == app.institution_id))
    institution = inst_result.scalar_one_or_none()
    institution_name = institution.name if institution else "—"

    content_json = {
        "section_6_29_a_i": "",
        "section_6_29_a_ii": "",
        "section_6_29_a_iii": "",
        "comments": "",
    }
    mom_row = MomContent(
        application_id=app.id,
        version=1,
        content_json=content_json,
        updated_by=user.id,
    )
    db.add(mom_row)
    await db.flush()

    settings = get_settings()
    mom_dir = Path(settings.upload_dir) / str(app.id) / DocumentType.MOM.value
    mom_dir.mkdir(parents=True, exist_ok=True)
    draft_filename = f"mom_draft_v1_{app.id}.docx"
    draft_path = mom_dir / draft_filename
    generate_mom_draft_docx(
        application_public_id=app.public_id,
        institution_name=institution_name,
        content_json=content_json,
        output_path=draft_path,
    )
    content = draft_path.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    doc = Document(
        application_id=app.id,
        doc_type=DocumentType.MOM,
        filename=draft_filename,
        storage_path=str(draft_path),
        uploaded_by=user.id,
        uploaded_at=datetime.now(timezone.utc),
        version=1,
        sha256=sha256,
    )
    db.add(doc)
    await db.flush()
    doc_id = doc.id

    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(app)

    await log_audit(
        db,
        actor=user,
        action="MOM_DRAFT_GENERATED",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={"from_status": from_status, "to_status": to_status, "mom_document_id": doc_id},
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


@router.get("/{application_id}/mom/content", response_model=MomContentOut)
async def mom_get_content(
    application_id: int,
    user: User = Depends(require_roles([UserRole.COMMITTEE, UserRole.REGISTRAR, UserRole.AUTHORITY])),
    db: AsyncSession = Depends(get_db),
) -> MomContentOut:
    """Get latest MoM content for editor (COMMITTEE can edit; REGISTRAR/AUTHORITY can view)."""
    app = await _get_application(db, application_id, user)
    result = await db.execute(
        select(MomContent)
        .where(MomContent.application_id == app.id)
        .order_by(MomContent.version.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    if latest is None:
        raise HTTPException(
            status_code=404,
            detail="No MoM content found. Generate draft first with POST /mom/draft",
        )
    return MomContentOut.model_validate(latest)


@router.put("/{application_id}/mom/content", response_model=MomContentOut)
async def mom_save_content(
    application_id: int,
    payload: MomContentIn,
    request: Request,
    user: User = Depends(require_roles([UserRole.COMMITTEE])),
    db: AsyncSession = Depends(get_db),
) -> MomContentOut:
    """Save structured MoM sections (new version). Allowed only when status is MOM_DRAFT_GENERATED."""
    app = await _get_application(db, application_id, user)
    if app.status != ApplicationStatus.MOM_DRAFT_GENERATED.value:
        raise HTTPException(
            status_code=400,
            detail="MoM content can be edited only when status is MOM_DRAFT_GENERATED",
        )
    result = await db.execute(
        select(MomContent)
        .where(MomContent.application_id == app.id)
        .order_by(MomContent.version.desc())
        .limit(1)
    )
    prev = result.scalar_one_or_none()
    next_version = (prev.version + 1) if prev else 1
    content_json = payload.to_content_json()
    mom_row = MomContent(
        application_id=app.id,
        version=next_version,
        content_json=content_json,
        updated_by=user.id,
    )
    db.add(mom_row)
    await db.commit()
    await db.refresh(mom_row)
    await log_audit(
        db,
        actor=user,
        action="MOM_CONTENT_SAVED",
        entity_type="mom_content",
        entity_id=str(mom_row.id),
        request=request,
        details={"application_id": app.id, "version": next_version},
        application_id=app.id,
    )
    return MomContentOut.model_validate(mom_row)


@router.post("/{application_id}/mom/finalize", response_model=ApplicationOut)
async def mom_finalize(
    application_id: int,
    request: Request,
    user: User = Depends(require_roles([UserRole.COMMITTEE])),
    db: AsyncSession = Depends(get_db),
) -> ApplicationOut:
    """Render final MoM DOCX from latest content and set status to MOM_FINALIZED."""
    app = await _get_application(db, application_id, user)
    from_status = app.status
    to_status = ApplicationStatus.MOM_FINALIZED.value
    _ensure_transition(from_status, to_status, user.role)

    result = await db.execute(
        select(MomContent)
        .where(MomContent.application_id == app.id)
        .order_by(MomContent.version.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    if latest is None:
        raise HTTPException(status_code=400, detail="No MoM content to finalize. Save content first.")
    content_json = latest.content_json

    inst_result = await db.execute(select(Institution).where(Institution.id == app.institution_id))
    institution = inst_result.scalar_one_or_none()
    institution_name = institution.name if institution else "—"

    settings = get_settings()
    mom_dir = Path(settings.upload_dir) / str(app.id) / DocumentType.MOM.value
    mom_dir.mkdir(parents=True, exist_ok=True)
    final_filename = f"mom_final_{app.public_id.replace('/', '_')}.docx"
    final_path = mom_dir / final_filename
    render_mom_final_docx(
        application_public_id=app.public_id,
        institution_name=institution_name,
        content_json=content_json,
        output_path=final_path,
    )
    content = final_path.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    doc = Document(
        application_id=app.id,
        doc_type=DocumentType.MOM,
        filename=final_filename,
        storage_path=str(final_path),
        uploaded_by=user.id,
        uploaded_at=datetime.now(timezone.utc),
        version=latest.version,
        sha256=sha256,
    )
    db.add(doc)
    await db.flush()
    doc_id = doc.id

    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(app)

    await log_audit(
        db,
        actor=user,
        action="MOM_FINALIZED",
        entity_type="application",
        entity_id=str(app.id),
        request=request,
        details={"from_status": from_status, "to_status": to_status, "mom_document_id": doc_id},
        application_id=app.id,
    )
    return ApplicationOut.model_validate(app)


# --- Decision (Authority) ---

_CLOSING_DECISION_TYPES = {
    DecisionType.REJECTED,
    DecisionType.RETURNED_WITHOUT_PROCESSING,
    DecisionType.CLOSED_NON_COMPLIANCE,
}


@router.post("/{application_id}/decision", response_model=DecisionOut, status_code=status.HTTP_201_CREATED)
async def issue_decision(
    application_id: int,
    payload: DecisionCreate,
    request: Request,
    user: User = Depends(require_roles([UserRole.AUTHORITY])),
    db: AsyncSession = Depends(get_db),
) -> DecisionOut:
    """Issue final decision: generate Decision Letter DOCX, store as Document, set status DECISION_ISSUED or CLOSED. Authority only."""
    app = await _get_application(db, application_id, user)
    existing = await db.execute(select(Decision).where(Decision.application_id == app.id))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="A decision has already been issued for this application")
    from_status = app.status
    if payload.decision_type in _CLOSING_DECISION_TYPES:
        to_status = ApplicationStatus.CLOSED.value
    else:
        to_status = ApplicationStatus.DECISION_ISSUED.value
    _ensure_transition(from_status, to_status, user.role)

    if payload.decision_type == DecisionType.GRANTED:
        allowed, msg = can_issue_granted(app.ugc_policy_mode, app.ugc_approval_recorded)
        if not allowed:
            raise HTTPException(status_code=400, detail=msg)

    ugc_subject_to_flag = (
        app.ugc_policy_mode == "B" and not app.ugc_approval_recorded
    )

    inst_result = await db.execute(select(Institution).where(Institution.id == app.institution_id))
    institution = inst_result.scalar_one_or_none()
    institution_name = institution.name if institution else "—"
    contact_email = institution.contact_email if institution else ""

    decision_row = Decision(
        application_id=app.id,
        decision_type=payload.decision_type,
        tenure_years=payload.tenure_years,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        reasons=payload.reasons,
        conditions=payload.conditions,
        ugc_subject_to_flag=ugc_subject_to_flag,
        created_by=user.id,
    )
    db.add(decision_row)
    await db.flush()

    settings = get_settings()
    dec_dir = Path(settings.upload_dir) / str(app.id) / DocumentType.DECISION_LETTER.value
    dec_dir.mkdir(parents=True, exist_ok=True)
    dec_filename = f"decision_{app.public_id.replace('/', '_')}.docx"
    dec_path = dec_dir / dec_filename
    generate_decision_letter_docx(
        application_public_id=app.public_id,
        institution_name=institution_name,
        decision_type=payload.decision_type.value,
        tenure_years=payload.tenure_years,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        reasons=payload.reasons,
        conditions=payload.conditions,
        ugc_subject_to_flag=ugc_subject_to_flag,
        output_path=dec_path,
    )
    content = dec_path.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    doc = Document(
        application_id=app.id,
        doc_type=DocumentType.DECISION_LETTER,
        filename=dec_filename,
        storage_path=str(dec_path),
        uploaded_by=user.id,
        uploaded_at=datetime.now(timezone.utc),
        version=1,
        sha256=sha256,
    )
    db.add(doc)
    await db.flush()
    doc_id = doc.id

    app.status = to_status
    app.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(decision_row)

    base = str(settings.base_url) if settings.base_url else ""
    download_link = f"{base}/api/documents/{doc_id}" if base else f"/api/documents/{doc_id}"
    import logging
    logger = logging.getLogger("aktu-autonomy-portal")
    logger.info(
        "decision_notification_stub",
        extra={
            "action": "decision_issued",
            "application_id": app.id,
            "institution_contact_email": contact_email,
            "download_link": download_link,
            "document_id": doc_id,
        },
    )

    await log_audit(
        db,
        actor=user,
        action="DECISION_ISSUED",
        entity_type="decision",
        entity_id=str(decision_row.id),
        request=request,
        details={
            "application_id": app.id,
            "decision_type": payload.decision_type.value,
            "to_status": to_status,
            "document_id": doc_id,
        },
        application_id=app.id,
    )
    return DecisionOut(
        id=decision_row.id,
        application_id=decision_row.application_id,
        decision_type=decision_row.decision_type.value,
        tenure_years=decision_row.tenure_years,
        valid_from=decision_row.valid_from,
        valid_to=decision_row.valid_to,
        reasons=decision_row.reasons,
        conditions=decision_row.conditions,
        ugc_subject_to_flag=decision_row.ugc_subject_to_flag,
        created_at=decision_row.created_at,
        created_by=decision_row.created_by,
    )
