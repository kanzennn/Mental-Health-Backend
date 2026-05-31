from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user_model import User
from app.services.auth_service import AuthService
from app.services.analysis_service import AnalysisService

_http_bearer = HTTPBearer()

_auth_service = AuthService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_http_bearer),
    db: Session = Depends(get_db),
) -> User:
    return _auth_service.get_current_user(db, credentials.credentials)


def get_analysis_service(db: Session = Depends(get_db)) -> AnalysisService:
    return AnalysisService(db)
