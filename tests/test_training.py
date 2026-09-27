
"""Pruebas sin datos clínicos ni conexión a MLflow."""
import numpy as np
import pandas as pd
import pytest
from ml.common import FEATURES, load_dataset, make_pipeline, split_data
from ml.evaluate import evaluate


def synthetic_data(n=200):
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "gender": rng.choice([1, 2], n), "height": rng.integers(150, 191, n),
        "weight": rng.integers(50, 110, n), "ap_hi": rng.integers(100, 170, n),
        "ap_lo": rng.integers(60, 99, n), "smoke": rng.integers(0, 2, n),
        "alco": rng.integers(0, 2, n), "active": rng.integers(0, 2, n),
        "age_years": rng.integers(30, 75, n), "bmi": rng.uniform(18, 37, n),
        "cardio": np.tile([0, 1], n // 2),
        "cholesterol": 1, "gluc": 1, "age": 20000, "id": np.arange(n),
    })
    return df


def test_load_keeps_exclusions_out_of_x(tmp_path):
    p = tmp_path / "clean.csv"
    synthetic_data().to_csv(p, index=False)
    X, y = load_dataset(p)
    assert list(X.columns) == FEATURES
    assert {"cholesterol", "gluc", "id", "age"}.isdisjoint(X.columns)
    assert set(y.unique()) == {0, 1}


def test_partitions_are_disjoint_and_repeatable():
    df = synthetic_data()
    X, y = df[FEATURES], df["cardio"]
    a = split_data(X, y)
    b = split_data(X, y)
    ids = [set(part[0].index) for part in a]
    assert [len(part[0]) for part in a] == [140, 30, 30]
    assert not (ids[0] & ids[1] or ids[0] & ids[2] or ids[1] & ids[2])
    assert all(a[i][0].index.equals(b[i][0].index) for i in range(3))


@pytest.mark.parametrize("kind,params", [
    (
        "logistic_regression",
        {
            "max_iter": 1000,
            "random_state": 42
        }
    ),
    (
        "decision_tree",
        {
            "max_depth": 5,
            "min_samples_leaf": 50,
            "random_state": 42
        }
    ),
    (
        "xgboost",
        {
            "n_estimators": 20,
            "max_depth": 3,
            "learning_rate": 0.1,
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "tree_method": "hist",
            "random_state": 42,
            "n_jobs": 1
        }
    ),
])
def test_models_fit_and_evaluate(kind, params):
    df = synthetic_data()
    (Xt, yt), (Xv, yv), _ = split_data(df[FEATURES], df["cardio"])
    pipeline = make_pipeline({"model_type": kind, "model_params": params})
    pipeline.fit(Xt, yt)
    metrics = evaluate(pipeline, Xv, yv)
    assert set(metrics) >= {"roc_auc", "brier", "accuracy", "specificity"}
    assert 0 <= metrics["roc_auc"] <= 1
    assert 0 <= metrics["brier"] <= 1
