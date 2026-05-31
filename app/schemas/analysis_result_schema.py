from uuid import UUID
from typing import Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AnalysisResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    analysis_session_id: UUID
    result_type: str
    score: float
    detail: Any | None
    created_at: datetime
    updated_at: datetime
