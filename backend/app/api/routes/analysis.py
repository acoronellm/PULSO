from fastapi import APIRouter, HTTPException

from backend.app.schemas.analysis import (
    AnalysisResponse,
    RagGenerationRequest,
    RagRequest,
    RagResponse,
    SimulationRequest,
    SimulationResponse,
    UserData,
)
from backend.app.services.ml_client import (
    MLClientError,
    MLValidationError,
    generate_prediction,
    generate_explanation,
    simulate_scenario
)
from backend.app.services.analysis_cache import (
    AnalysisCache,
    AnalysisNotFoundError,
)
from backend.app.core.config import settings
from backend.app.services.rag_client import (
    RagClientError,
    generate_recommendations,
)


router = APIRouter()
analysis_cache = AnalysisCache(
    ttl_seconds=settings.analysis_cache_ttl_seconds,
    max_entries=settings.analysis_cache_max_entries,
)


@router.post(
    "/rag",
    response_model=RagResponse,
)
async def rag_analysis(
    payload: RagRequest,
):
    try:
        context = analysis_cache.get(
            payload.analysis_id
        )

        return await generate_recommendations(
            RagGenerationRequest(
                prediction=context.prediction,
                user_data=context.user_data,
                shap=context.shap,
            )
        )

    except AnalysisNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="El análisis no existe o ya expiró.",
        ) from exc

    except RagClientError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
)
async def analyze(
    user_data: UserData,
):
    try:
        prediction = await generate_prediction(
            user_data
        )

        shap = await generate_explanation(
            user_data
        )
        analysis_id = analysis_cache.store(
            user_data,
            prediction,
            shap,
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            prediction=prediction,
            shap=shap,
        )

    except MLClientError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

@router.post(
    "/simulate",
    response_model=SimulationResponse,
)
async def simulate(
    payload: SimulationRequest,
):
    try:
        return await simulate_scenario(
            payload
        )

    except MLValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except MLClientError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc