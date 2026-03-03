from __future__ import annotations

from typing import Iterable, Sequence

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.models import AuditLog, User, UserRole
from app.db.session import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except ValueError:
        raise credentials_exception

    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception

    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


def _normalize_roles(roles: Sequence[UserRole | str]) -> set[str]:
    normalized: set[str] = set()
    for role in roles:
        if isinstance(role, UserRole):
            normalized.add(role.value)
        else:
            normalized.add(role)
    return normalized


async def log_audit(
    db: AsyncSession,
    *,
    actor: User | None,
    action: str,
    entity_type: str,
    entity_id: str,
    request: Request,
    details: dict | None = None,
    application_id: int | None = None,
) -> None:
    log = AuditLog(
        actor_user_id=actor.id if actor else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip=request.client.host if request.client else None,
        details_json=details or {},
        application_id=application_id,
    )
    db.add(log)
    await db.commit()


async def _log_audit(
    db: AsyncSession,
    *,
    actor: User | None,
    action: str,
    entity_type: str,
    entity_id: str,
    request: Request,
    details: dict | None = None,
) -> None:
    await log_audit(
        db, actor=actor, action=action, entity_type=entity_type,
        entity_id=entity_id, request=request, details=details,
    )


def require_roles(roles: Sequence[UserRole | str]):
    allowed = _normalize_roles(roles)

    async def dependency(
        request: Request,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        if user.role.value not in allowed:
            await _log_audit(
                db,
                actor=user,
                action="RBAC_FORBIDDEN",
                entity_type="route",
                entity_id=request.url.path,
                request=request,
                details={"required_roles": list(allowed), "actual_role": user.role.value},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden for this role",
            )
        return user

    return dependency

