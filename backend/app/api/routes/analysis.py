from fastapi import APIRouter, HTTPException

from backend.app.schemas.analysis import (
    AnalysisResponse,
    RagRequest,
    RagResponse,
    UserData,
)
from backend.app.services.ml_client import (
    MLClientError,
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
        return await generate_recommendations(
            payload
        )

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

        rag_request = RagRequest(
            prediction=prediction,
            user_data=user_data,
            shap=shap,
        )

        rag = await generate_recommendations(
            rag_request
        )

        return AnalysisResponse(
            prediction=prediction,
            shap=shap,
            rag=rag,
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

@router.post("/simulate")
async def simulate(
    payload: dict,
):
    try:
        return await simulate_scenario(
            payload
        )

    except MLClientError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc