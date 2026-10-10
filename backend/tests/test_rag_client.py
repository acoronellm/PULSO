import httpx
import pytest

from backend.app.schemas.analysis import RagRequest
from backend.app.services.rag_client import (
    generate_recommendations,
)


@pytest.mark.asyncio
async def test_generate_recommendations(monkeypatch):
    payload = RagRequest(
        prediction={
            "probability": 0.35,
            "classification": 0,
            "threshold": 0.38,
            "model_version": "v1",
        },
        user_data={
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
        },
        shap={
            "top_factors": [
                {
                    "feature": "ap_hi",
                    "value": 150,
                    "shap_value": 0.44,
                    "direction": "increase",
                },
                {
                    "feature": "smoke",
                    "value": 1,
                    "shap_value": 0.31,
                    "direction": "increase",
                },
                {
                    "feature": "active",
                    "value": 0,
                    "shap_value": 0.19,
                    "direction": "increase",
                },
            ]
        },
    )

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "summary": "Resumen de prueba.",
                "recommendations": [
                    {
                        "factor": "Presión arterial sistólica",
                        "recommendation": "Recomendación de prueba.",
                        "source_ids": [
                            "SOURCE_1"
                        ],
                        "sources": [
                            {
                                "source_id": "SOURCE_1",
                                "source": "documento.pdf",
                                "score": 0.72,
                                "lines": {
                                    "from": 20,
                                    "to": 26,
                                },
                            }
                        ],
                    }
                ],
                "considerations": "Consideraciones de prueba.",
                "note": "PULSO ofrece información educativa.",
                "insufficient_information": False,
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(
        "backend.app.services.rag_client."
        "settings.rag_service_url",
        "http://fake-rag",
    )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    result = await generate_recommendations(
        payload
    )

    assert result.summary == "Resumen de prueba."

    assert len(
        result.recommendations
    ) == 1

    recommendation = (
        result.recommendations[0]
    )

    assert (
        recommendation.factor
        == "Presión arterial sistólica"
    )

    assert (
        recommendation.source_ids
        == ["SOURCE_1"]
    )

    assert len(
        recommendation.sources
    ) == 1

    source = recommendation.sources[0]

    assert source.source_id == "SOURCE_1"
    assert source.source == "documento.pdf"
    assert source.score == 0.72
    assert source.lines.from_ == 20
    assert source.lines.to == 26

    assert (
        result.insufficient_information
        is False
    )