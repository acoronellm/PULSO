from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..domain.entities import AnalysisHistoryEntry, Prediction
from .analysis_history_model import AnalysisHistoryModel


class SQLAlchemyAnalysisHistoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        analysis_id: UUID,
        owner_id: UUID,
        prediction: Prediction,
    ) -> AnalysisHistoryEntry:
        analysis = AnalysisHistoryModel(
            id=analysis_id,
            user_id=owner_id,
            probability=prediction.probability,
            classification=prediction.classification,
            threshold=prediction.threshold,
            model_version=prediction.model_version,
        )
        self._session.add(analysis)
        self._session.commit()
        self._session.refresh(analysis)
        return self._to_entity(analysis)

    def list_for_user(
        self,
        owner_id: UUID,
        limit: int,
        offset: int,
    ) -> list[AnalysisHistoryEntry]:
        analyses = self._session.scalars(
            select(AnalysisHistoryModel)
            .where(AnalysisHistoryModel.user_id == owner_id)
            .order_by(AnalysisHistoryModel.created_at.desc(), AnalysisHistoryModel.id.desc())
            .limit(limit)
            .offset(offset)
        ).all()
        return [self._to_entity(analysis) for analysis in analyses]

    @staticmethod
    def _to_entity(analysis: AnalysisHistoryModel) -> AnalysisHistoryEntry:
        return AnalysisHistoryEntry(
            analysis_id=analysis.id,
            probability=analysis.probability,
            classification=analysis.classification,
            threshold=analysis.threshold,
            model_version=analysis.model_version,
            created_at=analysis.created_at,
        )
