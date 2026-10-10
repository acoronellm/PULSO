from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


VALID_PAYLOAD = {
    "prediction": {
        "probability": 0.35,
        "threshold": 0.38,
        "classification": 0,
        "model_version": "v1",
    },
    "user_data": {
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
    "shap": {
        "top_factors": [
            {
                "feature": "ap_hi",
                "value": 150,
                "shap_value": 0.44,
                "direction": "increase",
            }
        ]
    },
}


def test_rag_route(monkeypatch):
    async def fake_generate_recommendations(payload):
        return {
            "summary": "Resumen de prueba.",
            "recommendations": [
                {
                    "factor": "Presión arterial",
                    "recommendation": "Recomendación de prueba.",
                    "source_ids": ["SOURCE_1"],
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

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.generate_recommendations",
        fake_generate_recommendations,
    )

    response = client.post(
        "/api/rag",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["summary"] == "Resumen de prueba."
    assert len(body["recommendations"]) == 1
    assert body["insufficient_information"] is False
def test_rag_route_returns_502_on_rag_error(monkeypatch):
    from backend.app.services.rag_client import RagClientError

    async def fake_generate_recommendations(payload):
        raise RagClientError(
            "No fue posible comunicarse con el servicio RAG."
        )

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.generate_recommendations",
        fake_generate_recommendations,
    )

    response = client.post(
        "/api/rag",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 502

    assert (
        response.json()["detail"]
        == "No fue posible comunicarse con el servicio RAG."
    )