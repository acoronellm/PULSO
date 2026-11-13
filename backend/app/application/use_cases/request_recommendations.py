from __future__ import annotations

from uuid import UUID

from ...domain.entities import RecommendationReport
from ...domain.ports import AnalysisRepository, RecommendationGenerator


class RequestRecommendations:
    """Obtiene recomendaciones educativas para un análisis ya calculado.

    Recupera el contexto guardado, así que no vuelve a ejecutar el modelo.
    """

    def __init__(
        self,
        repository: AnalysisRepository,
        recommendations: RecommendationGenerator,
    ):
        self._repository = repository
        self._recommendations = recommendations

    async def execute(
        self,
        analysis_id: UUID,
        owner_id: UUID | None = None,
    ) -> RecommendationReport:
        context = self._repository.get(analysis_id, owner_id)
        return await self._recommendations.generate(context)
