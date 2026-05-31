import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    sessions = relationship(
        "AnalysisSession",
        back_populates="user",
        passive_deletes=True,
    )
