from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ...domain.entities import (
    AnalysisContext,
    CardiovascularProfile,
    Explanation,
    Prediction,
)
from ...domain.ports import (
    AnalysisHistoryRepository,
    AnalysisRepository,
    CardiovascularModel,
)


@dataclass(frozen=True)
class AnalysisResult:
    analysis_id: UUID
    prediction: Prediction
    explanation: Explanation


class AnalyzeProfile:
    """Calcula la predicción y la explicación SHAP y guarda el contexto del análisis.

    No solicita recomendaciones: el RAG se pide después con el analysis_id.
    """

    def __init__(
        self,
        model: CardiovascularModel,
        repository: AnalysisRepository,
        history_repository: AnalysisHistoryRepository,
    ):
        self._model = model
        self._repository = repository
        self._history_repository = history_repository

    async def execute(
        self,
        profile: CardiovascularProfile,
        owner_id: UUID,
    ) -> AnalysisResult:
        prediction = await self._model.predict(profile)
        explanation = await self._model.explain(profile)

        analysis_id = self._repository.save(
            AnalysisContext(
                profile=profile,
                prediction=prediction,
                explanation=explanation,
                owner_id=owner_id,
            )
        )
        self._history_repository.save(analysis_id, owner_id, prediction)

        return AnalysisResult(
            analysis_id=analysis_id,
            prediction=prediction,
            explanation=explanation,
        )
