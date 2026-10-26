"""Auditoría descriptiva por edad del XGBoost final de PULSO v1.

Uso desde la raíz del repositorio:
    python analisis_subgrupos_pulso.py
    python analisis_subgrupos_pulso.py --bootstrap 2000

No entrena, recalibra ni selecciona umbrales. Analiza exclusivamente Test.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score, brier_score_loss, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score, roc_curve,
    precision_recall_curve,
)

from ml.common import load_dataset, split_data

ROOT = Path(__file__).resolve().parent
OFFICIAL = {"tn": 3204, "fp": 1997, "fn": 1009, "tp": 4082}
OFFICIAL_AUC = 0.7967571434274213


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ece(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    # Fixed-width binning, includes p==1 in final bin
    ids = np.minimum((p * bins).astype(int), bins - 1)
    return float(sum(np.sum(ids == i) / len(y) * abs(y[ids == i].mean() - p[ids == i].mean())
                     for i in range(bins) if np.any(ids == i)))


def stats(y: np.ndarray, p: np.ndarray, threshold: float) -> dict:
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = map(int, confusion_matrix(y, pred, labels=[0, 1]).ravel())
    return dict(n=len(y), positives=int(sum(y == 1)), negatives=int(sum(y == 0)),
                prevalence=float(np.mean(y)), tp=tp, tn=tn, fp=fp, fn=fn,
                recall=float(recall_score(y, pred, zero_division=0)),
                specificity=tn / (tn + fp) if (tn + fp) else np.nan,
                precision=float(precision_score(y, pred, zero_division=0)),
                accuracy=float(accuracy_score(y, pred)),
                f1=float(f1_score(y, pred, zero_division=0)),
                roc_auc=float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else np.nan,
                brier=float(brier_score_loss(y, p)), ece=ece(y, p),
                mean_probability=float(np.mean(p)))


def bootstrap_ci(y: np.ndarray, p: np.ndarray, threshold: float,
                 repeats: int, rng: np.random.Generator) -> dict:
    # Stratified within group to avoid missing classes in bootstrap replicates.
    neg, pos = np.flatnonzero(y == 0), np.flatnonzero(y == 1)
    columns = ("recall", "specificity", "precision", "roc_auc", "brier", "ece")
    if len(neg) < 2 or len(pos) < 2 or not repeats:
        return {f"{name}_{bound}": np.nan for name in columns for bound in ("ci_low", "ci_high")}
    samples = {name: [] for name in columns}
    for _ in range(repeats):
        ix = np.concatenate((rng.choice(neg, len(neg), replace=True),
                             rng.choice(pos, len(pos), replace=True)))
        current = stats(y[ix], p[ix], threshold)
        for name in columns:
            samples[name].append(current[name])
    return {f"{name}_{bound}": float(np.percentile(samples[name], q))
            for name in columns for bound, q in (("ci_low", 2.5), ("ci_high", 97.5))}


def save_histograms(df: pd.DataFrame, output: Path, threshold: float) -> None:
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.6), sharex=True, sharey=True)
    for ax, (group, frame) in zip(axs, df.groupby("grupo_edad", sort=False, observed=True)):
        for target, label in ((0, "cardio = 0"), (1, "cardio = 1")):
            values = frame.loc[frame.y == target, "p"]
            if not values.empty:
                ax.hist(values, bins=np.linspace(0, 1, 26), density=True,
                        alpha=0.48, label=f"{label} (n={len(values)})")
        ax.axvline(threshold, color="black", ls="--", label=f"Umbral {threshold:.2f}")
        ax.set_title(str(group)); ax.set_xlabel("Probabilidad estimada")
        ax.legend(fontsize=8)
    axs[0].set_ylabel("Densidad (normalizada por clase)")
    fig.suptitle("Distribución de probabilidades por edad y etiqueta real — Test")
    fig.tight_layout(); fig.savefig(output, dpi=180); plt.close(fig)


def save_roc_pr(df: pd.DataFrame, output: Path) -> None:
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    for group, frame in df.groupby("grupo_edad", sort=False, observed=True):
        y, p = frame.y.to_numpy(), frame.p.to_numpy()
        if len(np.unique(y)) != 2:
            continue
        fpr, tpr, _ = roc_curve(y, p)
        precision, recall, _ = precision_recall_curve(y, p)
        axs[0].plot(fpr, tpr, label=f"{group} (AUC={roc_auc_score(y,p):.3f})")
        axs[1].plot(recall, precision, label=f"{group} (prevalencia={np.mean(y):.2f})")
    axs[0].plot([0, 1], [0, 1], "k--", alpha=0.5)
    axs[0].set(title="ROC por edad", xlabel="1 - especificidad", ylabel="Recall")
    axs[1].set(title="Precision–Recall por edad", xlabel="Recall", ylabel="Precision")
    for ax in axs: ax.legend(fontsize=9); ax.grid(alpha=0.2)
    fig.tight_layout(); fig.savefig(output, dpi=180); plt.close(fig)


def save_calibration(df: pd.DataFrame, output: Path, n_bins: int) -> None:
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.7), sharex=True, sharey=True)
    for ax, (group, frame) in zip(axs, df.groupby("grupo_edad", sort=False, observed=True)):
        y, p = frame.y.to_numpy(), frame.p.to_numpy()
        observed, predicted = calibration_curve(y, p, n_bins=n_bins, strategy="uniform")
        ax.plot(predicted, observed, "o-", label="Observado")
        ax.plot([0, 1], [0, 1], "k--", label="Calibración perfecta")
        ax.set_title(f"{group}\nBrier={brier_score_loss(y,p):.3f}; ECE={ece(y,p):.3f}")
        ax.set_xlabel("Probabilidad media estimada")
        ax.grid(alpha=0.2); ax.legend(fontsize=8)
    axs[0].set_ylabel("Frecuencia observada de cardio = 1")
    fig.suptitle("Calibración descriptiva por edad — Test (bins con datos únicamente)")
    fig.tight_layout(); fig.savefig(output, dpi=180); plt.close(fig)


def save_rates(summary: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(summary)); width = 0.35
    ax.bar(x - width/2, summary.recall * 100, width, label="Recall")
    ax.bar(x + width/2, summary.specificity * 100, width, label="Especificidad")
    ax.axhline(80, linestyle="--", color="black", alpha=0.7, label="Objetivo global recall 80 %")
    ax.set_xticks(x, summary.grupo_edad)
    ax.set_ylabel("Porcentaje")
    ax.set_ylim(0, 105); ax.set_title("Sensibilidad y especificidad por edad — Test")
    ax.legend(); fig.tight_layout(); fig.savefig(output, dpi=180); plt.close(fig)


def save_confusions(summary: pd.DataFrame, output: Path) -> None:
    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    for ax, row in zip(axs, summary.itertuples()):
        cm = np.array([[row.tn, row.fp], [row.fn, row.tp]])
        ax.imshow(cm, cmap="Blues")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=12)
        ax.set_xticks([0, 1], ["Pred. 0", "Pred. 1"])
        ax.set_yticks([0, 1], ["Real 0", "Real 1"])
        ax.set_title(row.grupo_edad)
    fig.suptitle("Matrices de confusión por edad — Test, umbral oficial")
    fig.tight_layout(); fig.savefig(output, dpi=180); plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/processed/cardio_clean_v1.csv")
    parser.add_argument("--model", type=Path, default=ROOT / "artifacts/final/model/pulso_xgboost.joblib")
    parser.add_argument("--output", type=Path, default=ROOT / "resultados/subgrupos_pulso")
    parser.add_argument("--threshold", type=float, default=0.38)
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--bins", type=int, default=10)
    args = parser.parse_args()
    if not 0 <= args.threshold <= 1 or args.bootstrap < 0 or args.bins < 2:
        parser.error("threshold debe estar entre 0 y 1, bootstrap >= 0 y bins >= 2")
    X, y = load_dataset(args.data)
    (_, _), (_, _), (X_test, y_test) = split_data(X, y)
    model = joblib.load(args.model)  # Cargar solo artefactos confiables
    probabilities = np.asarray(model.predict_proba(X_test)[:, 1], dtype=float)
    truth = y_test.to_numpy(dtype=int)
    if not np.isfinite(probabilities).all() or not np.all((0 <= probabilities) & (probabilities <= 1)):
        raise ValueError("Probabilidades no válidas")
    # Guardrail: ensure same official test and model before subgroup discussion.
    global_metrics = stats(truth, probabilities, args.threshold)
    current_counts = {key: global_metrics[key] for key in OFFICIAL}
    auc_match = np.isclose(global_metrics["roc_auc"], OFFICIAL_AUC, rtol=0, atol=1e-6)
    if args.threshold == 0.38 and (current_counts != OFFICIAL or not auc_match):
        raise RuntimeError(f"La evaluación NO coincide con la oficial. Conteos: {current_counts}; "
                           f"ROC-AUC: {global_metrics['roc_auc']:.9f}. "
                           "Verifica archivo de datos, orden y modelo.")
    group = pd.cut(X_test["age_years"], bins=[-np.inf, 50, 60, np.inf],
                   labels=["<50 años", "50–59 años", "≥60 años"], right=False)
    df = pd.DataFrame({"grupo_edad": group.to_numpy(), "y": truth, "p": probabilities})
    records = []
    rng = np.random.default_rng(42)
    for name, frame in df.groupby("grupo_edad", sort=False, observed=True):
        yy, pp = frame.y.to_numpy(), frame.p.to_numpy()
        row = dict(grupo_edad=str(name), **stats(yy, pp, args.threshold))
        row.update(bootstrap_ci(yy, pp, args.threshold, args.bootstrap, rng))
        records.append(row)
    summary = pd.DataFrame(records)
    args.output.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output / "metricas_edad_test.csv", index=False)
    pd.DataFrame([global_metrics]).to_csv(args.output / "metricas_globales_test.csv", index=False)
    save_histograms(df, args.output / "01_distribucion_probabilidades.png", args.threshold)
    save_roc_pr(df, args.output / "02_roc_precision_recall.png")
    save_calibration(df, args.output / "03_calibracion_edad.png", args.bins)
    save_rates(summary, args.output / "04_recall_especificidad.png")
    save_confusions(summary, args.output / "05_matrices_confusion.png")
    report = ["PULSO v1 — Auditoría descriptiva por edad (Test)",
              f"Modelo: {args.model}", f"SHA256 modelo: {sha256(args.model)}",
              f"Dataset: {args.data}", f"SHA256 dataset: {sha256(args.data)}",
              f"Umbral de referencia: {args.threshold:.2f}",
              f"N test: {len(truth)}; ROC-AUC global: {global_metrics['roc_auc']:.9f}",
              f"Bootstrap estratificado por clase, {args.bootstrap} repeticiones, IC percentil 95 %.",
              "Intervalos descriptivos; no validación externa ni garantía clínica.",
              "Bins de calibración: intervalos uniformes, pueden estar vacíos.",
              "Comparar PR con cautela: su nivel de referencia cambia con la prevalencia.",
              "Este análisis usa un test previamente evaluado: no optimizar umbrales con él.",
              "", summary.to_string(index=False, float_format=lambda v: f"{v:.4f}")]
    (args.output / "reporte.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report[:12]))
    print("\nResumen por edad:\n")
    print(summary[["grupo_edad", "n", "positives", "tp", "tn", "fp", "fn", "recall", "specificity", "roc_auc", "brier", "ece"]].to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print(f"\nArchivos en: {args.output}")


if __name__ == "__main__":
    main()
