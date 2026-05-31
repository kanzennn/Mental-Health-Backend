from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UpdateMeRequest,
    UpdatePasswordRequest,
    UserResponse,
)
from app.schemas.response_schema import BaseResponse
from app.services.auth_service import AuthService
from app.utils.response import ResponseBuilder

router = APIRouter(prefix="/auth", tags=["Auth"])
_http_bearer = HTTPBearer()
service = AuthService()


@router.post("/register", response_model=BaseResponse[UserResponse])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = service.register(db, name=payload.name, email=payload.email, password=payload.password)
    return ResponseBuilder.success(
        message="Registration successful",
        data=UserResponse.model_validate(user).model_dump(),
    )


@router.post("/login", response_model=BaseResponse[TokenResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    result = service.login(db, email=payload.email, password=payload.password)
    return ResponseBuilder.success(message="Login successful", data=result)


@router.get("/me", response_model=BaseResponse[UserResponse])
def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(_http_bearer),
    db: Session = Depends(get_db),
):
    user = service.get_current_user(db, credentials.credentials)
    return ResponseBuilder.success(
        message="User retrieved successfully",
        data=UserResponse.model_validate(user).model_dump(),
    )


@router.put("/me", response_model=BaseResponse[UserResponse])
def update_me(
    payload: UpdateMeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(_http_bearer),
    db: Session = Depends(get_db),
):
    user = service.update_current_user(db, credentials.credentials, name=payload.name, email=payload.email)
    return ResponseBuilder.success(
        message="Profile updated successfully",
        data=UserResponse.model_validate(user).model_dump(),
    )


@router.put("/me/password", response_model=BaseResponse[UserResponse])
def change_password(
    payload: UpdatePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(_http_bearer),
    db: Session = Depends(get_db),
):
    user = service.change_password(
        db, credentials.credentials,
        old_password=payload.old_password,
        new_password=payload.new_password,
    )
    return ResponseBuilder.success(
        message="Password updated successfully",
        data=UserResponse.model_validate(user).model_dump(),
    )
