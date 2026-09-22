
"""Contrato de datos, particiones y pipelines compartidos por los baselines."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

TARGET = "cardio"
FEATURES = [
    "gender", "height", "weight", "ap_hi", "ap_lo", "smoke", "alco",
    "active", "age_years", "bmi",
]
CONTINUOUS = ["height", "weight", "ap_hi", "ap_lo", "age_years", "bmi"]
BINARY = ["smoke", "alco", "active"]
CATEGORICAL = ["gender"]
EXCLUDED = ["id", "age", "cholesterol", "gluc"]
RANDOM_STATE = 42


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_dataset(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Lee SOLO el CSV ya depurado: no vuelve a aplicar prepare.py."""
    df = pd.read_csv(path)
    expected = FEATURES + [TARGET]
    missing = sorted(set(expected) - set(df.columns))
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")
    if len(df) == 0:
        raise ValueError("El dataset está vacío")
    if df[expected].isna().any().any():
        raise ValueError("Existen valores faltantes en las columnas utilizadas")
    if not set(df[TARGET].unique()) == {0, 1}:
        raise ValueError("cardio debe contener las clases 0 y 1")
    if not all(pd.api.types.is_numeric_dtype(df[c]) for c in expected):
        raise ValueError("Las características y cardio deben ser numéricas")
    if not np.isfinite(df[expected].to_numpy(dtype=float)).all():
        raise ValueError("Existen valores infinitos o no numéricos")
    return df[FEATURES].copy(), df[TARGET].copy()


def split_data(X: pd.DataFrame, y: pd.Series):
    """Reproduce EXACTAMENTE las dos divisiones de los notebooks (70/15/15)."""
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_STATE, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=RANDOM_STATE,
        stratify=y_temp,
    )
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


def make_pipeline(config: dict) -> Pipeline:
    kind = config["model_type"]
    if kind == "logistic_regression":
        continuous_transform = StandardScaler()
        model = LogisticRegression(**config["model_params"])
    elif kind == "decision_tree":
        continuous_transform = "passthrough"
        model = DecisionTreeClassifier(**config["model_params"])
    else:
        raise ValueError(f"Algoritmo desconocido: {kind}")
    preprocessor = ColumnTransformer(transformers=[
        ("continuous", continuous_transform, CONTINUOUS),
        ("gender", OneHotEncoder(drop=None, handle_unknown="ignore"), CATEGORICAL),
        ("binary", "passthrough", BINARY),
    ])
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])
