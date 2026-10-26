from fastapi import APIRouter, HTTPException

from backend.app.schemas.analysis import (
    AnalysisResponse,
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
from backend.app.services.rag_client import (
    RagClientError,
    generate_recommendations,
)


router = APIRouter()


@router.post(
    "/rag",
    response_model=RagResponse,
)
async def rag_analysis(
    payload: RagRequest,
):
    try:
        verified_prediction = await generate_prediction(
            payload.user_data
        )
        verified_shap = await generate_explanation(
            payload.user_data
        )

        if (
            payload.prediction.model_dump()
            != verified_prediction.model_dump()
            or payload.shap.model_dump()
            != verified_shap.model_dump()
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "El contexto de recomendaciones no coincide "
                    "con un análisis válido."
                ),
            )

        verified_payload = RagRequest(
            prediction=verified_prediction,
            user_data=payload.user_data,
            shap=verified_shap,
        )

        return await generate_recommendations(
            verified_payload
        )

    except MLClientError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
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

        return AnalysisResponse(
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