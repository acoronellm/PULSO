import pytest

from ml_service.app.config import MODEL_PATH
from ml_service.app.model_loader import load_model
from ml_service.app.predictor import predict
from ml_service.app.schemas import PredictionRequest


pytestmark = pytest.mark.skipif(
    not MODEL_PATH.exists(),
    reason="El artefacto real PULSO v1 no está disponible.",
)


def test_real_model_can_predict():
    model = load_model()

    assert model is not None

    request = PredictionRequest(
        gender=1,
        height=170,
        weight=80,
        ap_hi=150,
        ap_lo=90,
        smoke=0,
        alco=0,
        active=1,
        age_years=55,
        bmi=27.68,
    )

    result = predict(request)

    assert 0 <= result.probability <= 1
    assert result.classification in [0, 1]
    assert result.threshold == 0.38
    assert result.model_version == "v1"