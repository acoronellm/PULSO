"""Pruebas del pipeline de entrenamiento con datos sintéticos."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from sklearn.model_selection import GridSearchCV

from ml.threshold import search_threshold
from ml.common import (
    FEATURES,
    load_dataset,
    make_pipeline,
    split_data,
)
from ml.evaluate import evaluate

from ml.calibration import (
    evaluate_probabilities,
    expected_calibration_error,
    make_calibrated_model,
)

from ml.select_threshold import run_threshold_selection

import mlflow

import ml.select_threshold as select_threshold_module

import ml.final_evaluate as final_evaluate_module

from ml.final_evaluate import (
    build_final_model,
    calculate_final_metrics,
    run_final_evaluation,
)

MODEL_TYPES = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "xgboost",
    "gradient_boosting",
]


def minimal_model_params(model_type):
    """Devuelve parámetros mínimos y rápidos para pruebas."""

    params = {
        "logistic_regression": {
            "max_iter": 500,
            "random_state": 42,
        },
        "decision_tree": {
            "max_depth": 5,
            "min_samples_leaf": 10,
            "random_state": 42,
        },
        "random_forest": {
            "n_estimators": 20,
            "random_state": 42,
            "n_jobs": 1,
        },
        "xgboost": {
            "n_estimators": 20,
            "max_depth": 3,
            "learning_rate": 0.1,
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "tree_method": "hist",
            "random_state": 42,
            "n_jobs": 1,
        },
        "gradient_boosting": {
            "n_estimators": 20,
            "learning_rate": 0.1,
            "max_depth": 3,
            "random_state": 42,
        },
    }

    return params[model_type]


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

        # Variable objetivo aproximadamente balanceada.
        # np.resize también funciona correctamente cuando n es impar.
        "cardio": np.resize([0, 1], n),

        # Variables presentes en el CSV depurado,
        # pero actualmente excluidas del entrenamiento.
        "cholesterol": 1,
        "gluc": 1,

        # Variables conservadas para trazabilidad.
        "age": 20000,
        "id": np.arange(n),
    })

    return df


def test_load_keeps_exclusions_out_of_x(tmp_path):
    """Comprueba que las variables excluidas no formen parte de X."""

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

    first_split = split_data(X, y)
    second_split = split_data(X, y)

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

    # Train y validation no deben cruzarse.
    assert not (indexes[0] & indexes[1])

    # Train y test no deben cruzarse.
    assert not (indexes[0] & indexes[2])

    # Validation y test no deben cruzarse.
    assert not (indexes[1] & indexes[2])

    # La división debe ser reproducible.
    assert all(
        first_split[i][0].index.equals(
            second_split[i][0].index
        )
        for i in range(3)
    )


@pytest.mark.parametrize(
    "kind,params",
    [
        (
            model_type,
            minimal_model_params(model_type),
        )
        for model_type in MODEL_TYPES
    ],
)
def test_models_fit_and_evaluate(kind, params):
    """Comprueba que todos los modelos puedan entrenar y evaluarse."""

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

    # Verificar que existan las métricas principales.
    assert set(metrics) >= {
        "accuracy",
        "precision",
        "recall",
        "specificity",
        "f1",
        "roc_auc",
        "brier",
    }

    # ROC-AUC debe estar entre 0 y 1.
    assert 0 <= metrics["roc_auc"] <= 1

    # Brier score debe estar entre 0 y 1.
    assert 0 <= metrics["brier"] <= 1


@pytest.mark.parametrize(
    "kind,model_params,param_grid",
    [
        (
            "logistic_regression",
            minimal_model_params("logistic_regression"),
            {
                "model__C": [0.1, 1.0],
            },
        ),
        (
            "decision_tree",
            minimal_model_params("decision_tree"),
            {
                "model__max_depth": [3, 5],
            },
        ),
        (
            "random_forest",
            minimal_model_params("random_forest"),
            {
                "model__n_estimators": [10, 20],
            },
        ),
        (
            "xgboost",
            minimal_model_params("xgboost"),
            {
                "model__max_depth": [2, 3],
            },
        ),
        (
            "gradient_boosting",
            minimal_model_params("gradient_boosting"),
            {
                "model__n_estimators": [10, 20],
            },
        ),
    ],
)
def test_models_support_gridsearch(
    kind,
    model_params,
    param_grid,
):
    """
    Comprueba que todos los modelos soportados puedan
    utilizarse correctamente dentro de GridSearchCV.

    Se usan grids mínimos para mantener rápida la suite de tests.
    """

    df = synthetic_data()

    X = df[FEATURES]
    y = df["cardio"]

    (
        X_train,
        y_train,
    ), _, _ = split_data(
        X,
        y,
    )

    pipeline = make_pipeline({
        "model_type": kind,
        "model_params": model_params,
    })

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
    assert 0 <= grid.best_score_ <= 1
    assert isinstance(grid.best_params_, dict)
    assert len(grid.best_params_) > 0


@pytest.mark.parametrize("model_type", MODEL_TYPES)
def test_search_space_config_exists_and_is_valid(model_type):
    """
    Comprueba que cada modelo tenga un search space válido
    y con la estructura mínima esperada por ml.tune.

    GridSearchCV permite que param_grid sea:
    - un diccionario;
    - una lista de diccionarios.
    """

    search_path = (
        Path(__file__).resolve().parents[1]
        / "ml"
        / "configs"
        / "search_spaces"
        / f"{model_type}.yaml"
    )

    assert search_path.exists(), (
        f"No existe search space para {model_type}: "
        f"{search_path}"
    )

    config = yaml.safe_load(
        search_path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(config, dict)

    assert config["model_type"] == model_type

    assert "param_grid" in config

    param_grid = config["param_grid"]

    # GridSearchCV acepta:
    # dict
    # o list[dict]
    assert isinstance(
        param_grid,
        (dict, list),
    )

    if isinstance(param_grid, dict):

        assert len(param_grid) > 0

    else:

        assert len(param_grid) > 0

        assert all(
            isinstance(grid, dict)
            and len(grid) > 0
            for grid in param_grid
        )

    assert (
        config.get(
            "scoring",
            "roc_auc",
        )
        == "roc_auc"
    )

    assert config.get("cv", 5) >= 2

@pytest.mark.parametrize("model_type", MODEL_TYPES)
def test_search_space_parameters_exist_in_pipeline(model_type):
    """
    Comprueba que todas las claves definidas en param_grid
    correspondan a parámetros reales del pipeline.

    Soporta tanto:
    - dict;
    - list[dict].

    Esto es necesario porque Logistic Regression utiliza
    múltiples grids para representar combinaciones compatibles
    entre hiperparámetros.
    """

    search_path = (
        Path(__file__).resolve().parents[1]
        / "ml"
        / "configs"
        / "search_spaces"
        / f"{model_type}.yaml"
    )

    config = yaml.safe_load(
        search_path.read_text(
            encoding="utf-8"
        )
    )

    pipeline = make_pipeline({
        "model_type": model_type,
        "model_params": minimal_model_params(
            model_type
        ),
    })

    valid_params = set(
        pipeline
        .get_params()
        .keys()
    )

    param_grid = config["param_grid"]

    if isinstance(param_grid, dict):

        grid_list = [
            param_grid
        ]

    else:

        grid_list = param_grid

    invalid_params = []

    for grid in grid_list:

        for param_name in grid:

            if param_name not in valid_params:

                invalid_params.append(
                    param_name
                )

    assert not invalid_params, (
        f"Parámetros inválidos en el search space "
        f"de {model_type}: "
        f"{invalid_params}"
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
    assert 0.20 <= selected["threshold"] <= 0.60
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
        match="Ningún threshold",
    ):
        search_threshold(
            y_true,
            probabilities,
            min_threshold=0.50,
            max_threshold=0.90,
            step=0.10,
            min_recall=0.80,
        )
def test_expected_calibration_error_is_valid():
    """
    Comprueba que ECE produzca un valor válido
    entre 0 y 1.
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
        0.80,
        0.90,
    ])

    ece = expected_calibration_error(
        y_true,
        probabilities,
        n_bins=4,
    )

    assert 0 <= ece <= 1
def test_evaluate_probabilities_returns_expected_metrics():
    """
    Comprueba que la evaluación probabilística
    devuelva las métricas necesarias para comparar
    calibraciones.
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
        0.80,
        0.90,
    ])

    metrics = evaluate_probabilities(
        y_true,
        probabilities,
        n_bins=4,
    )

    assert set(metrics) == {
        "brier",
        "log_loss",
        "ece",
        "roc_auc",
    }

    assert 0 <= metrics["brier"] <= 1
    assert metrics["log_loss"] >= 0
    assert 0 <= metrics["ece"] <= 1
    assert 0 <= metrics["roc_auc"] <= 1
@pytest.mark.parametrize(
    "model_type",
    MODEL_TYPES,
)
@pytest.mark.parametrize(
    "method",
    [
        "sigmoid",
        "isotonic",
    ],
)
def test_models_support_calibration(
    model_type,
    method,
):
    """
    Comprueba que todos los modelos soportados
    puedan calibrarse con Sigmoid e Isotonic.
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
    ), _ = split_data(
        X,
        y,
    )

    pipeline = make_pipeline({
        "model_type": model_type,
        "model_params": minimal_model_params(
            model_type
        ),
    })

    calibrated_model = make_calibrated_model(
        pipeline,
        method=method,
        cv=2,
    )

    calibrated_model.fit(
        X_train,
        y_train,
    )

    probabilities = (
        calibrated_model
        .predict_proba(X_val)[:, 1]
    )

    assert len(probabilities) == len(y_val)

    assert np.all(
        probabilities >= 0
    )

    assert np.all(
        probabilities <= 1
    )

    metrics = evaluate_probabilities(
        y_val,
        probabilities,
    )

    assert 0 <= metrics["brier"] <= 1
    assert metrics["log_loss"] >= 0
    assert 0 <= metrics["ece"] <= 1
    assert 0 <= metrics["roc_auc"] <= 1

def disable_mlflow(
    monkeypatch,
    tmp_path,
):
    """
    Deshabilita los efectos secundarios de MLflow
    y redirige los artefactos al directorio temporal
    durante los tests.
    """

    # Evitar que los CSV de threshold se escriban
    # dentro del repositorio real.
    monkeypatch.setattr(
        select_threshold_module,
        "ROOT",
        tmp_path,
    )

    monkeypatch.setattr(
        mlflow,
        "set_tracking_uri",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        mlflow,
        "set_experiment",
        lambda *args, **kwargs: None,
    )

    class DummyRun:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

    monkeypatch.setattr(
        mlflow,
        "start_run",
        lambda *args, **kwargs: DummyRun(),
    )

    monkeypatch.setattr(
        mlflow,
        "log_param",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        mlflow,
        "log_metric",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        mlflow,
        "log_artifact",
        lambda *args, **kwargs: None,
    )
@pytest.mark.parametrize(
    "model_type",
    MODEL_TYPES,
)
def test_threshold_selection_with_no_calibration(
    model_type,
    tmp_path,
    monkeypatch,
):
    """
    Comprueba que la selección de threshold
    funcione para todos los modelos cuando
    no se utiliza calibración.
    """

    disable_mlflow(
        monkeypatch,
        tmp_path,
    )

    data_path = (
        tmp_path
        / "clean.csv"
    )

    config_path = (
        tmp_path
        / f"{model_type}_candidate.yaml"
    )

    synthetic_data(
        n=400
    ).to_csv(
        data_path,
        index=False,
    )

    config = {
        "model_type": model_type,
        "model_params": (
            minimal_model_params(
                model_type
            )
        ),
        "calibration": {
            "method": "none",
        },
        "threshold": 0.5,
    }

    config_path.write_text(
        yaml.safe_dump(
            config
        ),
        encoding="utf-8",
    )

    selected, results = (
        run_threshold_selection(
            config_path,
            data_path,
        )
    )

    assert not results.empty

    assert (
        selected["recall"]
        >= 0.80
    )

    assert (
        0.20
        <= selected["threshold"]
        <= 0.60
    )
@pytest.mark.parametrize(
    "model_type",
    MODEL_TYPES,
)
def test_threshold_selection_with_sigmoid_calibration(
    model_type,
    tmp_path,
    monkeypatch,
):
    """
    Comprueba que la selección de threshold
    funcione para todos los modelos cuando
    utilizan calibración Sigmoid.
    """

    disable_mlflow(
        monkeypatch,
        tmp_path,
    )

    data_path = (
        tmp_path
        / "clean.csv"
    )

    config_path = (
        tmp_path
        / f"{model_type}_candidate.yaml"
    )

    synthetic_data(
        n=400
    ).to_csv(
        data_path,
        index=False,
    )

    config = {
        "model_type": model_type,
        "model_params": (
            minimal_model_params(
                model_type
            )
        ),
        "calibration": {
            "method": "sigmoid",
            "cv": 2,
        },
        "threshold": 0.5,
    }

    config_path.write_text(
        yaml.safe_dump(
            config
        ),
        encoding="utf-8",
    )

    selected, results = (
        run_threshold_selection(
            config_path,
            data_path,
        )
    )

    assert not results.empty

    assert (
        selected["recall"]
        >= 0.80
    )

    assert (
        0.20
        <= selected["threshold"]
        <= 0.60
    )
@pytest.mark.parametrize(
    "model_type",
    MODEL_TYPES,
)
def test_threshold_selection_with_isotonic_calibration(
    model_type,
    tmp_path,
    monkeypatch,
):
    """
    Comprueba que la selección de threshold
    funcione para todos los modelos cuando
    utilizan calibración Isotonic.
    """

    disable_mlflow(
        monkeypatch,
        tmp_path,
    )

    data_path = (
        tmp_path
        / "clean.csv"
    )

    config_path = (
        tmp_path
        / f"{model_type}_candidate.yaml"
    )

    synthetic_data(
        n=400
    ).to_csv(
        data_path,
        index=False,
    )

    config = {
        "model_type": model_type,
        "model_params": (
            minimal_model_params(
                model_type
            )
        ),
        "calibration": {
            "method": "isotonic",
            "cv": 2,
        },
        "threshold": 0.5,
    }

    config_path.write_text(
        yaml.safe_dump(
            config
        ),
        encoding="utf-8",
    )

    selected, results = (
        run_threshold_selection(
            config_path,
            data_path,
        )
    )

    assert not results.empty

    assert (
        selected["recall"]
        >= 0.80
    )

    assert (
        0.20
        <= selected["threshold"]
        <= 0.60
    )
def disable_final_evaluation_side_effects(
    monkeypatch,
    tmp_path,
):
    """
    Redirige artefactos y deshabilita MLflow
    durante los tests de evaluación final.
    """

    monkeypatch.setattr(
        final_evaluate_module,
        "ROOT",
        tmp_path,
    )

    monkeypatch.setattr(
        mlflow,
        "set_tracking_uri",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        mlflow,
        "set_experiment",
        lambda *args, **kwargs: None,
    )

    class DummyRun:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

    monkeypatch.setattr(
        mlflow,
        "start_run",
        lambda *args, **kwargs: DummyRun(),
    )

    monkeypatch.setattr(
        mlflow,
        "log_param",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        mlflow,
        "log_metric",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        mlflow,
        "log_artifact",
        lambda *args, **kwargs: None,
    )
def test_calculate_final_metrics_returns_expected_metrics():
    """
    Comprueba que la evaluación final produzca
    todas las métricas requeridas.
    """

    y_true = np.array([
        0,
        0,
        0,
        1,
        1,
        1,
    ])

    probabilities = np.array([
        0.10,
        0.20,
        0.40,
        0.55,
        0.75,
        0.90,
    ])

    threshold = 0.38

    predictions = (
        probabilities >= threshold
    ).astype(int)

    metrics = calculate_final_metrics(
        y_true,
        probabilities,
        predictions,
    )

    assert set(metrics) == {
        "accuracy",
        "precision",
        "recall",
        "specificity",
        "f1",
        "roc_auc",
        "brier",
        "log_loss",
        "ece",
        "tn",
        "fp",
        "fn",
        "tp",
    }

    assert 0 <= metrics["accuracy"] <= 1
    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["specificity"] <= 1
    assert 0 <= metrics["f1"] <= 1
    assert 0 <= metrics["roc_auc"] <= 1
    assert 0 <= metrics["brier"] <= 1
    assert metrics["log_loss"] >= 0
    assert 0 <= metrics["ece"] <= 1

    assert (
        metrics["tn"]
        + metrics["fp"]
        + metrics["fn"]
        + metrics["tp"]
        == len(y_true)
    )
def test_build_final_model_without_calibration():
    """
    Comprueba que el candidato final pueda
    construirse correctamente cuando
    calibration.method = none.
    """

    config = {
        "model_type": "xgboost",
        "model_params": {
            "n_estimators": 10,
            "max_depth": 3,
            "learning_rate": 0.1,
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "tree_method": "hist",
            "random_state": 42,
            "n_jobs": 1,
        },
        "calibration": {
            "method": "none",
        },
        "threshold": 0.38,
    }

    model = build_final_model(
        config
    )

    df = synthetic_data(
        n=200
    )

    X = df[FEATURES]
    y = df["cardio"]

    model.fit(
        X,
        y,
    )

    probabilities = (
        model
        .predict_proba(X)[:, 1]
    )

    assert len(probabilities) == len(y)

    assert np.all(
        probabilities >= 0
    )

    assert np.all(
        probabilities <= 1
    )
def test_final_evaluation_pipeline(
    tmp_path,
    monkeypatch,
):
    """
    Comprueba el flujo completo de evaluación final
    utilizando datos sintéticos.

    No utiliza el dataset real de PULSO.
    """

    disable_final_evaluation_side_effects(
        monkeypatch,
        tmp_path,
    )

    data_path = (
        tmp_path
        / "clean.csv"
    )

    config_path = (
        tmp_path
        / "final_model.yaml"
    )

    synthetic_data(
        n=400
    ).to_csv(
        data_path,
        index=False,
    )

    config = {
        "model_type": "xgboost",
        "model_params": {
            "n_estimators": 10,
            "max_depth": 3,
            "learning_rate": 0.1,
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "tree_method": "hist",
            "random_state": 42,
            "n_jobs": 1,
        },
        "calibration": {
            "method": "none",
        },
        "threshold": 0.38,
    }

    config_path.write_text(
        yaml.safe_dump(
            config
        ),
        encoding="utf-8",
    )

    metrics, model = (
        run_final_evaluation(
            config_path,
            data_path,
        )
    )

    # -----------------------------
    # Verificar métricas
    # -----------------------------

    assert set(metrics) == {
        "accuracy",
        "precision",
        "recall",
        "specificity",
        "f1",
        "roc_auc",
        "brier",
        "log_loss",
        "ece",
        "tn",
        "fp",
        "fn",
        "tp",
    }

    # -----------------------------
    # Verificar que Test tenga
    # exactamente 15 % de 400 = 60
    # -----------------------------

    assert (
        metrics["tn"]
        + metrics["fp"]
        + metrics["fn"]
        + metrics["tp"]
        == 60
    )

    # -----------------------------
    # Verificar artefactos
    # -----------------------------

    output_dir = (
        tmp_path
        / "artifacts"
        / "final"
    )

    assert (
        output_dir
        / "test_metrics.csv"
    ).exists()

    assert (
        output_dir
        / "confusion_matrix.png"
    ).exists()

    assert (
        output_dir
        / "roc_curve.png"
    ).exists()

    assert (
        output_dir
        / "precision_recall_curve.png"
    ).exists()

    assert (
        output_dir
        / "calibration_curve.png"
    ).exists()

    assert (
        output_dir
        / "model"
        / "pulso_xgboost.joblib"
    ).exists()

    assert model is not None
def test_build_final_model_rejects_invalid_calibration():
    """
    Comprueba que una calibración no soportada
    produzca un error explícito.
    """

    config = {
        "model_type": "logistic_regression",
        "model_params": {
            "max_iter": 500,
            "random_state": 42,
        },
        "calibration": {
            "method": "invalid_method",
        },
        "threshold": 0.38,
    }

    with pytest.raises(
        ValueError,
        match="Método de calibración no soportado",
    ):
        build_final_model(
            config
        )