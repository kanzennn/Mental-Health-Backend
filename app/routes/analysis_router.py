from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from uuid import UUID

from app.dependencies import get_analysis_service, get_current_user
from app.models.user_model import User
from app.schemas.analysis_session_schema import CreateTextAnalysisSession, AnalysisSessionResponse
from app.schemas.response_schema import BaseResponse
from app.services.analysis_service import AnalysisService
from app.utils.response import ResponseBuilder

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("", response_model=BaseResponse[List[AnalysisSessionResponse]])
def get_analysis_sessions(
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    sessions = service.get_all_sessions(current_user.id)
    return ResponseBuilder.success(message="Sessions retrieved successfully", data=sessions)


@router.get("/{analysis_session_id}", response_model=BaseResponse[AnalysisSessionResponse])
def get_analysis_session_by_id(
    analysis_session_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    session = service.get_session_by_id(analysis_session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Analysis Session not found")
    return ResponseBuilder.success(
        message="Analysis Session retrieved successfully",
        data=session,
    )


@router.post("/text", response_model=BaseResponse[AnalysisSessionResponse])
async def send_text(
    data: CreateTextAnalysisSession,
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    session = await service.send_text(current_user.id, data.input_text)
    return ResponseBuilder.success(message="Analysis created successfully", data=session)


@router.post("/audio", response_model=BaseResponse[AnalysisSessionResponse])
async def send_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    result = await service.send_audio(current_user.id, file)
    return ResponseBuilder.success(
        message="Audio analysis processed successfully",
        data=result,
    )


@router.delete("/{analysis_session_id}", response_model=BaseResponse)
def delete_session(
    analysis_session_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    result = service.delete_session(analysis_session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis Session not found")
    return ResponseBuilder.success(message="Analysis Session deleted successfully")
