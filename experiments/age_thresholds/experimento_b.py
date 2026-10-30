"""Experimento B (exploratorio): umbrales globales y por edad para PULSO.

Ejecutar desde la raíz del repositorio:
    python -m experiments.age_thresholds.experimento_b

NO lee ni evalúa Test. NO modifica el modelo oficial PULSO v1.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import (accuracy_score, brier_score_loss, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split

from ml.common import load_dataset, make_pipeline, split_data

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "cardio_clean_v1.csv"
CONFIG = ROOT / "models" / "pulso" / "v1" / "final_model.yaml"
OUTPUT = ROOT / "experiments" / "age_thresholds" / "results"
SEED = 42
OFFICIAL_THRESHOLD = 0.38
GRID = np.round(np.arange(0.05, 0.951, 0.01), 2)
GROUPS = ["menor_50", "50_59", "60_64"]


def age_group(age: pd.Series) -> pd.Series:
    if age.isna().any():
        raise ValueError("Se encontraron edades faltantes")
    return pd.Series(
        np.select([age < 50, (age >= 50) & (age < 60), age >= 60],
                  GROUPS, default="invalid"), index=age.index, name="grupo_edad"
    )


def choose_threshold(y_true: np.ndarray, probabilities: np.ndarray,
                     min_recall: float = 0.80) -> dict:
    """Selección SOLO en calibración; maximiza precisión con recall >= mínimo.

    Si no se alcanza el mínimo, elige el máximo recall posible y marca incumplimiento.
    """
    candidates = []
    for threshold in GRID:
        pred = (probabilities >= threshold).astype(int)
        candidates.append({
            "threshold": float(threshold),
            "recall": float(recall_score(y_true, pred, zero_division=0)),
            "precision": float(precision_score(y_true, pred, zero_division=0)),
            "f1": float(f1_score(y_true, pred, zero_division=0)),
        })
    eligible = [r for r in candidates if r["recall"] >= min_recall]
    if eligible:
        chosen = max(eligible, key=lambda x: (x["precision"], x["f1"], x["threshold"]))
        chosen["meets_recall_calibration"] = True
    else:
        chosen = max(candidates, key=lambda x: (x["recall"], x["precision"]))
        chosen["meets_recall_calibration"] = False
    return chosen


def metrics(y_true: np.ndarray, p: np.ndarray, predicted: np.ndarray) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, predicted, labels=[0, 1]).ravel()
    return {
        "n": int(len(y_true)), "positives": int(np.sum(y_true == 1)),
        "negatives": int(np.sum(y_true == 0)),
        "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn),
        "recall": float(recall_score(y_true, predicted, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else None,
        "precision": float(precision_score(y_true, predicted, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, predicted)),
        "f1": float(f1_score(y_true, predicted, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, p)) if len(np.unique(y_true)) == 2 else None,
        "brier": float(brier_score_loss(y_true, p)),
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    X, y = load_dataset(DATA)
    (X_train, y_train), (X_val, y_val), _ = split_data(X, y)

    # Un único modelo global para las tres políticas de decisión.
    model = make_pipeline(config)
    print("Entrenando XGBoost global exclusivamente con Train...")
    model.fit(X_train, y_train)
    p_val = model.predict_proba(X_val)[:, list(model.classes_).index(1)]
    groups = age_group(X_val["age_years"])

    # Dos mitades de Validation: una para elegir umbrales y otra para evaluarlos.
    # Estratificamos simultáneamente por edad y etiqueta, sin introducir Test.
    stratify = groups.astype(str) + "_" + y_val.astype(str)
    cal_idx, eval_idx = train_test_split(
        np.arange(len(X_val)), test_size=0.50, random_state=SEED,
        stratify=stratify,
    )
    truth = np.asarray(y_val)
    gp = groups.to_numpy()
    global_selected = choose_threshold(truth[cal_idx], p_val[cal_idx])
    age_selected = {}
    for group in GROUPS:
        mask = cal_idx[gp[cal_idx] == group]
        age_selected[group] = choose_threshold(truth[mask], p_val[mask])

    eval_y = truth[eval_idx]
    eval_p = p_val[eval_idx]
    eval_g = gp[eval_idx]
    policies = {
        "v1_threshold_0_38": np.full(len(eval_idx), OFFICIAL_THRESHOLD),
        "global_optimized": np.full(len(eval_idx), global_selected["threshold"]),
        "age_specific": np.array([age_selected[g]["threshold"] for g in eval_g]),
    }

    rows = []
    for policy_name, thresholds in policies.items():
        preds = (eval_p >= thresholds).astype(int)
        rows.append({"policy": policy_name, "grupo_edad": "GLOBAL",
                     **metrics(eval_y, eval_p, preds)})
        for group in GROUPS:
            m = eval_g == group
            rows.append({"policy": policy_name, "grupo_edad": group,
                         **metrics(eval_y[m], eval_p[m], preds[m])})

    pd.DataFrame(rows).to_csv(OUTPUT / "metricas_validacion_evaluacion.csv", index=False)
    selections = ([{"scope": "GLOBAL", **global_selected}] +
                  [{"scope": g, **age_selected[g]} for g in GROUPS])
    pd.DataFrame(selections).to_csv(OUTPUT / "umbrales_seleccionados.csv", index=False)
    record = {
        "purpose": "Experimento B exploratorio; no inferencia clínica ni evaluación independiente final",
        "dataset": str(DATA.relative_to(ROOT)),
        "config": str(CONFIG.relative_to(ROOT)),
        "seed": SEED,
        "train_rows": len(X_train),
        "validation_calibration_rows": len(cal_idx),
        "validation_evaluation_rows": len(eval_idx),
        "test_used": False,
        "threshold_selection": "Máxima precision sujeta a recall >= 0.80 sobre mitad de Validation",
        "groups": {"menor_50": "age<50", "50_59": "50<=age<60", "60_64": "age>=60 (en dataset hasta ~64.9)"},
        "caveat": "Edad y grupos ya explorados en Test previamente: resultados solo exploratorios; exigir nueva cohorte externa para conclusión confirmatoria.",
    }
    (OUTPUT / "protocolo.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nUmbrales elegidos en Validation-calibration:")
    print(pd.DataFrame(selections).to_string(index=False))
    print("\nMétricas en Validation-evaluation (globales):")
    print(pd.DataFrame(rows).query("grupo_edad == 'GLOBAL'")[
        ["policy", "n", "recall", "specificity", "precision", "f1", "fp", "fn"]
    ].to_string(index=False))
    print(f"\nArchivos: {OUTPUT}")
    print("Test NO utilizado. Modelo oficial NO modificado.")


if __name__ == "__main__":
    main()
