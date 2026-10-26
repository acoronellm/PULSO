"""Auditoría exploratoria de edades para PULSO (solo datos de desarrollo).

Ejecutar desde la raíz del repositorio:
    python experiments/age_analysis/analizar_edades.py

No entrena modelos ni utiliza Test para seleccionar cortes por edad.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split  # dependencia ya existente

from ml.common import FEATURES, load_dataset, split_data

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / 'data' / 'processed' / 'cardio_clean_v1.csv'
DEFAULT_OUT = ROOT / 'experiments' / 'age_analysis' / 'results'


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return float('nan'), float('nan')
    p = k / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n))/denom
    half = z * np.sqrt(p*(1-p)/n + z*z/(4*n*n))/denom
    return float(center-half), float(center+half)


def summarize(df: pd.DataFrame, key: str, dataset: str) -> pd.DataFrame:
    records = []
    for label, group in df.groupby(key, observed=True, sort=True):
        n = int(len(group))
        pos = int(group['cardio'].sum())
        neg = n-pos
        low, high = wilson_interval(pos, n)
        records.append({'origen':dataset, 'grupo':str(label), 'n':n,
                        'positivos':pos, 'negativos':neg, 'prevalencia':pos/n,
                        'prevalencia_ic95_inf':low, 'prevalencia_ic95_sup':high,
                        'edad_min':float(group['age_years'].min()),
                        'edad_max':float(group['age_years'].max())})
    return pd.DataFrame(records)


def candidate_summary(df: pd.DataFrame, scheme: str, cuts: list[float], labels: list[str]) -> pd.DataFrame:
    tmp = df.copy()
    tmp['grupo_candidato'] = pd.cut(tmp['age_years'], bins=cuts, labels=labels,
                                     right=False, include_lowest=True)
    out = summarize(tmp, 'grupo_candidato', 'desarrollo (Train+Validation)')
    out.insert(0, 'esquema', scheme)
    out['advertencia_muestra'] = np.where(
        (out['positivos'] < 100) | (out['negativos'] < 100),
        'Menos de 100 observaciones de alguna clase (criterio exploratorio)', '')
    return out


def save_chart_age_dist(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ages = np.floor(df['age_years']).astype(int)
    counts = ages.value_counts().sort_index()
    ax.bar(counts.index, counts.values, width=0.85)
    for age in (50, 60, 70):
        ax.axvline(age - 0.5, linestyle='--', linewidth=1, label=f'{age} años')
    ax.set(title='PULSO | Distribución de edades en desarrollo', xlabel='Edad (años cumplidos)',
           ylabel='Registros')
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / '01_distribucion_edades.png', dpi=180)
    plt.close(fig)


def save_chart_prevalence(five: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.2))
    x = np.arange(len(five))
    values = five['prevalencia'].to_numpy()
    err = np.vstack((values-five['prevalencia_ic95_inf'].to_numpy(),
                     five['prevalencia_ic95_sup'].to_numpy()-values))
    ax.errorbar(x, values * 100, yerr=err*100, fmt='o-', capsize=3)
    ax.set_xticks(x, five['grupo'].tolist(), rotation=35, ha='right')
    ax.set_ylim(0, 100)
    ax.set(title='PULSO | Prevalencia de cardio=1 por intervalos de cinco años',
           xlabel='Edad (años)', ylabel='Porcentaje positivo e IC Wilson 95 %')
    fig.tight_layout()
    fig.savefig(out / '02_prevalencia_cinco_anos.png', dpi=180)
    plt.close(fig)


def save_chart_classes(candidate: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), sharey=True)
    for ax, (name, section) in zip(axes, candidate.groupby('esquema', sort=False)):
        x = np.arange(len(section))
        ax.bar(x, section['positivos'], label='cardio=1')
        ax.bar(x, section['negativos'], bottom=section['positivos'], label='cardio=0')
        ax.set_xticks(x, section['grupo'].tolist())
        ax.set(title=name, ylabel='Registros de desarrollo')
        ax.legend()
    fig.suptitle('Tamaño y balance por segmentación candidata')
    fig.tight_layout()
    fig.savefig(out / '03_balance_grupos_candidatos.png', dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=DEFAULT_DATA)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if not args.data.is_file():
        parser.error(f'No existe el CSV: {args.data}')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    X, y = load_dataset(args.data)
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = split_data(X, y)
    # Test: solo se verifica su tamaño; no se usa para escoger grupos.
    assert len(X_train)+len(X_val)+len(X_test)==len(X)
    assert set(X_train.index).isdisjoint(X_val.index)
    assert set(X_train.index).isdisjoint(X_test.index)
    assert set(X_val.index).isdisjoint(X_test.index)
    development = pd.concat([X_train.assign(cardio=y_train),
                             X_val.assign(cardio=y_val)], axis=0)
    assert development['cardio'].isin([0, 1]).all()

    d = development.copy()
    d['edad_entera'] = np.floor(d['age_years']).astype(int)
    min_age = int(d['edad_entera'].min())
    max_age = int(d['edad_entera'].max())
    # Etiquetas fijas 5 años, alineadas con múltiplos de cinco.
    left = 5 * (min_age // 5)
    right = 5 * (max_age // 5 + 1)
    bounds = list(range(left, right+1, 5))
    d['intervalo_5'] = pd.cut(d['age_years'], bins=bounds, right=False,
                             labels=[f'{a}–{a+4}' for a in bounds[:-1]])
    yearly = summarize(d, 'edad_entera', 'desarrollo (Train+Validation)')
    five = summarize(d, 'intervalo_5', 'desarrollo (Train+Validation)')

    candidates = pd.concat([
        candidate_summary(d, 'Actual: <50 / 50–59 / ≥60',
                          [-np.inf, 50, 60, np.inf], ['<50', '50–59', '≥60']),
        candidate_summary(d, 'Alternativo: <50 / 50–69 / ≥70',
                          [-np.inf, 50, 70, np.inf], ['<50', '50–69', '≥70'])
    ], ignore_index=True)

    yearly.to_csv(out/'edades_por_ano_desarrollo.csv', index=False)
    five.to_csv(out/'edades_cada_5_anos_desarrollo.csv', index=False)
    candidates.to_csv(out/'comparacion_grupos_candidatos.csv', index=False)
    save_chart_age_dist(d, out)
    save_chart_prevalence(five, out)
    save_chart_classes(candidates, out)

    # Resumen explícito de cobertura y duplicados EXACTOS entre filas de desarrollo.
    duplicates = int(d[FEATURES + ['cardio']].duplicated(keep=False).sum())
    summary = [
        'AUDITORÍA EXPLORATORIA DE EDADES | PULSO',
        'Sin entrenamiento ni modificación de PULSO v1.',
        'Los cortes se evalúan exclusivamente sobre Train+Validation.',
        f'Registros depurados: {len(X):,}',
        f'Train: {len(X_train):,} | Validation: {len(X_val):,} | Test reservado: {len(X_test):,}',
        f'Desarrollo: {len(d):,}',
        f'Edad mínima: {d.age_years.min():.2f} | máxima: {d.age_years.max():.2f}',
        f'Edad mediana: {d.age_years.median():.2f}',
        f'Prevalencia cardio=1 en desarrollo: {d.cardio.mean():.4f}',
        f'Filas con perfil de entrada y etiqueta duplicados en desarrollo: {duplicates:,}',
        'Un perfil duplicado puede ser una coincidencia genuina: revisar antes de eliminar.',
        'Los resultados NO establecen cortes clínicos ni validan modelos especializados.',
        'No usar Test para elegir umbrales/cortes/modelos de los experimentos B y C.',
    ]
    (out/'resumen_auditoria.txt').write_text('\n'.join(summary)+'\n', encoding='utf-8')
    print('\n'.join(summary))
    print('\nSEGMENTACIONES CANDIDATAS\n')
    print(candidates[['esquema','grupo','n','positivos','negativos','prevalencia','advertencia_muestra']].to_string(index=False))
    print(f'\nArchivos: {out}')


if __name__ == '__main__':
    main()
