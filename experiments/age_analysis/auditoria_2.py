"""Segunda auditoría de edades PULSO: descriptiva, sin reentrenar ni tocar Test.

Desde raíz de PULSO:
    python -m experiments.age_analysis.auditoria_2
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ml.common import FEATURES, load_dataset, split_data

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/processed/cardio_clean_v1.csv'
OUTPUT = ROOT / 'experiments/age_analysis/results/auditoria_2'
GROUPS = ['<50', '50–59', '60–64']
VARIABLES = ['ap_hi', 'ap_lo', 'bmi', 'weight', 'height', 'smoke', 'alco', 'active']


def age_group(series: pd.Series) -> pd.Categorical:
    return pd.cut(series, bins=[-np.inf, 50, 60, np.inf],
                  labels=GROUPS, right=False)


def duplicate_report(train: pd.DataFrame, val: pd.DataFrame) -> pd.DataFrame:
    """Perfiles idénticos son una señal a revisar, no prueba de mismo individuo."""
    rows = []
    for keys, name in [(FEATURES, 'mismas 10 variables'),
                       (FEATURES + ['cardio'], 'mismas 10 variables y etiqueta')]:
        both = pd.concat([train.assign(origen='Train'),
                          val.assign(origen='Validation')], ignore_index=True)
        counts = both.groupby(keys, dropna=False).size()
        duplicated_profiles = counts[counts > 1]
        train_keys = pd.MultiIndex.from_frame(train[keys])
        val_keys = pd.MultiIndex.from_frame(val[keys])
        overlap_train = train_keys.isin(val_keys)
        overlap_val = val_keys.isin(train_keys)
        rows.append({'criterio': name,
                     'filas_duplicadas_en_desarrollo': int(both.duplicated(keys, keep=False).sum()),
                     'perfiles_distintos_repetidos': int(len(duplicated_profiles)),
                     'filas_train_con_equivalente_en_validation': int(overlap_train.sum()),
                     'filas_validation_con_equivalente_en_train': int(overlap_val.sum())})
    return pd.DataFrame(rows)


def make_plots(data: pd.DataFrame, out: Path) -> None:
    ages = GROUPS
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    for ax, var in zip(axes, ['ap_hi', 'ap_lo', 'bmi']):
        series = [data.loc[data.grupo_edad == group, var].to_numpy() for group in ages]
        ax.boxplot(series, tick_labels=ages, showfliers=False)
        ax.set_title(var)
        ax.set_ylabel('Valor observado')
    fig.suptitle('PULSO | Distribución de mediciones por edad — Desarrollo')
    fig.tight_layout()
    fig.savefig(out/'01_mediciones_por_edad.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5), sharey=True)
    for ax, var in zip(axes, ['smoke', 'alco', 'active']):
        frac = data.groupby('grupo_edad', observed=True)[var].mean().reindex(ages) * 100
        ax.bar(ages, frac)
        ax.set_title(var)
        ax.set_ylim(0, 100)
        ax.set_ylabel('Porcentaje con valor 1')
    fig.suptitle('PULSO | Hábitos reportados por edad — Desarrollo')
    fig.tight_layout()
    fig.savefig(out/'02_habitos_por_edad.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5), sharey=False)
    for ax, var in zip(axes, ['ap_hi', 'bmi', 'active']):
        if var == 'active':
            temp = data.groupby(['grupo_edad', 'cardio'], observed=True)[var].mean().unstack() * 100
            temp = temp.reindex(ages)
            x = np.arange(len(ages))
            ax.bar(x-0.2, temp[0], 0.4, label='cardio=0')
            ax.bar(x+0.2, temp[1], 0.4, label='cardio=1')
            ax.set_xticks(x, ages)
            ax.set_ylabel('Porcentaje con active=1')
        else:
            values = [data.loc[(data.grupo_edad == age) & (data.cardio == label), var].to_numpy()
                      for age in ages for label in [0, 1]]
            ax.boxplot(values, positions=[1,2, 4,5, 7,8], widths=.7,
                       showfliers=False, tick_labels=['0','1']*3)
            ax.set_xticks([1.5,4.5,7.5], ages)
            ax.set_ylabel('Valor observado')
        ax.set_title(var)
    axes[2].legend()
    fig.suptitle('PULSO | Variables según edad y etiqueta — Desarrollo')
    fig.tight_layout()
    fig.savefig(out/'03_variables_por_edad_y_clase.png', dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=DATA)
    parser.add_argument('--out', type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not args.data.is_file():
        parser.error(f'CSV no encontrado: {args.data}')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    X, y = load_dataset(args.data)
    (X_train, y_train), (X_val, y_val), (X_test, _) = split_data(X, y)
    assert len(X_train) + len(X_val) + len(X_test) == len(X)
    assert set(X_train.index).isdisjoint(X_val.index)
    assert set(X_train.index).isdisjoint(X_test.index)
    assert set(X_val.index).isdisjoint(X_test.index)

    train = X_train.copy().assign(cardio=y_train)
    val = X_val.copy().assign(cardio=y_val)
    dev = pd.concat([train, val], axis=0)
    dev['grupo_edad'] = age_group(dev.age_years)
    if dev.grupo_edad.isna().any():
        raise ValueError('Se encontraron edades sin grupo')

    summary = []
    for (group, label), df in dev.groupby(['grupo_edad', 'cardio'], observed=True):
        row = {'grupo': str(group), 'cardio': int(label), 'n': int(len(df))}
        for v in ['age_years', 'ap_hi', 'ap_lo', 'bmi', 'height', 'weight']:
            row[f'{v}_mediana'] = float(df[v].median())
            row[f'{v}_p25'] = float(df[v].quantile(.25))
            row[f'{v}_p75'] = float(df[v].quantile(.75))
        for v in ['smoke', 'alco', 'active']:
            row[f'{v}_tasa_1'] = float((df[v] == 1).mean())
        summary.append(row)
    stats = pd.DataFrame(summary)
    stats.to_csv(out/'variables_por_grupo_y_clase.csv', index=False)

    corr = []
    for group, d in dev.groupby('grupo_edad', observed=True):
        for variable in VARIABLES + ['age_years']:
            if d[variable].nunique() < 2:
                value = np.nan
            else:
                value = d[variable].corr(d['cardio'], method='spearman')
            corr.append({'grupo':str(group), 'variable':variable,
                         'rho_spearman_con_cardio':value, 'n':len(d)})
    pd.DataFrame(corr).to_csv(out/'asociaciones_exploratorias.csv', index=False)

    duplicates = duplicate_report(train, val)
    duplicates.to_csv(out/'duplicados_desarrollo.csv', index=False)
    make_plots(dev, out)

    lines = ['PULSO — AUDITORÍA 2 (solo desarrollo)',
             f'Train: {len(train)}; Validation: {len(val)}; Test reservado: {len(X_test)}',
             'NO se ha entrenado, ajustado ni evaluado XGBoost.',
             'Las asociaciones Spearman son descriptivas, no causales.',
             'Las coincidencias exactas entre perfiles no demuestran duplicados de pacientes.',
             'Las clases en este análisis corresponden a la etiqueta cardio, no eventos futuros.',
             '\nDuplicados:', duplicates.to_string(index=False),
             '\nArchivos: variables_por_grupo_y_clase.csv, asociaciones_exploratorias.csv,',
             'duplicados_desarrollo.csv y 3 figuras PNG.']
    (out/'resumen.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('\n'.join(lines))
    print(f'\nCarpeta de resultados: {out}')

if __name__ == '__main__':
    main()
