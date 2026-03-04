from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Sequence

from sqlalchemy import select, func

from app.core.security import hash_password
from app.db.models import Application, Institution, User, UserRole
from app.db.session import AsyncSessionLocal
from app.workflow import ApplicationStatus


SEED_EMAIL_DOMAIN = "seed.aktu-autonomy.local"
SEED_PASSWORD = "Test@123"


async def _already_seeded(session) -> bool:
    """Return True if our canonical seed users already exist."""
    stmt = select(func.count()).select_from(User).where(
        User.email == f"institution_a@{SEED_EMAIL_DOMAIN}"
    )
    count = (await session.execute(stmt)).scalar_one()
    return count > 0


def _sample_programmes() -> dict:
    """Return a small, valid programmes_json payload."""
    return {
        "programmes": [
            {
                "name": "B.Tech CSE",
                "level": "UG",
                "intake": 120,
            }
        ]
    }


async def apply_seed(session) -> None:
    """Create institutions, users and applications for manual testing."""
    if await _already_seeded(session):
        print("Seed data already present; skipping creation.")
        return

    # Institutions
    inst_a = Institution(
        name="Synthetic College A",
        code="SEED-A",
        address="123 Test Lane, City A",
        district="TestDistrictA",
        contact_email=f"contact_a@{SEED_EMAIL_DOMAIN}",
        contact_phone="0000000001",
    )
    inst_b = Institution(
        name="Synthetic College B",
        code="SEED-B",
        address="456 Test Road, City B",
        district="TestDistrictB",
        contact_email=f"contact_b@{SEED_EMAIL_DOMAIN}",
        contact_phone="0000000002",
    )
    session.add_all([inst_a, inst_b])
    await session.flush()

    # Users (one per role; two institution users)
    users: list[User] = [
        User(
            email=f"institution_a@{SEED_EMAIL_DOMAIN}",
            name="Seed Institution A User",
            hashed_password=hash_password(SEED_PASSWORD),
            role=UserRole.INSTITUTION,
            institution_id=inst_a.id,
        ),
        User(
            email=f"institution_b@{SEED_EMAIL_DOMAIN}",
            name="Seed Institution B User",
            hashed_password=hash_password(SEED_PASSWORD),
            role=UserRole.INSTITUTION,
            institution_id=inst_b.id,
        ),
        User(
            email=f"dealing_hand@{SEED_EMAIL_DOMAIN}",
            name="Seed Dealing Hand",
            hashed_password=hash_password(SEED_PASSWORD),
            role=UserRole.DEALING_HAND,
        ),
        User(
            email=f"registrar@{SEED_EMAIL_DOMAIN}",
            name="Seed Registrar",
            hashed_password=hash_password(SEED_PASSWORD),
            role=UserRole.REGISTRAR,
        ),
        User(
            email=f"committee@{SEED_EMAIL_DOMAIN}",
            name="Seed Committee Member",
            hashed_password=hash_password(SEED_PASSWORD),
            role=UserRole.COMMITTEE,
        ),
        User(
            email=f"authority@{SEED_EMAIL_DOMAIN}",
            name="Seed Authority",
            hashed_password=hash_password(SEED_PASSWORD),
            role=UserRole.AUTHORITY,
        ),
        User(
            email=f"accounts@{SEED_EMAIL_DOMAIN}",
            name="Seed Accounts",
            hashed_password=hash_password(SEED_PASSWORD),
            role=UserRole.ACCOUNTS,
        ),
    ]
    session.add_all(users)
    await session.flush()

    current_year = datetime.utcnow().year

    apps: list[Application] = [
        Application(
            institution_id=inst_a.id,
            status=ApplicationStatus.DRAFT.value,
            requested_from_year=current_year,
            programmes_json=_sample_programmes(),
            ugc_policy_mode="A",
            ugc_approval_recorded=False,
        ),
        Application(
            institution_id=inst_a.id,
            status=ApplicationStatus.SUBMITTED_ONLINE.value,
            requested_from_year=current_year,
            programmes_json=_sample_programmes(),
            ugc_policy_mode="A",
            ugc_approval_recorded=False,
        ),
        Application(
            institution_id=inst_b.id,
            status=ApplicationStatus.HARDCOPY_RECEIVED.value,
            requested_from_year=current_year,
            programmes_json=_sample_programmes(),
            ugc_policy_mode="A",
            ugc_approval_recorded=False,
        ),
        Application(
            institution_id=inst_b.id,
            status=ApplicationStatus.UNDER_SCRUTINY.value,
            requested_from_year=current_year,
            programmes_json=_sample_programmes(),
            ugc_policy_mode="A",
            ugc_approval_recorded=False,
        ),
        Application(
            institution_id=inst_a.id,
            status=ApplicationStatus.SCRUTINY_CLEARED.value,
            requested_from_year=current_year,
            programmes_json=_sample_programmes(),
            ugc_policy_mode="A",
            ugc_approval_recorded=True,
        ),
        Application(
            institution_id=inst_a.id,
            status=ApplicationStatus.MOM_FINALIZED.value,
            requested_from_year=current_year,
            programmes_json=_sample_programmes(),
            ugc_policy_mode="B",
            ugc_approval_recorded=False,
        ),
    ]
    session.add_all(apps)


async def verify_seed(session) -> bool:
    """Verify counts and workflow coverage; print a short report."""
    inst_count = (await session.execute(select(func.count()).select_from(Institution))).scalar_one()
    user_count = (await session.execute(select(func.count()).select_from(User))).scalar_one()

    app_rows: Sequence[tuple[str]] = (
        await session.execute(select(Application.status))
    ).all()
    app_statuses = [row[0] for row in app_rows]
    app_count = len(app_statuses)

    print(f"Institutions: {inst_count}, Users: {user_count}, Applications: {app_count}")
    print("Application statuses:", ", ".join(sorted(set(app_statuses))) or "(none)")

    ok = True

    if inst_count < 2:
        print("ERROR: Expected at least 2 institutions, found", inst_count)
        ok = False
    if user_count < 6:
        print("ERROR: Expected at least 6 users (one per role), found", user_count)
        ok = False
    if not (2 <= app_count <= 10):
        print("ERROR: Expected between 2 and 10 applications, found", app_count)
        ok = False

    # Check that we have at least one DRAFT and one non-DRAFT status.
    if ApplicationStatus.DRAFT.value not in app_statuses:
        print("ERROR: Expected at least one DRAFT application in seed data.")
        ok = False
    non_draft_statuses = {s for s in app_statuses if s != ApplicationStatus.DRAFT.value}
    if not non_draft_statuses:
        print("ERROR: Expected at least one application beyond DRAFT status.")
        ok = False

    return ok


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await apply_seed(session)
        await session.commit()

    # Re-open session for verification so we see committed state.
    async with AsyncSessionLocal() as session:
        ok = await verify_seed(session)

    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

