from app.models.analysis_session_model import AnalysisSession


class AnalysisSessionRepository:
    def __init__(self, db):
        self.db = db

    def get_by_user(self, user_id):
        return self.db.query(AnalysisSession).filter(
            AnalysisSession.user_id == user_id
        ).all()

    def create(
        self,
        user_id,
        input_text: str | None,
        category: str | None = None,
        confidence: float | None = None,
        model_version: str | None = None,
        method: str | None = None,
    ) -> AnalysisSession:
        session = AnalysisSession(
            user_id=user_id,
            input_text=input_text,
            category=category,
            confidence=confidence,
            model_version=model_version,
            method=method,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, analysis_session_id) -> AnalysisSession | None:
        return self.db.query(AnalysisSession).filter(
            AnalysisSession.id == analysis_session_id
        ).first()

    def delete(self, analysis_session_id) -> AnalysisSession | None:
        session = self.get_by_id(analysis_session_id)
        if not session:
            return None
        self.db.delete(session)
        self.db.commit()
        return session
