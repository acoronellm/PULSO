"""Composición de dependencias: conecta los casos de uso con sus implementaciones.

Es el único lugar que conoce las clases concretas de infraestructura. Las
pruebas reemplazan estas funciones con app.dependency_overrides.
"""

from functools import lru_cache

from fastapi import Depends

from ...application.use_cases.analyze_profile import AnalyzeProfile
from ...application.use_cases.request_recommendations import RequestRecommendations
from ...application.use_cases.simulate_scenario import SimulateScenario
from ...domain.ports import AnalysisRepository, CardiovascularModel, RecommendationGenerator
from ...infrastructure.config import Settings
from ...infrastructure.in_memory_analysis_repository import InMemoryAnalysisRepository
from ...infrastructure.ml_service_client import MLServiceClient
from ...infrastructure.n8n_rag_client import N8nRecommendationClient


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_analysis_repository() -> AnalysisRepository:
    # Una sola instancia por proceso: los análisis viven en su memoria
    settings = get_settings()
    return InMemoryAnalysisRepository(
        ttl_seconds=settings.analysis_cache_ttl_seconds,
        max_entries=settings.analysis_cache_max_entries,
    )


def get_cardiovascular_model() -> CardiovascularModel:
    settings = get_settings()
    return MLServiceClient(
        base_url=settings.ml_service_url,
        timeout_seconds=settings.ml_timeout_seconds,
    )


def get_recommendation_generator() -> RecommendationGenerator:
    settings = get_settings()
    return N8nRecommendationClient(
        url=settings.rag_service_url,
        timeout_seconds=settings.rag_timeout_seconds,
    )


def get_analyze_profile(
    model: CardiovascularModel = Depends(get_cardiovascular_model),
    repository: AnalysisRepository = Depends(get_analysis_repository),
) -> AnalyzeProfile:
    return AnalyzeProfile(model=model, repository=repository)


def get_request_recommendations(
    repository: AnalysisRepository = Depends(get_analysis_repository),
    recommendations: RecommendationGenerator = Depends(get_recommendation_generator),
) -> RequestRecommendations:
    return RequestRecommendations(repository=repository, recommendations=recommendations)


def get_simulate_scenario(
    model: CardiovascularModel = Depends(get_cardiovascular_model),
) -> SimulateScenario:
    return SimulateScenario(model=model)
