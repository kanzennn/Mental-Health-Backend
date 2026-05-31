import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Float, ForeignKey, String, JSON, DateTime, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_session_id = Column(UUID(as_uuid=True), ForeignKey("analysis_sessions.id"))
    result_type = Column(String, nullable=False)
    score = Column(Float, default=0.0)
    detail = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    session = relationship("AnalysisSession", back_populates="results")
