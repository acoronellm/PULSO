import time
from dataclasses import replace
from uuid import UUID

import pytest

from backend.app.domain.entities import AnalysisContext
from backend.app.domain.errors import AnalysisNotFoundError
from backend.app.infrastructure.in_memory_analysis_repository import InMemoryAnalysisRepository

from conftest import EXPLANATION, PREDICTION, PROFILE

CONTEXT = AnalysisContext(profile=PROFILE, prediction=PREDICTION, explanation=EXPLANATION)


def test_repository_stores_and_retrieves_each_context():
    repository = InMemoryAnalysisRepository(ttl_seconds=60, max_entries=2)

    first_id = repository.save(CONTEXT)
    second_id = repository.save(
        replace(CONTEXT, profile=replace(PROFILE, weight=70, bmi=23.66))
    )

    assert isinstance(first_id, UUID)
    assert repository.get(first_id).profile.weight == 88
    assert repository.get(second_id).profile.weight == 70


def test_repository_expires_context():
    repository = InMemoryAnalysisRepository(ttl_seconds=0.01, max_entries=2)
    analysis_id = repository.save(CONTEXT)

    time.sleep(0.02)

    with pytest.raises(AnalysisNotFoundError):
        repository.get(analysis_id)


def test_repository_evicts_oldest_context_when_full():
    repository = InMemoryAnalysisRepository(ttl_seconds=60, max_entries=1)
    first_id = repository.save(CONTEXT)
    second_id = repository.save(CONTEXT)

    with pytest.raises(AnalysisNotFoundError):
        repository.get(first_id)

    assert repository.get(second_id).prediction == PREDICTION


def test_repository_rejects_invalid_limits():
    with pytest.raises(ValueError):
        InMemoryAnalysisRepository(ttl_seconds=0, max_entries=1)
    with pytest.raises(ValueError):
        InMemoryAnalysisRepository(ttl_seconds=1, max_entries=0)
