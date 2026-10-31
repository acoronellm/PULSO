import time
from uuid import UUID

import pytest

from backend.app.schemas.analysis import (
    PredictionData,
    ShapData,
    UserData,
)
from backend.app.services.analysis_cache import (
    AnalysisCache,
    AnalysisNotFoundError,
)


USER_DATA = UserData(
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
)
PREDICTION = PredictionData(
    probability=0.35,
    classification=0,
    threshold=0.38,
    model_version="v1",
)
SHAP = ShapData(top_factors=[])


def test_cache_stores_and_retrieves_isolated_context():
    cache = AnalysisCache(ttl_seconds=60, max_entries=2)

    first_id = cache.store(USER_DATA, PREDICTION, SHAP)
    second_id = cache.store(
        USER_DATA.model_copy(update={"weight": 70, "bmi": 23.66}),
        PREDICTION,
        SHAP,
    )

    assert isinstance(first_id, UUID)
    assert cache.get(first_id).user_data.weight == 88
    assert cache.get(second_id).user_data.weight == 70


def test_cache_expires_context():
    cache = AnalysisCache(ttl_seconds=0.01, max_entries=2)
    analysis_id = cache.store(USER_DATA, PREDICTION, SHAP)

    time.sleep(0.02)

    with pytest.raises(AnalysisNotFoundError):
        cache.get(analysis_id)


def test_cache_evicts_oldest_context_when_full():
    cache = AnalysisCache(ttl_seconds=60, max_entries=1)
    first_id = cache.store(USER_DATA, PREDICTION, SHAP)
    second_id = cache.store(USER_DATA, PREDICTION, SHAP)

    with pytest.raises(AnalysisNotFoundError):
        cache.get(first_id)

    assert cache.get(second_id).prediction == PREDICTION
