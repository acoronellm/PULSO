"""Composición de dependencias: conecta los casos de uso con sus implementaciones.

Es el único lugar que conoce las clases concretas de infraestructura. Las
pruebas reemplazan estas funciones con app.dependency_overrides.
"""

from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ...application.use_cases.authenticate_user import AuthenticateUser
from ...application.use_cases.analyze_profile import AnalyzeProfile
from ...application.use_cases.list_analysis_history import ListAnalysisHistory
from ...application.use_cases.register_user import RegisterUser
from ...application.use_cases.request_recommendations import RequestRecommendations
from ...application.use_cases.simulate_scenario import SimulateScenario
from ...domain.entities import AuthUser
from ...domain.ports import (
    AccessTokenIssuer,
    AnalysisRepository,
    AnalysisHistoryRepository,
    CardiovascularModel,
    PasswordHasher,
    RecommendationGenerator,
    UserRepository,
)
from ...infrastructure.config import Settings
from ...infrastructure.database import get_db_session
from ...infrastructure.in_memory_analysis_repository import InMemoryAnalysisRepository
from ...infrastructure.sqlalchemy_analysis_history_repository import (
    SQLAlchemyAnalysisHistoryRepository,
)
from ...infrastructure.jwt_access_tokens import JWTAccessTokens
from ...infrastructure.ml_service_client import MLServiceClient
from ...infrastructure.n8n_rag_client import N8nRecommendationClient
from ...infrastructure.password_hasher import Argon2PasswordHasher
from ...infrastructure.sqlalchemy_user_repository import SQLAlchemyUserRepository

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_user_repository(
    session: Session = Depends(get_db_session),
) -> UserRepository:
    return SQLAlchemyUserRepository(session)


def get_analysis_history_repository(
    session: Session = Depends(get_db_session),
) -> AnalysisHistoryRepository:
    return SQLAlchemyAnalysisHistoryRepository(session)


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()


def get_access_token_issuer() -> AccessTokenIssuer:
    return JWTAccessTokens(get_settings())


def get_register_user(
    users: UserRepository = Depends(get_user_repository),
    passwords: PasswordHasher = Depends(get_password_hasher),
    tokens: AccessTokenIssuer = Depends(get_access_token_issuer),
) -> RegisterUser:
    return RegisterUser(users=users, passwords=passwords, tokens=tokens)


def get_authenticate_user(
    users: UserRepository = Depends(get_user_repository),
    passwords: PasswordHasher = Depends(get_password_hasher),
    tokens: AccessTokenIssuer = Depends(get_access_token_issuer),
) -> AuthenticateUser:
    return AuthenticateUser(users=users, passwords=passwords, tokens=tokens)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    users: UserRepository = Depends(get_user_repository),
    tokens: AccessTokenIssuer = Depends(get_access_token_issuer),
) -> AuthUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = tokens.subject(credentials.credentials)
    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = users.find_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


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
    history_repository: AnalysisHistoryRepository = Depends(get_analysis_history_repository),
) -> AnalyzeProfile:
    return AnalyzeProfile(
        model=model,
        repository=repository,
        history_repository=history_repository,
    )


def get_list_analysis_history(
    repository: AnalysisHistoryRepository = Depends(get_analysis_history_repository),
) -> ListAnalysisHistory:
    return ListAnalysisHistory(repository)


def get_request_recommendations(
    repository: AnalysisRepository = Depends(get_analysis_repository),
    recommendations: RecommendationGenerator = Depends(get_recommendation_generator),
) -> RequestRecommendations:
    return RequestRecommendations(repository=repository, recommendations=recommendations)


def get_simulate_scenario(
    model: CardiovascularModel = Depends(get_cardiovascular_model),
) -> SimulateScenario:
    return SimulateScenario(model=model)
