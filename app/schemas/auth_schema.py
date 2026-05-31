from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateMeRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    updated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
