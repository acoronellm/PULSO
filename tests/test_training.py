"""Pruebas del pipeline de entrenamiento con datos sintéticos."""

import numpy as np
import pandas as pd
import pytest

from sklearn.model_selection import GridSearchCV

from ml.threshold import search_threshold
from ml.common import (
    FEATURES,
    load_dataset,
    make_pipeline,
    split_data,
)

from ml.evaluate import evaluate


def synthetic_data(n=200):
    """
    Genera un dataset sintético con la misma estructura básica
    utilizada por los modelos de PULSO.
    """

    rng = np.random.default_rng(42)

    df = pd.DataFrame({
        "gender": rng.choice([1, 2], n),
        "height": rng.integers(150, 191, n),
        "weight": rng.integers(50, 110, n),
        "ap_hi": rng.integers(100, 170, n),
        "ap_lo": rng.integers(60, 99, n),
        "smoke": rng.integers(0, 2, n),
        "alco": rng.integers(0, 2, n),
        "active": rng.integers(0, 2, n),
        "age_years": rng.integers(30, 75, n),
        "bmi": rng.uniform(18, 37, n),

        # Variable objetivo balanceada
        "cardio": np.tile([0, 1], n // 2),

        # Variables presentes en el CSV depurado,
        # pero actualmente excluidas del entrenamiento
        "cholesterol": 1,
        "gluc": 1,

        # Variables conservadas para trazabilidad
        "age": 20000,
        "id": np.arange(n),
    })

    return df


def test_load_keeps_exclusions_out_of_x(tmp_path):
    """
    Comprueba que las variables excluidas no formen parte de X.
    """

    path = tmp_path / "clean.csv"

    synthetic_data().to_csv(
        path,
        index=False,
    )

    X, y = load_dataset(path)

    assert list(X.columns) == FEATURES

    assert {
        "cholesterol",
        "gluc",
        "id",
        "age",
    }.isdisjoint(X.columns)

    assert set(y.unique()) == {0, 1}


def test_partitions_are_disjoint_and_repeatable():
    """
    Comprueba que las particiones:

    - tengan el tamaño esperado;
    - no compartan registros;
    - sean reproducibles.
    """

    df = synthetic_data()
 

    X = df[FEATURES]
    y = df["cardio"]

    first_split = split_data(
        X,
        y,
    )

    second_split = split_data(
        X,
        y,
    )

    # Para 200 registros:
    # 70 % = 140
    # 15 % = 30
    # 15 % = 30

    assert [
        len(part[0])
        for part in first_split
    ] == [140, 30, 30]

    indexes = [
        set(part[0].index)
        for part in first_split
    ]

    # Train y validation no deben cruzarse
    assert not (
        indexes[0]
        & indexes[1]
    )

    # Train y test no deben cruzarse
    assert not (
        indexes[0]
        & indexes[2]
    )

    # Validation y test no deben cruzarse
    assert not (
        indexes[1]
        & indexes[2]
    )

    # La división debe ser reproducible
    assert all(
        first_split[i][0].index.equals(
            second_split[i][0].index
        )
        for i in range(3)
    )

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
        "random_forest",
        {
            "n_estimators": 20,
            "random_state": 42,
            "n_jobs": 1
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
    (
        "gradient_boosting",
        {
            "n_estimators": 20,
            "learning_rate": 0.1,
            "max_depth": 3,
            "random_state": 42
        }
    ),
])
def test_models_fit_and_evaluate(kind, params):
    
    df = synthetic_data()

    X = df[FEATURES]
    y = df["cardio"]

    (
        X_train,
        y_train,
    ), (
        X_val,
        y_val,
    ), _ = split_data(
        X,
        y,
    )

    pipeline = make_pipeline({
        "model_type": kind,
        "model_params": params,
    })

    pipeline.fit(
        X_train,
        y_train,
    )

    metrics = evaluate(
        pipeline,
        X_val,
        y_val,
    )

    # Verificar que existan las métricas principales
    assert set(metrics) >= {
        "accuracy",
        "precision",
        "recall",
        "specificity",
        "f1",
        "roc_auc",
        "brier",
    }

    # ROC-AUC debe estar entre 0 y 1
    assert (
        0
        <= metrics["roc_auc"]
        <= 1
    )

    # Brier score debe estar entre 0 y 1
    assert (
        0
        <= metrics["brier"]
        <= 1
    )
def test_gridsearch_finds_best_estimator():
    """
    Comprueba que GridSearchCV pueda ejecutarse sobre el pipeline
    utilizando únicamente Train y devolver una mejor configuración.
    """

    df = synthetic_data()

    X = df[FEATURES]
    y = df["cardio"]

    (
        X_train,
        y_train,
    ), (
        X_val,
        y_val,
    ), (
        X_test,
        y_test,
    ) = split_data(
        X,
        y,
    )

    pipeline = make_pipeline({
        "model_type": "decision_tree",
        "model_params": {
            "random_state": 42
        },
    })

    param_grid = {
        "model__max_depth": [3, 5]
    }

    grid = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=2,
        n_jobs=1,
    )

    grid.fit(
        X_train,
        y_train,
    )

    assert grid.best_estimator_ is not None

    assert grid.best_params_["model__max_depth"] in [
        3,
        5,
    ]

    assert (
        0
        <= grid.best_score_
        <= 1
    )
def test_threshold_selection_meets_minimum_recall():
    """
    Comprueba que el threshold seleccionado cumpla
    el recall mínimo establecido.
    """

    y_true = np.array([
        0,
        0,
        0,
        1,
        1,
        1,
        1,
    ])

    probabilities = np.array([
        0.10,
        0.20,
        0.30,
        0.40,
        0.60,
        0.70,
        0.90,
    ])

    selected, results = search_threshold(
        y_true,
        probabilities,
        min_threshold=0.20,
        max_threshold=0.60,
        step=0.01,
        min_recall=0.80,
    )

    assert selected["recall"] >= 0.80

    assert (
        0.20
        <= selected["threshold"]
        <= 0.60
    )

    assert not results.empty
def test_threshold_selection_fails_when_recall_requirement_is_impossible():
    """
    Comprueba que el pipeline falle de forma explícita
    cuando ningún threshold cumple el recall mínimo.
    """

    y_true = np.array([
        0,
        0,
        1,
        1,
    ])

    probabilities = np.array([
        0.10,
        0.20,
        0.10,
        0.20,
    ])

    with pytest.raises(
        ValueError,
        match="Ningún threshold"
    ):
        search_threshold(
            y_true,
            probabilities,
            min_threshold=0.50,
            max_threshold=0.90,
            step=0.10,
            min_recall=0.80,
        )