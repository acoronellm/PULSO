from ml_service.app.schemas import (
    PredictionRequest,
    SimulationChanges,
    SimulationRequest,
)
from ml_service.app.simulator import simulate
import pytest


def test_simulation_returns_expected_structure(
    monkeypatch,
):
    class FakePrediction:
        def __init__(
            self,
            probability,
            classification,
        ):
            self.probability = probability
            self.classification = classification

    calls = []

    def fake_predict(request):
        calls.append(request)

        if len(calls) == 1:
            return FakePrediction(
                probability=0.80,
                classification=1,
            )

        return FakePrediction(
            probability=0.50,
            classification=1,
        )

    monkeypatch.setattr(
        "ml_service.app.simulator.predict",
        fake_predict,
    )

    request = SimulationRequest(
        original=PredictionRequest(
            gender=1,
            height=172,
            weight=88,
            ap_hi=150,
            ap_lo=92,
            smoke=1,
            alco=0,
            active=0,
            age_years=61,
            bmi=29.75,
        ),
        changes=SimulationChanges(
            weight=80,
            ap_hi=130,
            smoke=0,
            active=1,
        ),
    )

    result = simulate(request)

    assert result.original.probability == 0.80
    assert result.simulated.probability == 0.50
    assert result.probability_difference == pytest.approx(-0.30)
    assert result.model_version == "v1"
    assert result.threshold == 0.38

def test_simulation_recalculates_bmi(
    monkeypatch,
):
    captured_requests = []

    class FakePrediction:
        probability = 0.5
        classification = 1

    def fake_predict(request):
        captured_requests.append(request)
        return FakePrediction()

    monkeypatch.setattr(
        "ml_service.app.simulator.predict",
        fake_predict,
    )

    request = SimulationRequest(
        original=PredictionRequest(
            gender=1,
            height=172,
            weight=88,
            ap_hi=150,
            ap_lo=92,
            smoke=1,
            alco=0,
            active=0,
            age_years=61,
            bmi=29.75,
        ),
        changes=SimulationChanges(
            weight=80,
        ),
    )

    simulate(request)

    simulated_request = captured_requests[1]

    expected_bmi = 80 / (1.72 ** 2)

    assert simulated_request.bmi == expected_bmi