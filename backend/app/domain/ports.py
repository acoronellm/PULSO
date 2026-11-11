"""Puertos: interfaces que el dominio necesita del mundo exterior.

La capa de infraestructura las implementa (ML Service, n8n, memoria) y los
casos de uso dependen solo de estas abstracciones.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from .entities import (
    AnalysisContext,
    CardiovascularProfile,
    Explanation,
    Prediction,
    RecommendationReport,
    ScenarioChanges,
    SimulationOutcome,
)


class CardiovascularModel(Protocol):
    """Modelo PULSO: predicción, explicación SHAP y simulación de escenarios."""

    async def predict(self, profile: CardiovascularProfile) -> Prediction: ...

    async def explain(self, profile: CardiovascularProfile) -> Explanation: ...

    async def simulate(
        self,
        profile: CardiovascularProfile,
        changes: ScenarioChanges,
    ) -> SimulationOutcome: ...


class RecommendationGenerator(Protocol):
    """Genera recomendaciones educativas a partir de un análisis ya calculado."""

    async def generate(self, context: AnalysisContext) -> RecommendationReport: ...


class AnalysisRepository(Protocol):
    """Guarda temporalmente los análisis para consultarlos por su identificador."""

    def save(self, context: AnalysisContext) -> UUID: ...

    def get(self, analysis_id: UUID) -> AnalysisContext:
        """Lanza AnalysisNotFoundError si no existe o expiró."""
        ...
