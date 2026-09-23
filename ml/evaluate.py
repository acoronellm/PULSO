
"""Métricas comunes; no utiliza test hasta la evaluación final aprobada."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score, brier_score_loss, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score,
)


def evaluate(model, X, y, threshold: float = 0.5) -> dict[str, float]:
    if not 0 < threshold < 1:
        raise ValueError("El umbral debe estar entre 0 y 1")
    classes = list(model.classes_)
    if 1 not in classes:
        raise ValueError("El modelo no tiene clase positiva 1")
    proba = model.predict_proba(X)[:, classes.index(1)]
    prediction = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    return {
        "accuracy": float(accuracy_score(y, prediction)),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else float("nan"),
        "f1": float(f1_score(y, prediction, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, proba)),
        "brier": float(brier_score_loss(y, proba)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }
