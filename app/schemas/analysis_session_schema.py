from uuid import UUID
from typing import List
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from app.schemas.analysis_result_schema import AnalysisResultResponse


class CreateTextAnalysisSession(BaseModel):
    input_text: str

    @field_validator("input_text")
    @classmethod
    def input_text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("input_text must not be empty")
        return v


class AnalysisSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    input_text: str | None
    category: str | None
    confidence: float | None
    model_version: str | None
    method: str | None
    created_at: datetime
    updated_at: datetime
    results: List[AnalysisResultResponse] = []
