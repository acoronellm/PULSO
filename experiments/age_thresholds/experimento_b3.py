"""PULSO — Experimento B3: umbrales por edad con balance recall/especificidad.

Desde raíz de PULSO:
    python -m experiments.age_thresholds.experimento_b3

Entrena UN XGBoost con Train; elige umbrales en media Validation y
los evalúa en la otra media. Nunca utiliza Test ni modifica PULSO v1.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import (
    accuracy_score, brier_score_loss, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split

from ml.common import load_dataset, make_pipeline, split_data

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "cardio_clean_v1.csv"
CONFIG = ROOT / "models" / "pulso" / "v1" / "final_model.yaml"
OUT = ROOT / "experiments" / "age_thresholds" / "results" / "b3"
SEED = 42
OFFICIAL = 0.38
GRID = np.round(np.arange(0.05, 0.951, 0.01), 2)
GROUPS = ("menor_50", "50_59", "60_64")
# Umbrales exploratorios observados en el experimento B previo; no se recalculan con Test.
B_PREVIOUS = {"menor_50": 0.23, "50_59": 0.38, "60_64": 0.55}
OBJECTIVES = ("balanced_accuracy", "weighted_60_40", "minimax")


def age_group(age: pd.Series) -> np.ndarray:
    if age.isna().any():
        raise ValueError("Hay edades faltantes")
    return np.select([age < 50, (age >= 50) & (age < 60), age >= 60],
                     GROUPS, default="invalid")


def score_table(y: np.ndarray, p: np.ndarray) -> pd.DataFrame:
    """Evalúa ambas tasas por cada candidato; no optimiza sobre evaluación."""
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    if len(y) == 0 or set(np.unique(y)) != {0, 1}:
        raise ValueError("Cada muestra de selección debe contener ambas clases")
    if not np.isfinite(p).all():
        raise ValueError("Probabilidades no finitas")
    rows = []
    for t in GRID:
        z = p >= t
        tp = int(np.sum(z & (y == 1)))
        tn = int(np.sum(~z & (y == 0)))
        fp = int(np.sum(z & (y == 0)))
        fn = int(np.sum(~z & (y == 1)))
        rec = tp / (tp + fn)
        spec = tn / (tn + fp)
        rows.append({"threshold": float(t), "recall": rec, "specificity": spec,
                     "balanced_accuracy": (rec + spec) / 2,
                     "weighted_60_40": .6 * rec + .4 * spec,
                     "minimax": min(rec, spec), "tp": tp, "tn": tn, "fp": fp, "fn": fn})
    return pd.DataFrame(rows)


def choose(table: pd.DataFrame, objective: str) -> dict:
    """Desempate por BA, luego cercanía a 0.38, luego menor umbral."""
    if objective not in OBJECTIVES:
        raise ValueError(objective)
    ordered = table.assign(distance=(table.threshold - OFFICIAL).abs()).sort_values(
        by=[objective, "balanced_accuracy", "distance", "threshold"],
        ascending=[False, False, True, True], kind="mergesort"
    )
    row = ordered.iloc[0]
    return {"threshold": float(row.threshold),
            "selection_score": float(row[objective]),
            "recall_selection": float(row.recall),
            "specificity_selection": float(row.specificity),
            "ba_selection": float(row.balanced_accuracy)}


def metrics(y: np.ndarray, p: np.ndarray, z: np.ndarray) -> dict:
    tn, fp, fn, tp = (int(v) for v in confusion_matrix(y, z, labels=[0, 1]).ravel())
    return {
        "n": len(y), "positives": int(np.sum(y == 1)), "negatives": int(np.sum(y == 0)),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "recall": recall_score(y, z, zero_division=0),
        "specificity": tn / (tn + fp) if tn + fp else np.nan,
        "precision": precision_score(y, z, zero_division=0),
        "f1": f1_score(y, z, zero_division=0),
        "accuracy": accuracy_score(y, z),
        "balanced_accuracy": .5 * (tp / (tp + fn) + tn / (tn + fp)) if (tp + fn) and (tn + fp) else np.nan,
        "roc_auc": roc_auc_score(y, p) if len(np.unique(y)) == 2 else np.nan,
        "brier": brier_score_loss(y, p),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    X, y = load_dataset(DATA)
    (X_train, y_train), (X_val, y_val), _ = split_data(X, y)
    model = make_pipeline(config)
    print("Entrenando un XGBoost global solo con Train...")
    model.fit(X_train, y_train)
    classes = list(model.classes_)
    p_val = model.predict_proba(X_val)[:, classes.index(1)]
    truth = np.asarray(y_val, dtype=int)
    gp = age_group(X_val["age_years"])
    stratify = pd.Series(gp, index=X_val.index).astype(str) + "_" + y_val.astype(str)
    cal_idx, ev_idx = train_test_split(np.arange(len(X_val)), test_size=.5,
                                      random_state=SEED, stratify=stratify)

    selections = []
    curve_rows = []
    selected = {}
    scopes = {"GLOBAL": cal_idx}
    scopes.update({g: cal_idx[gp[cal_idx] == g] for g in GROUPS})
    for group, indices in scopes.items():
        curve = score_table(truth[indices], p_val[indices])
        curve.insert(0, "grupo_edad", group)
        curve_rows.append(curve)
        for objective in OBJECTIVES:
            chosen = choose(curve, objective)
            selected[(objective, group)] = chosen["threshold"]
            selections.append({"objetivo": objective, "grupo_edad": group,
                               "n_seleccion": len(indices), **chosen})

    yy, pp, gg = truth[ev_idx], p_val[ev_idx], gp[ev_idx]
    policy_thresholds = {
        "referencia_0_38": np.full(len(ev_idx), OFFICIAL),
        "B_previo_recall80": np.array([B_PREVIOUS[g] for g in gg], dtype=float),
    }
    for obj in OBJECTIVES:
        policy_thresholds[f"B3_{obj}_global"] = np.full(len(ev_idx), selected[(obj, "GLOBAL")])
        policy_thresholds[f"B3_{obj}_edad"] = np.array([selected[(obj, g)] for g in gg])

    rows = []
    for policy, ts in policy_thresholds.items():
        zz = (pp >= ts).astype(int)
        for group in ("GLOBAL", *GROUPS):
            mask = np.ones(len(ev_idx), dtype=bool) if group == "GLOBAL" else gg == group
            rows.append({"politica": policy, "grupo_edad": group,
                         **metrics(yy[mask], pp[mask], zz[mask])})

    # Porciones que pueden cambiar decisión a la misma probabilidad si se cambia de tramo.
    boundaries = []
    ages = X_val["age_years"].to_numpy()[ev_idx]
    for obj in OBJECTIVES:
        for age_cut, g_left, g_right in ((50, "menor_50", "50_59"), (60, "50_59", "60_64")):
            t_left, t_right = selected[(obj, g_left)], selected[(obj, g_right)]
            for window in (.5, 1.0):
                mask = np.abs(ages - age_cut) < window
                flips = int(np.sum((pp[mask] >= t_left) != (pp[mask] >= t_right)))
                boundaries.append({"objetivo": obj, "corte_edad": age_cut,
                                   "ventana_anios": window, "n": int(mask.sum()),
                                   "umbral_izq": t_left, "umbral_der": t_right,
                                   "cambios_potenciales": flips,
                                   "fraccion_potencial": flips / int(mask.sum()) if mask.sum() else np.nan})

    pd.concat(curve_rows, ignore_index=True).to_csv(OUT / "b3_curvas_seleccion.csv", index=False)
    pd.DataFrame(selections).to_csv(OUT / "b3_umbrales_seleccionados.csv", index=False)
    pd.DataFrame(rows).to_csv(OUT / "b3_metricas_evaluacion.csv", index=False)
    pd.DataFrame(boundaries).to_csv(OUT / "b3_cortes_edad.csv", index=False)
    record = {
        "experiment": "B3", "dataset": str(DATA.relative_to(ROOT)),
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "config": str(CONFIG.relative_to(ROOT)), "random_seed": SEED,
        "train_rows": len(X_train), "validation_rows": len(X_val),
        "selection_rows": len(cal_idx), "evaluation_rows": len(ev_idx),
        "test_used": False, "model_retrained_on_train": True,
        "groups": {"menor_50": "edad < 50", "50_59": "50 <= edad < 60", "60_64": "edad >= 60"},
        "grid": "0.05 to 0.95 inclusive, step 0.01",
        "objectives": {
            "balanced_accuracy": "(recall + specificity)/2",
            "weighted_60_40": "0.6*recall + 0.4*specificity; exploratory, not medically endorsed",
            "minimax": "min(recall, specificity)"
        },
        "tie_break": "BA descending, distance to 0.38 ascending, threshold ascending",
        "caveats": [
            "Only one split of Validation is used; exploratory estimate, not external validation.",
            "Group boundaries were informed partly by earlier Test analysis.",
            "Selection scores are not evaluation metrics; no minimum recall guarantee.",
            "Boundary comparison keeps probability fixed; actual predicted probability depends on age.",
            "Repeated comparison of approaches on the same evaluation split can bias a post-hoc winner choice."
        ],
    }
    (OUT / "b3_protocolo.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nUmbrales seleccionados:\n", pd.DataFrame(selections)[
        ["objetivo", "grupo_edad", "threshold", "recall_selection", "specificity_selection"]
    ].to_string(index=False))
    print("\nEvaluación global:\n", pd.DataFrame(rows).query("grupo_edad == 'GLOBAL'")[
        ["politica", "recall", "specificity", "balanced_accuracy", "precision", "fp", "fn"]
    ].to_string(index=False))
    print(f"\nResultados guardados en: {OUT}\nTest no utilizado; PULSO v1 no modificado.")


if __name__ == "__main__":
    main()
