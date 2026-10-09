from fastapi import APIRouter, HTTPException

from backend.app.schemas.analysis import (
    RagRequest,
    RagResponse,
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