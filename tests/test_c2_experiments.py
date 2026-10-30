"""Pruebas rápidas de contratos de C2: no requieren dataset real ni entrenamientos costosos."""
import numpy as np
import pandas as pd
import pytest

pytest.importorskip('mlflow')
from ml.common import FEATURES
from experiments.age_specialized_models.c2.motor import (
    CONFIGS, FOLDS, GRUPOS, grupo_edades, validate_partition,
    validate_probabilities, make_pipeline,
)


def fake_split(n=12):
    rows = []
    for i in range(n):
        row = dict.fromkeys(FEATURES, 0.0)
        row.update(gender=1, height=170, weight=75, ap_hi=120,
                   ap_lo=80, age_years=40 + i / 100, bmi=25.95,
                   smoke=0, alco=0, active=1)
        rows.append(row)
    return pd.DataFrame(rows, columns=FEATURES), pd.Series([0, 1] * (n // 2))


def test_age_boundaries():
    assert grupo_edades([49.99, 50, 59.99, 60, 64.9]).tolist() == [
        'menor_50', '50_59', '50_59', '60_64', '60_64']


def test_group_partition_contract_and_disjoint_indices():
    X, y = fake_split()
    validate_partition(X.iloc[:6], y.iloc[:6], X.iloc[6:], y.iloc[6:], 'menor_50')
    with pytest.raises(ValueError, match='comparten índices'):
        validate_partition(X.iloc[:6], y.iloc[:6], X.iloc[:6], y.iloc[:6], 'menor_50')


def test_rejects_wrong_age_group():
    X, y = fake_split()
    X.loc[9, 'age_years'] = 62
    with pytest.raises(ValueError, match='fuera del rango'):
        validate_partition(X.iloc[:6], y.iloc[:6], X.iloc[6:], y.iloc[6:], 'menor_50')


class FakeProbModel:
    classes_ = np.array([0, 1])
    def predict_proba(self, X):
        return np.tile(np.array([[0.3, 0.7]]), (len(X), 1))


def test_probability_contract():
    X, _ = fake_split()
    assert np.allclose(validate_probabilities(FakeProbModel(), X), 0.7)


def test_all_algorithms_construct_pipeline():
    for name, spec in CONFIGS.items():
        pipeline = make_pipeline({'model_type': name, 'model_params': spec['base'], 'threshold': 0.38})
        assert 'preprocessor' in pipeline.named_steps
        assert 'model' in pipeline.named_steps
    assert FOLDS == 5 and set(GRUPOS) == {'global', 'menor_50', '50_59', '60_64'}


def test_original_search_spaces_and_baselines():
    from experiments.age_specialized_models.c2.motor import build_candidates, BUDGET
    for algorithm in CONFIGS:
        candidates, method, search, baseline, original_count, original = build_candidates(algorithm)
        assert search.exists() and baseline.exists()
        assert any(candidate == original for candidate in candidates)
        assert len(candidates) <= (BUDGET[algorithm] or original_count) + 1
        assert original_count >= len(candidates) - 1
        assert method in {'GridSearchCV_equivalente_manual', 'RandomizedSearchCV_equivalente_manual'}

def test_candidate_selection_is_reproducible():
    from experiments.age_specialized_models.c2.motor import build_candidates
    for algorithm in CONFIGS:
        assert build_candidates(algorithm)[0] == build_candidates(algorithm)[0]
