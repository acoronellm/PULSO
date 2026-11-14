"""Puertos: interfaces que el dominio necesita del mundo exterior.

La capa de infraestructura las implementa (ML Service, n8n, memoria) y los
casos de uso dependen solo de estas abstracciones.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from .entities import (
    AnalysisContext,
    AnalysisHistoryEntry,
    AuthUser,
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

    def get(self, analysis_id: UUID, owner_id: UUID | None = None) -> AnalysisContext:
        """Lanza AnalysisNotFoundError si no existe o expiró."""
        ...


class AnalysisHistoryRepository(Protocol):
    """Persiste resultados mínimos de análisis y los consulta por propietario."""

    def save(
        self,
        analysis_id: UUID,
        owner_id: UUID,
        prediction: Prediction,
    ) -> AnalysisHistoryEntry: ...

    def list_for_user(
        self,
        owner_id: UUID,
        limit: int,
        offset: int,
    ) -> list[AnalysisHistoryEntry]: ...


class UserRepository(Protocol):
    """Acceso a las cuentas de usuario."""

    def find_by_email(self, email: str) -> AuthUser | None: ...

    def find_by_id(self, user_id: UUID) -> AuthUser | None: ...

    def create(self, email: str, password_hash: str) -> AuthUser: ...


class PasswordHasher(Protocol):
    """Crea y verifica hashes seguros de contraseñas."""

    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...


class AccessTokenIssuer(Protocol):
    """Emite tokens de acceso firmados para una cuenta."""

    def issue(self, user_id: UUID) -> str: ...

    def subject(self, token: str) -> UUID: ...
