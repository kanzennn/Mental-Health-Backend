from app.models.analysis_result_model import AnalysisResult


class AnalysisResultRepository:
    def __init__(self, db):
        self.db = db

    def create_many(self, analysis_session_id, results: list[dict]) -> list[AnalysisResult]:
        objects = [
            AnalysisResult(
                analysis_session_id=analysis_session_id,
                result_type=r["result_type"],
                score=r["score"],
                detail=r.get("detail"),
            )
            for r in results
        ]
        self.db.add_all(objects)
        self.db.commit()
        for obj in objects:
            self.db.refresh(obj)
        return sorted(objects, key=lambda x: x.score, reverse=True)

    def get_by_session(self, analysis_session_id) -> list[AnalysisResult]:
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.analysis_session_id == analysis_session_id
        ).order_by(AnalysisResult.score.desc()).all()
