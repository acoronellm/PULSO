from fastapi import FastAPI, HTTPException

from backend.app.schemas.analysis import (
    AnalysisResponse,
    RagRequest,
    SimulationRequest,
    SimulationResponse,
    UserData,
)
from backend.app.services.rag_client import (
    RagClientError,
    generate_recommendations,
)

from backend.app.schemas.analysis import (
    AnalysisResponse,
    PredictionData,
    RagRequest,
    ShapData,
    SimulationRequest,
    SimulationResponse,
    UserData,
)

from ml_service.app.explainer import explain
from ml_service.app.predictor import predict
from ml_service.app.simulator import simulate
from ml_service.app.schemas import PredictionRequest


app = FastAPI(
    title="PULSO Monolith Experimental",
    version="0.1.0",
)


def to_prediction_request(
    user_data: UserData,
) -> PredictionRequest:
    return PredictionRequest(
        **user_data.model_dump()
    )


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "architecture": "monolith",
    }


@app.post(
    "/api/analyze",
    response_model=AnalysisResponse,
)
async def analyze(
    user_data: UserData,
):
    try:
        ml_request = to_prediction_request(user_data)

        # ML interno
        ml_prediction = predict(ml_request)
        ml_shap = explain(ml_request)

        # Convertir schemas del ML Service
        # a los schemas que utiliza el Backend.
        prediction = PredictionData.model_validate(
            ml_prediction.model_dump()
        )

        shap = ShapData.model_validate(
            ml_shap.model_dump()
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

    except RagClientError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {str(exc)}",
        ) from exc


@app.post(
    "/api/simulate",
    response_model=SimulationResponse,
)
def simulate_endpoint(
    payload: SimulationRequest,
):
    try:
        original = PredictionRequest(
            **payload.original.model_dump()
        )

        from ml_service.app.schemas import (
            SimulationChanges,
            SimulationRequest as MlSimulationRequest,
        )

        ml_request = MlSimulationRequest(
            original=original,
            changes=SimulationChanges(
                **payload.changes.model_dump(
                    exclude_none=True
                )
            ),
        )

        return simulate(
            ml_request
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Error en simulación monolítica.",
        ) from exc