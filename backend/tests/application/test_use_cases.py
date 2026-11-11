from uuid import uuid4

import pytest

from backend.app.application.use_cases.analyze_profile import AnalyzeProfile
from backend.app.application.use_cases.request_recommendations import RequestRecommendations
from backend.app.application.use_cases.simulate_scenario import SimulateScenario
from backend.app.domain.entities import ScenarioChanges
from backend.app.domain.errors import AnalysisNotFoundError, ModelServiceError

from conftest import EXPLANATION, PREDICTION, PROFILE, REPORT, SIMULATION, FakeModel


@pytest.mark.asyncio
async def test_analyze_profile_predicts_explains_and_stores_context(model, repository):
    result = await AnalyzeProfile(model, repository).execute(PROFILE)

    assert result.prediction == PREDICTION
    assert result.explanation == EXPLANATION
    assert model.calls == ["predict", "explain"]

    stored = repository.get(result.analysis_id)
    assert stored.profile == PROFILE
    assert stored.prediction == PREDICTION


@pytest.mark.asyncio
async def test_analyze_profile_does_not_store_when_model_fails(repository):
    model = FakeModel(error=ModelServiceError("ML Service no disponible."))

    with pytest.raises(ModelServiceError):
        await AnalyzeProfile(model, repository).execute(PROFILE)


@pytest.mark.asyncio
async def test_recommendations_use_stored_context_without_running_the_model(
    model, repository, recommendations
):
    analysis = await AnalyzeProfile(model, repository).execute(PROFILE)
    model.calls.clear()

    report = await RequestRecommendations(repository, recommendations).execute(analysis.analysis_id)

    assert report == REPORT
    assert recommendations.received.profile == PROFILE
    assert recommendations.received.prediction == PREDICTION
    assert model.calls == []


@pytest.mark.asyncio
async def test_recommendations_fail_for_unknown_analysis(repository, recommendations):
    with pytest.raises(AnalysisNotFoundError):
        await RequestRecommendations(repository, recommendations).execute(uuid4())

    assert recommendations.received is None


@pytest.mark.asyncio
async def test_simulate_scenario_delegates_to_model(model):
    changes = ScenarioChanges(weight=80)

    outcome = await SimulateScenario(model).execute(PROFILE, changes)

    assert outcome == SIMULATION
    assert model.simulated_with == (PROFILE, changes)
