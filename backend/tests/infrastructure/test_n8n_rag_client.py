import json

import httpx
import pytest

from backend.app.domain.entities import AnalysisContext
from backend.app.domain.errors import RecommendationServiceError
from backend.app.infrastructure.n8n_rag_client import N8nRecommendationClient

from conftest import EXPLANATION, PREDICTION, PROFILE, PROFILE_PAYLOAD

CONTEXT = AnalysisContext(profile=PROFILE, prediction=PREDICTION, explanation=EXPLANATION)

RAG_RESPONSE = {
    "summary": "Resumen de prueba.",
    "recommendations": [
        {
            "factor": "Presión arterial sistólica",
            "recommendation": "Recomendación de prueba.",
            "source_ids": ["SOURCE_1"],
            "sources": [
                {
                    "source_id": "SOURCE_1",
                    "source": "documento.pdf",
                    "score": 0.72,
                    "lines": {"from": 20, "to": 26},
                }
            ],
        }
    ],
    "considerations": "Consideraciones de prueba.",
    "note": "PULSO ofrece información educativa.",
    "insufficient_information": False,
}


def rag_client(handler, url: str = "http://fake-rag") -> N8nRecommendationClient:
    return N8nRecommendationClient(url, 5, transport=httpx.MockTransport(handler))


@pytest.mark.asyncio
async def test_generate_sends_context_and_maps_response():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=RAG_RESPONSE)

    report = await rag_client(handler).generate(CONTEXT)

    body = json.loads(requests[0].content)
    assert body["user_data"] == PROFILE_PAYLOAD
    assert body["prediction"]["threshold"] == 0.38
    assert body["shap"]["top_factors"][0]["feature"] == "ap_hi"

    assert report.summary == "Resumen de prueba."
    recommendation = report.recommendations[0]
    assert recommendation.factor == "Presión arterial sistólica"
    assert recommendation.source_ids == ("SOURCE_1",)
    source = recommendation.sources[0]
    assert source.source == "documento.pdf"
    assert source.score == 0.72
    assert (source.lines.start, source.lines.end) == (20, 26)
    assert report.insufficient_information is False


@pytest.mark.asyncio
async def test_generate_requires_configured_url():
    with pytest.raises(RecommendationServiceError, match="RAG_SERVICE_URL no está configurado."):
        await rag_client(lambda request: httpx.Response(200), url="").generate(CONTEXT)


@pytest.mark.asyncio
async def test_generate_rejects_empty_body():
    # n8n responde 200 sin cuerpo cuando el workflow se detiene antes de responder
    with pytest.raises(RecommendationServiceError, match="no es JSON válido"):
        await rag_client(lambda request: httpx.Response(200, content=b"")).generate(CONTEXT)


@pytest.mark.asyncio
async def test_generate_rejects_non_object_json():
    with pytest.raises(RecommendationServiceError, match="debe ser un objeto JSON"):
        await rag_client(lambda request: httpx.Response(200, json=[])).generate(CONTEXT)


@pytest.mark.asyncio
async def test_generate_rejects_response_outside_contract():
    with pytest.raises(RecommendationServiceError, match="no cumple el contrato esperado"):
        await rag_client(lambda request: httpx.Response(200, json={"summary": "x"})).generate(CONTEXT)


@pytest.mark.asyncio
async def test_generate_maps_http_errors():
    with pytest.raises(RecommendationServiceError, match="HTTP 503"):
        await rag_client(lambda request: httpx.Response(503)).generate(CONTEXT)
@pytest.mark.asyncio
async def test_generate_preserves_factor_explanations_and_source_metadata():
    response_data = {
        **RAG_RESPONSE,
        "factor_explanations": [
            {
                "query_group": "blood_pressure",
                "factor": "presión arterial",
                "features": ["ap_hi", "ap_lo"],
                "explanation": "La presión arterial es un factor relacionado con la salud cardiovascular.",
                "source_ids": ["SOURCE_3"],
                "sources": [
                    {
                        "source_id": "SOURCE_3",
                        "source": "Documento sobre presión arterial",
                        "author": "American Heart Association",
                        "publication_year": 2025,
                        "source_url": "https://example.org/documento",
                        "pdf_url": None,
                        "score": None,
                        "lines": None,
                    }
                ],
            }
        ],
        "retrieval_evaluation": {"documents_retrieved": 5},
        "validation_audit": {"semantic_auditor_performed": False},
    }

    report = await rag_client(
        lambda request: httpx.Response(200, json=response_data)
    ).generate(CONTEXT)

    assert len(report.factor_explanations) == 1

    explanation = report.factor_explanations[0]

    assert explanation.query_group == "blood_pressure"
    assert explanation.factor == "presión arterial"
    assert explanation.features == ("ap_hi", "ap_lo")
    assert explanation.source_ids == ("SOURCE_3",)
    assert explanation.explanation.startswith("La presión arterial")

    source = explanation.sources[0]

    assert source.author == "American Heart Association"
    assert source.publication_year == 2025
    assert source.source_url == "https://example.org/documento"
    assert source.pdf_url is None
    assert source.score is None
    assert source.lines is None

    assert report.summary == "Resumen de prueba."
    assert len(report.recommendations) == 1

@pytest.mark.asyncio
async def test_generate_handles_rag_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Tiempo de espera agotado.", request=request)

    with pytest.raises(
        RecommendationServiceError,
        match="No fue posible comunicarse con el servicio RAG",
    ):
        await rag_client(handler).generate(CONTEXT)
@pytest.mark.asyncio
async def test_generate_rejects_invalid_factor_explanation():
    response_data = {
        **RAG_RESPONSE,
        "factor_explanations": [
            {
                "query_group": "blood_pressure",
                "factor": "presión arterial",
                "features": ["ap_hi", "ap_lo"],
                "explanation": 123,
                "source_ids": [],
                "sources": [],
            }
        ],
    }

    with pytest.raises(
        RecommendationServiceError,
        match="no cumple el contrato esperado",
    ):
        await rag_client(
            lambda request: httpx.Response(200, json=response_data)
        ).generate(CONTEXT)
@pytest.mark.asyncio
async def test_generate_rejects_more_than_three_recommendations():
    response_data = {
        **RAG_RESPONSE,
        "recommendations": RAG_RESPONSE["recommendations"] * 4,
    }

    with pytest.raises(
        RecommendationServiceError,
        match="no cumple el contrato esperado",
    ):
        await rag_client(
            lambda request: httpx.Response(200, json=response_data)
        ).generate(CONTEXT)

@pytest.mark.asyncio
async def test_generate_rejects_missing_source_references():
    recommendation = {
        **RAG_RESPONSE["recommendations"][0],
        "source_ids": ["SOURCE_INEXISTENTE"],
    }

    response_data = {
        **RAG_RESPONSE,
        "recommendations": [recommendation],
    }

    with pytest.raises(
        RecommendationServiceError,
        match="no cumple el contrato esperado",
    ):
        await rag_client(
            lambda request: httpx.Response(200, json=response_data)
        ).generate(CONTEXT)
@pytest.mark.asyncio
async def test_generate_accepts_explanations_without_recommendations():
    response_data = {
        **RAG_RESPONSE,
        "recommendations": [],
        "factor_explanations": [
            {
                "query_group": "age",
                "factor": "edad",
                "features": ["age_years"],
                "explanation": "La edad se relaciona con cambios cardiovasculares.",
                "source_ids": ["SOURCE_1"],
                "sources": [
                    {
                        "source_id": "SOURCE_1",
                        "source": "Documento educativo",
                        "author": None,
                        "publication_year": None,
                        "source_url": None,
                        "pdf_url": None,
                        "score": None,
                        "lines": None,
                    }
                ],
            }
        ],
        "insufficient_information": False,
    }

    report = await rag_client(
        lambda request: httpx.Response(200, json=response_data)
    ).generate(CONTEXT)

    assert report.recommendations == ()
    assert len(report.factor_explanations) == 1
    assert report.factor_explanations[0].factor == "edad"
    assert report.insufficient_information is False