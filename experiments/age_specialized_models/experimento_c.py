"""PULSO experimento C: XGBoost global versus tres modelos especializados por edad.

Ejecutar desde raíz del repositorio:
    python -m experiments.age_specialized_models.experimento_c

Solo usa Train y Validation; NO utiliza Test ni altera artefactos oficiales.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import confusion_matrix, roc_auc_score, brier_score_loss, log_loss
from sklearn.model_selection import train_test_split

from ml.common import load_dataset, make_pipeline, split_data

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data' / 'processed' / 'cardio_clean_v1.csv'
CONFIG = ROOT / 'models' / 'pulso' / 'v1' / 'final_model.yaml'
OUT = ROOT / 'experiments' / 'age_specialized_models' / 'results' / 'c1'
SEED = 42
REFERENCE_THRESHOLD = 0.38
GRID = np.round(np.arange(.05, .951, .01), 2)
GROUPS = ('menor_50', '50_59', '60_64')


def age_group(age: pd.Series) -> np.ndarray:
    if age.isna().any():
        raise ValueError('Edades faltantes')
    result = np.select([age < 50, (age >= 50) & (age < 60), age >= 60], GROUPS, default='invalid')
    if (result == 'invalid').any():
        raise ValueError('Grupo inválido')
    return result


def rates(y, p, threshold):
    z = (np.asarray(p) >= threshold).astype(int)
    tn, fp, fn, tp = (int(v) for v in confusion_matrix(y, z, labels=[0, 1]).ravel())
    rec = tp / (tp + fn) if tp + fn else np.nan
    spec = tn / (tn + fp) if tn + fp else np.nan
    return {'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn, 'recall': rec, 'specificity': spec,
            'balanced_accuracy': (rec + spec) / 2, 'minimax': min(rec, spec),
            'precision': tp / (tp + fp) if tp + fp else 0.0,
            'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
            'accuracy': (tp + tn) / len(y)}


def choose_threshold(y, p, objective):
    if len(np.unique(y)) != 2:
        raise ValueError('La muestra para seleccionar umbral requiere ambas clases')
    rows = [{'threshold': float(t), **rates(y, p, t)} for t in GRID]
    df = pd.DataFrame(rows)
    df['distance_to_038'] = (df.threshold - REFERENCE_THRESHOLD).abs()
    result = df.sort_values([objective, 'balanced_accuracy', 'distance_to_038', 'threshold'],
                            ascending=[False, False, True, True], kind='mergesort').iloc[0]
    return float(result.threshold), float(result[objective]), df


def evaluation_row(name, policy, group, y, p, threshold):
    r = rates(y, p, threshold)
    return {'modelo': name, 'politica': policy, 'grupo_edad': group,
            'n': len(y), 'positives': int(np.sum(y == 1)), 'negatives': int(np.sum(y == 0)),
            'threshold': float(np.asarray(threshold).reshape(-1)[0]) if np.unique(threshold).size == 1 else np.nan, **r,
            'roc_auc': roc_auc_score(y, p) if len(np.unique(y)) == 2 else np.nan,
            'brier': brier_score_loss(y, p),
            'log_loss': log_loss(y, p, labels=[0, 1])}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
    if config.get('model_type') != 'xgboost':
        raise ValueError('Se esperaba la configuración XGBoost de PULSO v1')

    X, y = load_dataset(DATA)
    (X_train, y_train), (X_val, y_val), _ = split_data(X, y)
    group_train = age_group(X_train['age_years'])
    group_val = age_group(X_val['age_years'])
    ytr = np.asarray(y_train, dtype=int)
    yv = np.asarray(y_val, dtype=int)

    print('Entrenando XGBoost global solo con Train...')
    global_model = make_pipeline(config)
    global_model.fit(X_train, y_train)
    p_global = global_model.predict_proba(X_val)[:, list(global_model.classes_).index(1)]

    p_special = np.full(len(X_val), np.nan)
    train_counts = []
    for group in GROUPS:
        tr_mask = group_train == group
        val_mask = group_val == group
        if len(np.unique(ytr[tr_mask])) != 2:
            raise ValueError(f'El grupo {group} no contiene ambas clases en Train')
        print(f'Entrenando XGBoost especializado {group}: {tr_mask.sum()} filas...')
        specialist = make_pipeline(config)
        specialist.fit(X_train.iloc[np.flatnonzero(tr_mask)], y_train.iloc[np.flatnonzero(tr_mask)])
        p_special[val_mask] = specialist.predict_proba(X_val.iloc[np.flatnonzero(val_mask)])[:,
                                                    list(specialist.classes_).index(1)]
        train_counts.append({'grupo_edad': group, 'n_train': int(tr_mask.sum()),
                             'positives_train': int(ytr[tr_mask].sum()),
                             'n_validation': int(val_mask.sum())})
        # No exportar el modelo experimental como si estuviera aprobado para producción.
        del specialist

    if not np.isfinite(p_global).all() or not np.isfinite(p_special).all():
        raise ValueError('Probabilidades incompletas o no finitas')

    strat = pd.Series(group_val).astype(str) + '_' + pd.Series(yv).astype(str)
    cal_idx, ev_idx = train_test_split(np.arange(len(X_val)), test_size=.5,
                                      random_state=SEED, stratify=strat)

    probability_sets = {'global': p_global, 'especializado': p_special}
    thresholds = []
    curves = []
    selected = {}
    for name, probs in probability_sets.items():
        for scope in ('GLOBAL', *GROUPS):
            idx = cal_idx if scope == 'GLOBAL' else cal_idx[group_val[cal_idx] == scope]
            for objective in ('balanced_accuracy', 'minimax'):
                t, selection_score, curve = choose_threshold(yv[idx], probs[idx], objective)
                selected[(name, scope, objective)] = t
                thresholds.append({'modelo': name, 'grupo_edad': scope, 'objetivo': objective,
                                   'n_seleccion': len(idx), 'threshold': t,
                                   'selection_score': selection_score})
                if objective == 'balanced_accuracy':
                    curves.append(curve.assign(modelo=name, grupo_edad=scope))

    rows = []
    for name, probs_all in probability_sets.items():
        probs = probs_all[ev_idx]
        yy = yv[ev_idx]
        gg = group_val[ev_idx]
        policies = {'referencia_0_38': np.full(len(ev_idx), REFERENCE_THRESHOLD)}
        for objective in ('balanced_accuracy', 'minimax'):
            policies[f'{objective}_global'] = np.full(len(ev_idx), selected[(name, 'GLOBAL', objective)])
            policies[f'{objective}_edad'] = np.asarray([selected[(name, g, objective)] for g in gg])
        for policy, t in policies.items():
            for group in ('GLOBAL', *GROUPS):
                mask = np.ones(len(ev_idx), dtype=bool) if group == 'GLOBAL' else gg == group
                rows.append(evaluation_row(name, policy, group, yy[mask], probs[mask], t[mask]))

    # Diagnóstico de diferencias de discriminación/probabilidad, independiente de los umbrales.
    comparisons = []
    for group in ('GLOBAL', *GROUPS):
        mask = np.ones(len(ev_idx), dtype=bool) if group == 'GLOBAL' else group_val[ev_idx] == group
        yy = yv[ev_idx][mask]
        pa, pb = p_global[ev_idx][mask], p_special[ev_idx][mask]
        comparisons.append({'grupo_edad': group, 'n': int(mask.sum()),
                            'roc_auc_global': roc_auc_score(yy, pa),
                            'roc_auc_especializado': roc_auc_score(yy, pb),
                            'delta_auc_especializado_menos_global': roc_auc_score(yy, pb) - roc_auc_score(yy, pa),
                            'brier_global': brier_score_loss(yy, pa),
                            'brier_especializado': brier_score_loss(yy, pb),
                            'delta_brier_especializado_menos_global': brier_score_loss(yy, pb)-brier_score_loss(yy, pa)})

    pd.DataFrame(thresholds).to_csv(OUT / 'c1_umbrales_seleccionados.csv', index=False)
    pd.DataFrame(rows).to_csv(OUT / 'c1_metricas_evaluacion.csv', index=False)
    pd.DataFrame(comparisons).to_csv(OUT / 'c1_comparacion_probabilidades.csv', index=False)
    pd.DataFrame(train_counts).to_csv(OUT / 'c1_tamanos_grupos.csv', index=False)
    pd.concat(curves, ignore_index=True).to_csv(OUT / 'c1_curvas_seleccion.csv', index=False)
    metadata = {
        'experiment': 'C1 - global vs 3 age-specialized XGBoost', 'seed': SEED,
        'dataset': str(DATA.relative_to(ROOT)),
        'dataset_sha256': hashlib.sha256(DATA.read_bytes()).hexdigest(),
        'config': str(CONFIG.relative_to(ROOT)),
        'train_rows': len(X_train), 'validation_rows': len(X_val),
        'selection_rows': len(cal_idx), 'evaluation_rows': len(ev_idx), 'test_used': False,
        'model_count': {'global': 1, 'specialized': 3},
        'training': 'Global fit Train; specialists fit mutually exclusive age subsets of Train',
        'selection': 'Validation 50/50 stratified age group x label; thresholds fit selection half, evaluated on other half',
        'parameter_policy': 'Same PULSO v1 hyperparameters for all models; no per-group tuning',
        'evaluation': 'Shared evaluation rows for all model/policy combinations',
        'important_cautions': [
            'The official PULSO v1 production model was refitted on Train + Validation, unlike these experimental models.',
            'Model comparison and policy choice use reused Validation records; confirmatory claims require new independent data.',
            'Age boundaries were previously informed partly by Test subgroup analyses.',
            'A different specialized model can create a discontinuous probability at ages 50/60, even with one common threshold.',
            'These classifications are educational and not diagnoses or clinically validated future risk estimates.'
        ]
    }
    (OUT / 'c1_protocolo.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    print('\nComparación por probabilidades (evaluation):')
    print(pd.DataFrame(comparisons).round(4).to_string(index=False))
    summary = pd.DataFrame(rows)
    print('\nMétricas globales:')
    print(summary[summary.grupo_edad == 'GLOBAL'][
        ['modelo', 'politica', 'recall', 'specificity', 'balanced_accuracy', 'roc_auc', 'brier', 'fp', 'fn']
    ].round(4).to_string(index=False))
    print(f'\nGuardado en {OUT}\nTest no utilizado. PULSO v1 no modificado.')


if __name__ == '__main__':
    main()
