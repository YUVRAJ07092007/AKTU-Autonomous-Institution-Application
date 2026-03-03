from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.db.models import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: UserRole
    institution_id: int | None = None

    class Config:
        from_attributes = True

