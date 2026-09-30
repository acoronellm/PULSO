"""Selección reproducible del threshold usando Validation."""
from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


def search_threshold(
    y_true,
    probabilities,
    min_threshold: float = 0.20,
    max_threshold: float = 0.60,
    step: float = 0.01,
    min_recall: float = 0.80,
):

    thresholds = np.arange(
        min_threshold,
        max_threshold + step / 2,
        step
    )

    rows = []

    for threshold in thresholds:

        predictions = (
            probabilities >= threshold
        ).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y_true,
            predictions,
            labels=[0, 1]
        ).ravel()

        specificity = (
            tn / (tn + fp)
            if tn + fp
            else 0.0
        )

        rows.append({
            "threshold": float(threshold),
            "accuracy": accuracy_score(
                y_true,
                predictions
            ),
            "precision": precision_score(
                y_true,
                predictions,
                zero_division=0
            ),
            "recall": recall_score(
                y_true,
                predictions,
                zero_division=0
            ),
            "specificity": specificity,
            "f1": f1_score(
                y_true,
                predictions,
                zero_division=0
            ),
        })

    results = pd.DataFrame(rows)

    eligible = results[
        results["recall"] >= min_recall
    ].copy()

    if eligible.empty:
        raise ValueError(
            f"Ningún threshold alcanzó recall >= {min_recall}"
        )

    eligible = eligible.sort_values(
        by=[
            "precision",
            "f1"
        ],
        ascending=[
            False,
            False
        ]
    )

    selected = eligible.iloc[0]

    return selected, results