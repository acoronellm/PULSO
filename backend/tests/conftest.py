"""Datos y dobles de prueba compartidos por todas las capas."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.domain.entities import (
    AnalysisContext,
    CardiovascularProfile,
    DocumentSource,
    Explanation,
    Prediction,
    Recommendation,
    RecommendationReport,
    ScenarioChanges,
    ScenarioResult,
    ShapFactor,
    SimulationOutcome,
    SourceLines,
)
from backend.app.infrastructure.in_memory_analysis_repository import InMemoryAnalysisRepository
from backend.app.interfaces.http import dependencies
from backend.app.main import create_app

PROFILE_PAYLOAD = {
    "gender": 1,
    "height": 172,
    "weight": 88,
    "ap_hi": 150,
    "ap_lo": 92,
    "smoke": 1,
    "alco": 0,
    "active": 0,
    "age_years": 61,
    "bmi": 29.75,
}

PROFILE = CardiovascularProfile(**PROFILE_PAYLOAD)

PREDICTION = Prediction(
    probability=0.35,
    classification=0,
    threshold=0.38,
    model_version="v1",
)

EXPLANATION = Explanation(
    top_factors=(
        ShapFactor(feature="ap_hi", value=150, shap_value=0.44, direction="increase"),
    )
)

REPORT = RecommendationReport(
    summary="Resumen de prueba.",
    considerations="Consideraciones de prueba.",
    note="PULSO ofrece información educativa.",
    insufficient_information=False,
    recommendations=(
        Recommendation(
            factor="Presión arterial sistólica",
            recommendation="Recomendación de prueba.",
            source_ids=("SOURCE_1",),
            sources=(
                DocumentSource(
                    source_id="SOURCE_1",
                    source="documento.pdf",
                    score=0.72,
                    lines=SourceLines(start=20, end=26),
                ),
            ),
        ),
    ),
)

SIMULATION = SimulationOutcome(
    original=ScenarioResult(probability=0.80, classification=1),
    simulated=ScenarioResult(probability=0.50, classification=1),
    probability_difference=-0.30,
    model_version="v1",
    threshold=0.38,
    applied_changes={"weight": 80},
)


class FakeModel:
    """Implementación en memoria del puerto CardiovascularModel."""

    def __init__(self, error: Exception | None = None):
        self.error = error
        self.calls: list[str] = []
        self.simulated_with: tuple[CardiovascularProfile, ScenarioChanges] | None = None

    async def predict(self, profile: CardiovascularProfile) -> Prediction:
        self.calls.append("predict")
        if self.error:
            raise self.error
        return PREDICTION

    async def explain(self, profile: CardiovascularProfile) -> Explanation:
        self.calls.append("explain")
        if self.error:
            raise self.error
        return EXPLANATION

    async def simulate(
        self,
        profile: CardiovascularProfile,
        changes: ScenarioChanges,
    ) -> SimulationOutcome:
        self.calls.append("simulate")
        self.simulated_with = (profile, changes)
        if self.error:
            raise self.error
        return SIMULATION


class FakeRecommendations:
    """Implementación en memoria del puerto RecommendationGenerator."""

    def __init__(self, error: Exception | None = None):
        self.error = error
        self.received: AnalysisContext | None = None

    async def generate(self, context: AnalysisContext) -> RecommendationReport:
        self.received = context
        if self.error:
            raise self.error
        return REPORT


@pytest.fixture
def repository() -> InMemoryAnalysisRepository:
    return InMemoryAnalysisRepository(ttl_seconds=60, max_entries=10)


@pytest.fixture
def model() -> FakeModel:
    return FakeModel()


@pytest.fixture
def recommendations() -> FakeRecommendations:
    return FakeRecommendations()


@pytest.fixture
def client(repository, model, recommendations):
    """API real con los puertos reemplazados por dobles de prueba."""
    app = create_app()
    app.dependency_overrides[dependencies.get_analysis_repository] = lambda: repository
    app.dependency_overrides[dependencies.get_cardiovascular_model] = lambda: model
    app.dependency_overrides[dependencies.get_recommendation_generator] = lambda: recommendations
    return TestClient(app)
