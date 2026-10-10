import httpx

from backend.app.core.config import settings
from backend.app.schemas.analysis import (
    RagRequest,
    RagResponse,
)


class RagClientError(Exception):
    """Error de comunicación o respuesta inválida del servicio RAG."""


async def generate_recommendations(
    payload: RagRequest,
) -> RagResponse:
    """
    Envía el contexto de PULSO al servicio RAG
    y devuelve la respuesta validada.
    """

    if not settings.rag_service_url:
        raise RagClientError(
            "RAG_SERVICE_URL no está configurado."
        )

    try:
        async with httpx.AsyncClient(
            timeout=settings.rag_timeout_seconds,
        ) as client:
            response = await client.post(
                settings.rag_service_url,
                json=payload.model_dump(),
            )

    except httpx.RequestError as exc:
        raise RagClientError(
            "No fue posible comunicarse con el servicio RAG."
        ) from exc

    if response.status_code >= 400:
        raise RagClientError(
            f"El servicio RAG respondió con "
            f"HTTP {response.status_code}."
        )

    try:
        response_data = response.json()

    except Exception as exc:
        raise RagClientError(
            "El servicio RAG devolvió una respuesta "
            "que no es JSON válido."
        ) from exc

    if not isinstance(response_data, dict):
        raise RagClientError(
            "La respuesta del servicio RAG debe ser un objeto JSON."
        )

    try:
        return RagResponse.model_validate(
            response_data
        )

    except Exception as exc:
        raise RagClientError(
            "La respuesta del servicio RAG "
            "no cumple el contrato esperado."
        ) from exc