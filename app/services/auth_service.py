import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
from typing import cast

from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, decode_token


class AuthService:
    def __init__(self):
        self.repo = UserRepository()

    def register(self, db: Session, name: str, email: str, password: str):
        if self.repo.find_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed = hash_password(password)
        return self.repo.create(db, name=name, email=email, password_hash=hashed)

    def login(self, db: Session, email: str, password: str):
        user = self.repo.find_by_email(db, email)
        if not user or not verify_password(password, cast(str, user.password)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}

    def get_current_user(self, db: Session, token: str):
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        user = self.repo.get_by_id(db, uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_current_user(self, db: Session, token: str, **kwargs):
        user = self.get_current_user(db, token)
        filtered = {k: v for k, v in kwargs.items() if v is not None}
        return self.repo.update(db, user.id, **filtered)

    def change_password(self, db: Session, token: str, old_password: str, new_password: str):
        user = self.get_current_user(db, token)
        if not verify_password(old_password, cast(str, user.password)):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        hashed = hash_password(new_password)
        return self.repo.update(db, user.id, password=hashed)
