import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Float, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    input_text = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    model_version = Column(String, nullable=True)
    method = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    user = relationship("User", back_populates="sessions")
    results = relationship(
        "AnalysisResult",
        back_populates="session",
        cascade="all, delete-orphan",
    )
