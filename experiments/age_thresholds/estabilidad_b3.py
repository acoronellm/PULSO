"""PULSO · Robustez de B3 (100 particiones de Validation, modelo global fijo).

Desde la raíz del repositorio:
    python -m experiments.age_thresholds.estabilidad_b3

Requiere experiments/age_thresholds/experimento_b3.py. No utiliza Test.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

from ml.common import load_dataset, make_pipeline, split_data
from experiments.age_thresholds.experimento_b3 import (
    DATA, CONFIG, ROOT, OFFICIAL, B_PREVIOUS, GROUPS, OBJECTIVES,
    age_group, choose, metrics, score_table,
)

OUT = ROOT / "experiments" / "age_thresholds" / "results" / "b3_estabilidad"
SEEDS = range(42, 142)  # 100 particiones; incluye la original (42)
ALL_GROUPS = ("GLOBAL", *GROUPS)
POLICIES = ("referencia_0_38", "B_previo_recall80", *(
    f"B3_{objective}_{scope}" for objective in OBJECTIVES for scope in ("global", "edad")
))


def summarize(frame: pd.DataFrame, keys: list[str], measures: list[str]) -> pd.DataFrame:
    rows = []
    for group_key, part in frame.groupby(keys, sort=False):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        record = dict(zip(keys, group_key))
        record["repeticiones"] = len(part)
        for metric in measures:
            vals = part[metric].astype(float)
            record[f"{metric}_media"] = vals.mean()
            record[f"{metric}_mediana"] = vals.median()
            record[f"{metric}_p05"] = vals.quantile(.05)
            record[f"{metric}_p95"] = vals.quantile(.95)
            record[f"{metric}_min"] = vals.min()
            record[f"{metric}_max"] = vals.max()
        rows.append(record)
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    X, y = load_dataset(DATA)
    (X_train, y_train), (X_val, y_val), _ = split_data(X, y)
    print("Entrenando un XGBoost global con Train (una sola vez)...")
    model = make_pipeline(cfg)
    model.fit(X_train, y_train)
    probability = model.predict_proba(X_val)[:, list(model.classes_).index(1)]
    truth = np.asarray(y_val, dtype=int)
    groups = age_group(X_val["age_years"])
    strata = pd.Series(groups, index=X_val.index).astype(str) + "_" + y_val.astype(str)

    selected_rows, evaluation_rows, comparison_rows, group_worst_rows = [], [], [], []
    for i, seed in enumerate(SEEDS, 1):
        select_idx, eval_idx = train_test_split(
            np.arange(len(truth)), test_size=.5, random_state=seed, stratify=strata,
        )
        selected = {}
        for group in ALL_GROUPS:
            idx = select_idx if group == "GLOBAL" else select_idx[groups[select_idx] == group]
            table = score_table(truth[idx], probability[idx])
            for objective in OBJECTIVES:
                item = choose(table, objective)
                selected[(objective, group)] = item["threshold"]
                selected_rows.append({"semilla": seed, "objetivo": objective,
                                      "grupo_edad": group, "n_seleccion": len(idx), **item})

        yy, pp, gg = truth[eval_idx], probability[eval_idx], groups[eval_idx]
        thresholds = {
            "referencia_0_38": np.full(len(eval_idx), OFFICIAL),
            "B_previo_recall80": np.array([B_PREVIOUS[g] for g in gg]),
        }
        for objective in OBJECTIVES:
            thresholds[f"B3_{objective}_global"] = np.full(len(eval_idx), selected[(objective, "GLOBAL")])
            thresholds[f"B3_{objective}_edad"] = np.array([selected[(objective, g)] for g in gg])

        base_prediction = pp >= OFFICIAL
        result_by_policy = {}
        for policy, ts in thresholds.items():
            prediction = pp >= ts
            result_by_policy[policy] = {}
            for group in ALL_GROUPS:
                mask = np.ones(len(yy), dtype=bool) if group == "GLOBAL" else gg == group
                result = metrics(yy[mask], pp[mask], prediction[mask].astype(int))
                evaluation_rows.append({"semilla": seed, "politica": policy,
                                        "grupo_edad": group, **result})
                result_by_policy[policy][group] = result

            # Cambios en FP/FN respecto a 0.38 sobre *los mismos* registros.
            base_fp = int(np.sum(base_prediction & (yy == 0)))
            base_fn = int(np.sum(~base_prediction & (yy == 1)))
            cur_fp = int(np.sum(prediction & (yy == 0)))
            cur_fn = int(np.sum(~prediction & (yy == 1)))
            comparison_rows.append({"semilla": seed, "politica": policy,
                                    "delta_fp_vs_038": cur_fp - base_fp,
                                    "delta_fn_vs_038": cur_fn - base_fn,
                                    "cambios_clasificacion_vs_038": int(np.sum(prediction != base_prediction))})

            per_group = [result_by_policy[policy][g] for g in GROUPS]
            group_worst_rows.append({
                "semilla": seed, "politica": policy,
                "peor_recall_grupal": min(x["recall"] for x in per_group),
                "peor_especificidad_grupal": min(x["specificity"] for x in per_group),
                "peor_ba_grupal": min(x["balanced_accuracy"] for x in per_group),
                "amplitud_recall_grupal": max(x["recall"] for x in per_group) - min(x["recall"] for x in per_group),
                "amplitud_especificidad_grupal": max(x["specificity"] for x in per_group) - min(x["specificity"] for x in per_group),
            })
        if i % 20 == 0:
            print(f"Particiones completadas: {i}/100")

    selected_df = pd.DataFrame(selected_rows)
    eval_df = pd.DataFrame(evaluation_rows)
    comparison_df = pd.DataFrame(comparison_rows)
    worst_df = pd.DataFrame(group_worst_rows)
    selected_df.to_csv(OUT / "b3_estabilidad_umbrales_100.csv", index=False)
    eval_df.to_csv(OUT / "b3_estabilidad_metricas_100.csv", index=False)
    comparison_df.to_csv(OUT / "b3_estabilidad_cambios_vs_038_100.csv", index=False)
    worst_df.to_csv(OUT / "b3_estabilidad_peor_grupo_100.csv", index=False)

    summary_thresholds = summarize(selected_df, ["objetivo", "grupo_edad"], ["threshold", "recall_selection", "specificity_selection"])
    summary_metrics = summarize(eval_df, ["politica", "grupo_edad"], ["recall", "specificity", "balanced_accuracy", "precision", "fp", "fn"])
    summary_comparisons = summarize(comparison_df, ["politica"], ["delta_fp_vs_038", "delta_fn_vs_038", "cambios_clasificacion_vs_038"])
    summary_worst = summarize(worst_df, ["politica"], ["peor_recall_grupal", "peor_especificidad_grupal", "peor_ba_grupal", "amplitud_recall_grupal", "amplitud_especificidad_grupal"])
    summary_thresholds.to_csv(OUT / "b3_resumen_umbrales.csv", index=False)
    summary_metrics.to_csv(OUT / "b3_resumen_metricas.csv", index=False)
    summary_comparisons.to_csv(OUT / "b3_resumen_cambios_vs_038.csv", index=False)
    summary_worst.to_csv(OUT / "b3_resumen_peor_grupo.csv", index=False)

    # La semilla 42 debe reproducir exactamente los resultados iniciales de B3.
    source_dir = ROOT / "experiments" / "age_thresholds" / "results" / "b3"
    original_csv = source_dir / "b3_umbrales_seleccionados.csv"
    check = "archivo_original_no_disponible"
    if original_csv.exists():
        original = pd.read_csv(original_csv)
        repeated = selected_df[selected_df.semilla == 42]
        joined = original.merge(repeated, on=["objetivo", "grupo_edad"], suffixes=("_original", "_repetido"))
        if len(joined) == len(original) == len(repeated):
            check = "coincide" if np.allclose(joined.threshold_original, joined.threshold_repetido) else "NO_COINCIDE"
        else:
            check = "NO_COINCIDE_numero_filas"
        if check != "coincide":
            raise RuntimeError("El control de reproducibilidad con B3 original falló: " + check)

    protocol = {
        "experimento": "B3 estabilidad", "repeticiones": len(SEEDS),
        "semillas": [min(SEEDS), max(SEEDS)], "train_rows": len(X_train),
        "validation_rows": len(X_val), "test_utilizado": False,
        "sha256_dataset": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "config": str(CONFIG.relative_to(ROOT)),
        "esquema": "Train fija, modelo único; 100 divisiones estratificadas 50/50 de Validation por grupo×etiqueta; selección/evaluación separadas en cada repetición",
        "politicas": list(POLICIES), "comprobacion_semilla_42": check,
        "advertencias": [
            "Las 100 redistribuciones no son independientes; los percentiles NO son intervalos de confianza poblacionales.",
            "Se reutiliza el mismo modelo, por lo que no se estima variabilidad por reentrenamiento.",
            "No elegir una política ganadora después de comparar reiteradamente sobre los mismos registros sin nueva validación independiente.",
            "Los límites de edad fueron informados parcialmente por un análisis anterior de Test.",
            "El objetivo 60/40 es experimental y no está validado clínicamente.",
        ],
    }
    (OUT / "b3_protocolo_estabilidad.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nResumen de estabilidad de umbrales:\n", summary_thresholds[["objetivo", "grupo_edad", "threshold_mediana", "threshold_p05", "threshold_p95"]].to_string(index=False))
    print("\nMétricas globales medias:\n", summary_metrics[summary_metrics.grupo_edad == "GLOBAL"][["politica", "recall_media", "specificity_media", "balanced_accuracy_media"]].to_string(index=False))
    print("\nPeor grupo (promedio sobre las 100 repeticiones):\n", summary_worst[["politica", "peor_recall_grupal_media", "peor_especificidad_grupal_media"]].to_string(index=False))
    print("\nControl contra B3 original (semilla 42):", check)
    print("Archivos guardados en:", OUT)


if __name__ == "__main__":
    main()
