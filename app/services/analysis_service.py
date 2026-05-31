import httpx
from uuid import UUID
from fastapi import HTTPException

from app.core.config import settings
from app.core.labels import LABEL_MAP
from app.repositories.analysis_session_repository import AnalysisSessionRepository
from app.repositories.analysis_result_repository import AnalysisResultRepository
from app.services.transcriber_service import TranscriberService


class AnalysisService:
    def __init__(self, db):
        self.db = db
        self.session_repo = AnalysisSessionRepository(db)
        self.result_repo = AnalysisResultRepository(db)
        self.transcriber = TranscriberService()

    def get_all_sessions(self, user_id):
        return self.session_repo.get_by_user(user_id)

    def get_session_by_id(self, session_id):
        session = self.session_repo.get_by_id(session_id)
        if not session:
            return None
        session.results = self.result_repo.get_by_session(session.id)
        return session

    async def send_text(self, user_id, input_text: str):
        ai_result = await self._call_explain(input_text)
        session, results = self._create_session(user_id, input_text, ai_result)
        session.results = results
        return session

    async def send_audio(self, user_id, audio_file):
        transcribed = await self.transcriber.transcribe_audio(audio_file)
        if not transcribed or not transcribed.text.strip():
            raise HTTPException(status_code=422, detail="Transcription returned empty text")
        text = transcribed.text
        ai_result = await self._call_explain(text)
        session, results = self._create_session(user_id, text, ai_result)
        session.results = results
        return session

    def delete_session(self, session_id):
        session = self.session_repo.get_by_id(session_id)
        if not session:
            return None
        self.session_repo.delete(session.id)
        return session

    def _create_session(self, user_id, text: str, ai_result: dict):
        raw_preds = ai_result["predictions"]
        raw_explanations = ai_result.get("explanations", {})

        probabilities = {
            LABEL_MAP[lbl]: round(val["prob"] * 100, 2)
            for lbl, val in raw_preds.items()
            if lbl in LABEL_MAP
        }
        mapped_explanations = {
            LABEL_MAP[lbl]: scores
            for lbl, scores in raw_explanations.items()
            if lbl in LABEL_MAP
        }

        top_category = max(probabilities, key=probabilities.get)
        top_confidence = probabilities[top_category] / 100

        session = self.session_repo.create(
            user_id=user_id,
            input_text=text,
            category=top_category,
            confidence=top_confidence,
            model_version="v1",
            method="LIME",
        )

        analysis_results = [
            {
                "result_type": label,
                "score": score,
                "detail": mapped_explanations.get(label),
            }
            for label, score in probabilities.items()
        ]
        saved_results = self.result_repo.create_many(session.id, analysis_results)

        return session, saved_results

    async def _call_explain(self, text: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.XAI_API_URL}/explain",
                    json={"text": text, "num_features": 10, "num_samples": 500},
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Inference service timeout")
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Inference service error: {str(e)}")
