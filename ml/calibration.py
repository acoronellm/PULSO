"""Utilidades para evaluación y calibración de probabilidades."""

from __future__ import annotations

import numpy as np

from sklearn.base import clone
from sklearn.calibration import (
    CalibratedClassifierCV,
    calibration_curve,
)
from sklearn.metrics import (
    brier_score_loss,
    log_loss,
    roc_auc_score,
)


def expected_calibration_error(
    y_true,
    probabilities,
    n_bins: int = 10,
) -> float:
    """
    Calcula Expected Calibration Error (ECE).

    Divide las probabilidades en bins y calcula la
    diferencia ponderada entre confianza media y
    frecuencia observada.
    """

    y_true = np.asarray(y_true)
    probabilities = np.asarray(probabilities)

    bins = np.linspace(
        0.0,
        1.0,
        n_bins + 1,
    )

    bin_ids = np.digitize(
        probabilities,
        bins[1:-1],
        right=True,
    )

    ece = 0.0

    for bin_id in range(n_bins):

        mask = bin_ids == bin_id

        if not np.any(mask):
            continue

        bin_probability = (
            probabilities[mask].mean()
        )

        bin_frequency = (
            y_true[mask].mean()
        )

        bin_weight = (
            mask.sum()
            / len(y_true)
        )

        ece += (
            bin_weight
            * abs(
                bin_probability
                - bin_frequency
            )
        )

    return float(ece)


def evaluate_probabilities(
    y_true,
    probabilities,
    n_bins: int = 10,
) -> dict[str, float]:
    """
    Evalúa la calidad probabilística de un modelo.
    """

    return {
        "brier": float(
            brier_score_loss(
                y_true,
                probabilities,
            )
        ),
        "log_loss": float(
            log_loss(
                y_true,
                probabilities,
            )
        ),
        "ece": expected_calibration_error(
            y_true,
            probabilities,
            n_bins=n_bins,
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),
    }


def make_calibrated_model(
    pipeline,
    method: str,
    cv: int = 5,
):
    """
    Construye una versión calibrada del pipeline.

    method:
        - sigmoid
        - isotonic
    """

    if method not in {
        "sigmoid",
        "isotonic",
    }:
        raise ValueError(
            "Método de calibración no soportado: "
            f"{method}"
        )

    return CalibratedClassifierCV(
        estimator=clone(pipeline),
        method=method,
        cv=cv,
        ensemble=False,
        n_jobs=-1,
    )