"""Análisis de robustez del experimento B de PULSO.

Ejecutar desde la raíz del repositorio:
    python -m experiments.age_thresholds.analisis_estabilidad_b

Entrena SOLO con Train; redivide Validation 100 veces, sin acceder a Test.
Las repeticiones reutilizan observaciones y NO son 100 evaluaciones independientes.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

from ml.common import load_dataset, make_pipeline, split_data
from experiments.age_thresholds.experimento_b import (
    CONFIG, DATA, OUTPUT, GROUPS, OFFICIAL_THRESHOLD,
    age_group, choose_threshold, metrics,
)

N_REPETITIONS = 100
MIN_RECALL = 0.80


def wilson_interval(success: int, total: int, z: float = 1.95996398454) -> tuple[float, float]:
    if total <= 0:
        return (float("nan"), float("nan"))
    p = success / total
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    half = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return (float(center - half), float(center + half))


def attach_ci(row: dict) -> dict:
    recall_lo, recall_hi = wilson_interval(row["tp"], row["positives"])
    spec_lo, spec_hi = wilson_interval(row["tn"], row["negatives"])
    return {**row, "recall_ci_low": recall_lo, "recall_ci_high": recall_hi,
            "specificity_ci_low": spec_lo, "specificity_ci_high": spec_hi}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load(Path(CONFIG).read_text(encoding="utf-8"))
    X, y = load_dataset(DATA)
    (X_train, y_train), (X_val, y_val), _ = split_data(X, y)

    print("Entrenando una sola vez XGBoost sobre Train...")
    model = make_pipeline(config)
    model.fit(X_train, y_train)
    p = np.asarray(model.predict_proba(X_val)[:, list(model.classes_).index(1)])
    truth = np.asarray(y_val)
    groups = age_group(X_val["age_years"]).to_numpy()
    ages = X_val["age_years"].to_numpy()
    stratify = np.array([f"{g}_{label}" for g, label in zip(groups, truth)])

    selection_rows = []
    eval_rows = []
    original_rows = []
    for seed in range(42, 42 + N_REPETITIONS):
        cal_idx, eval_idx = train_test_split(
            np.arange(len(truth)), test_size=0.5, random_state=seed,
            stratify=stratify,
        )
        selected = {"GLOBAL": choose_threshold(truth[cal_idx], p[cal_idx], MIN_RECALL)}
        for group in GROUPS:
            indices = cal_idx[groups[cal_idx] == group]
            selected[group] = choose_threshold(truth[indices], p[indices], MIN_RECALL)
        for group, chosen in selected.items():
            selection_rows.append({"seed": seed, "grupo_edad": group, **chosen})

        eval_p = p[eval_idx]
        eval_y = truth[eval_idx]
        eval_groups = groups[eval_idx]
        policies = {
            "umbral_0_38": np.full(len(eval_idx), OFFICIAL_THRESHOLD),
            "global_optimizado": np.full(len(eval_idx), selected["GLOBAL"]["threshold"]),
            "por_edad": np.asarray([selected[g]["threshold"] for g in eval_groups]),
        }
        for policy, thresholds in policies.items():
            pred = (eval_p >= thresholds).astype(int)
            for group in ["GLOBAL", *GROUPS]:
                mask = np.ones(len(eval_idx), dtype=bool) if group == "GLOBAL" else eval_groups == group
                row = {"seed": seed, "politica": policy, "grupo_edad": group,
                       **metrics(eval_y[mask], eval_p[mask], pred[mask])}
                eval_rows.append(row)
                if seed == 42:
                    original_rows.append(attach_ci(row))

    thresholds_df = pd.DataFrame(selection_rows)
    eval_df = pd.DataFrame(eval_rows)
    original_df = pd.DataFrame(original_rows)
    thresholds_df.to_csv(OUTPUT / "b_estabilidad_umbrales_100_particiones.csv", index=False)
    eval_df.to_csv(OUTPUT / "b_estabilidad_metricas_100_particiones.csv", index=False)
    original_df.to_csv(OUTPUT / "b_intervalos_confianza_evaluacion.csv", index=False)

    summaries = []
    for group, df in thresholds_df.groupby("grupo_edad", sort=False):
        summaries.append({
            "grupo_edad": group,
            "mediana_umbral": float(df["threshold"].median()),
            "q05_umbral": float(df["threshold"].quantile(.05)),
            "q95_umbral": float(df["threshold"].quantile(.95)),
            "min_umbral": float(df["threshold"].min()),
            "max_umbral": float(df["threshold"].max()),
            "proporcion_cumple_recall_seleccion": float(df["meets_recall_calibration"].mean()),
        })
    pd.DataFrame(summaries).to_csv(OUTPUT / "b_resumen_estabilidad_umbrales.csv", index=False)

    summaries_metrics = []
    for (policy, group), df in eval_df.groupby(["politica", "grupo_edad"], sort=False):
        summaries_metrics.append({
            "politica": policy, "grupo_edad": group,
            "recall_promedio": float(df["recall"].mean()),
            "recall_q05": float(df["recall"].quantile(.05)),
            "recall_q95": float(df["recall"].quantile(.95)),
            "fraccion_repeticiones_recall_mayor_igual_0_80": float((df["recall"] >= MIN_RECALL).mean()),
            "especificidad_promedio": float(df["specificity"].mean()),
            "especificidad_q05": float(df["specificity"].quantile(.05)),
            "especificidad_q95": float(df["specificity"].quantile(.95)),
            "fp_promedio": float(df["fp"].mean()),
            "fn_promedio": float(df["fn"].mean()),
        })
    pd.DataFrame(summaries_metrics).to_csv(OUTPUT / "b_resumen_estabilidad_metricas.csv", index=False)

    # Riesgo de discordancia de clasificación con probabilidades fijas si solo cambia
    # la política al atravesar un corte etario. No supone que el modelo mantenga
    # constante su probabilidad al cambiar la edad real.
    chosen42 = thresholds_df[thresholds_df.seed == 42].set_index("grupo_edad")["threshold"].to_dict()
    boundary_rows = []
    for boundary, below, above in [(50, "menor_50", "50_59"), (60, "50_59", "60_64")]:
        t_below, t_above = chosen42[below], chosen42[above]
        for window in [0.5, 1.0]:
            mask = np.abs(ages - boundary) <= window
            differing = ((p[mask] >= t_below) != (p[mask] >= t_above))
            boundary_rows.append({
                "limite_edad": boundary, "ventana_anos": window,
                "umbral_inferior": t_below, "umbral_superior": t_above,
                "n_ventana": int(mask.sum()),
                "n_podria_cambiar_clase_con_probabilidad_fija": int(differing.sum()),
                "proporcion_podria_cambiar": float(differing.mean()) if mask.sum() else None,
            })
    pd.DataFrame(boundary_rows).to_csv(OUTPUT / "b_sensibilidad_cortes_edad.csv", index=False)

    protocol = {
        "experiment": "B robustness", "repetitions": N_REPETITIONS,
        "train_rows": len(X_train), "validation_rows": len(X_val),
        "test_used": False, "random_seeds": [42, 141],
        "method": "Train fija; predicciones Validation fijas; 100 redistribuciones estratificadas 50/50 para selección/evaluación de umbrales",
        "confidence_intervals": "Wilson 95% binomial para seed=42; únicamente incertidumbre condicional al modelo y partición",
        "cautions": [
            "Las 100 particiones reutilizan registros y no constituyen 100 muestras independientes.",
            "Los cuantiles 5%-95% de repeticiones NO son intervalos de confianza poblacionales.",
            "Las estimaciones siguen siendo exploratorias; diseño de grupos informado parcialmente por análisis previos de Test.",
            "La comprobación de cortes de edad mantiene fija la probabilidad predicha; NO es una simulación realista de cambio de edad.",
            "No se reentrena en cada repetición; se mide estabilidad de política con modelo fijo, no estabilidad del entrenamiento.",
        ],
    }
    (OUTPUT / "b_protocolo_estabilidad.json").write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\n=== Umbrales: mediana y percentiles 5/95 ===")
    print(pd.DataFrame(summaries)[["grupo_edad", "mediana_umbral", "q05_umbral", "q95_umbral"]].to_string(index=False))
    print("\n=== Rendimiento global en las repeticiones ===")
    print(pd.DataFrame(summaries_metrics).query("grupo_edad == 'GLOBAL'")[
        ["politica", "recall_promedio", "especificidad_promedio", "fraccion_repeticiones_recall_mayor_igual_0_80"]
    ].to_string(index=False))
    print(f"\nResultados: {OUTPUT}")
    print("Test sin utilizar. Modelo oficial intacto.")


if __name__ == "__main__":
    main()
