"""Motor común C2: selección de hiperparámetros por algoritmo y grupo.

Ejecutar mediante los scripts entrenar_*.py; NO usa Test.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import tempfile
import shutil
import json
import time
import warnings
import yaml
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from sklearn.model_selection import ParameterGrid, StratifiedKFold, ParameterSampler
from tqdm.auto import tqdm

from ml.common import load_dataset, make_pipeline, split_data, sha256_file, FEATURES

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'data' / 'processed' / 'cardio_clean_v1.csv'
OUT = ROOT / 'experiments' / 'age_specialized_models' / 'results' / 'c2_v2'
CONFIG_ROOT = Path(__file__).resolve().parent
SEED = 42
FOLDS = 5
BUDGET = {'logistic_regression': None, 'decision_tree': 50, 'random_forest': 50, 'gradient_boosting': 50, 'xgboost': 70}
PROTOCOL_VERSION = 'C2_v2_original_spaces_fivefold'
GRUPOS = ('menor_50', '50_59', '60_64', 'global')

# Espacios y candidatos provienen de los YAML originales de PULSO.
# Nunca modificar estas definiciones durante un entrenamiento ya iniciado.
CONFIGS = {
    'logistic_regression': {'base': {'max_iter': 3000, 'random_state': SEED}},
    'decision_tree': {'base': {'random_state': SEED}},
    'random_forest': {'base': {'random_state': SEED, 'n_jobs': 1}},
    'gradient_boosting': {'base': {'random_state': SEED}},
    'xgboost': {'base': {'objective': 'binary:logistic', 'eval_metric': 'logloss',
                        'tree_method': 'hist', 'random_state': SEED, 'n_jobs': 1}},
}


def build_candidates(algoritmo):
    """Muestreo reproducible sin reemplazo + candidato original garantizado."""
    search_path = CONFIG_ROOT / 'search_spaces' / f'{algoritmo}.yaml'
    baseline_path = CONFIG_ROOT / 'candidates' / f'{algoritmo}_tuned.yaml'
    search = yaml.safe_load(search_path.read_text(encoding='utf-8'))
    baseline = yaml.safe_load(baseline_path.read_text(encoding='utf-8'))
    if search['model_type'] != algoritmo or baseline['model_type'] != algoritmo:
        raise ValueError('Los YAML no coinciden con el algoritmo solicitado')
    space = search['param_grid']
    full_grid = list(ParameterGrid(space))
    reference = {'model__'+k: v for k,v in baseline['model_params'].items()
                 if k in {name.removeprefix('model__') for c in full_grid[:1] for name in c}}
    # También incluir explícitamente todos los parámetros del baseline que se buscaron.
    searchable = {k for candidate in full_grid for k in candidate}
    reference = {'model__'+k: v for k,v in baseline['model_params'].items()
                 if 'model__'+k in searchable}
    # Los defaults del YAML base y los candidatos originales mantienen el mismo contrato.
    budget = BUDGET[algoritmo]
    if budget is None or budget >= len(full_grid):
        selected = full_grid
        method = 'GridSearchCV_equivalente_manual'
    else:
        selected = list(ParameterSampler(space, n_iter=min(budget,len(full_grid)), random_state=SEED))
        method = 'RandomizedSearchCV_equivalente_manual'
    # Si el candidato original no aparece en la rejilla (p. ej. rango extra), se incluye explícitamente.
    selected_set = {json.dumps(x,sort_keys=True) for x in selected}
    original_key = json.dumps(reference,sort_keys=True)
    # Si la referencia omite parámetros que pertenecen al grid, rellenarlos con su valor original
    # cuando estén presentes en el modelo base; los defaults restantes son válidos y se mantienen.
    if original_key not in selected_set:
        selected.append(reference)
    # Conservar registros de procedencia y conjuntos de búsqueda exactos.
    return selected, method, search_path, baseline_path, len(full_grid), reference


def grupo_edades(edad):
    a = np.asarray(edad, dtype=float)
    if not np.isfinite(a).all():
        raise ValueError('age_years contiene valores ausentes o no finitos')
    return np.select([a < 50, (a >= 50) & (a < 60), a >= 60],
                     ['menor_50', '50_59', '60_64'], default='invalido')


def get_prob(estimator, X):
    classes = list(estimator.classes_)
    return estimator.predict_proba(X)[:, classes.index(1)]


def git_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return 'not-available'


def validate_partition(X_train, y_train, X_val, y_val, grupo):
    if grupo not in GRUPOS:
        raise ValueError(f'Grupo inválido: {grupo}')
    if X_train.empty or X_val.empty or len(X_train) != len(y_train) or len(X_val) != len(y_val):
        raise ValueError('Partición vacía o inconsistente')
    if X_train.index.intersection(X_val.index).size:
        raise ValueError('Train y Validation comparten índices: posible fuga de datos')
    for X, y in ((X_train, y_train), (X_val, y_val)):
        if set(y.unique()) != {0, 1}:
            raise ValueError('Cada partición debe contener ambas clases')
        if list(X.columns) != list(FEATURES):
            raise ValueError('Esquema/orden de variables no coincide con PULSO')
        if grupo != 'global' and not (grupo_edades(X['age_years']) == grupo).all():
            raise ValueError('Existen registros fuera del rango etario seleccionado')


def validate_probabilities(model, X):
    p = np.asarray(get_prob(model, X))
    if p.shape != (len(X),) or not np.isfinite(p).all() or (p < 0).any() or (p > 1).any():
        raise ValueError('Probabilidades inválidas del modelo')
    return p


def configure_mlflow():
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'sqlite:///mlflow.db'))
    mlflow.set_experiment('PULSO-C2-Age-Model-Selection')


def fit_one(algoritmo, grupo, X_train, y_train, X_val, y_val, data_path=DATA):
    validate_partition(X_train, y_train, X_val, y_val, grupo)
    spec = CONFIGS[algoritmo]
    cfg = {'model_type': algoritmo, 'model_params': spec['base'], 'threshold': 0.38}
    pipeline = make_pipeline(cfg)
    # Comprobación anticipada de parámetros para mostrar error legible si difiere el repositorio.
    grid, search_method, search_path, baseline_path, total_space, reference = build_candidates(algoritmo)
    for candidate in grid:
        clone(pipeline).set_params(**candidate)
    print(f'\n{algoritmo} / {grupo}: {search_method} | {len(grid)} candidatos de {total_space}, {FOLDS} folds')
    cv = StratifiedKFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    records = []
    start = time.perf_counter()
    progress = tqdm(total=len(grid) * FOLDS, desc=f'{algoritmo} | {grupo}',
                    unit='fit', dynamic_ncols=True, leave=True)
    try:
        for index, params in enumerate(grid):
            for fold, (idx_tr, idx_va) in enumerate(cv.split(X_train, y_train), start=1):
                model = clone(pipeline).set_params(**params)
                model.fit(X_train.iloc[idx_tr], y_train.iloc[idx_tr])
                probs = get_prob(model, X_train.iloc[idx_va])
                score = roc_auc_score(np.asarray(y_train)[idx_va], probs)
                records.append({'candidate': index, 'fold': fold,
                                'roc_auc': float(score), 'params': json.dumps(params, sort_keys=True)})
                progress.update(1)
                progress.set_postfix(auc=f'{score:.3f}', faltan=len(grid)*FOLDS-progress.n)
    finally:
        progress.close()
    detail = pd.DataFrame(records)
    summary = detail.groupby(['candidate', 'params'], as_index=False).agg(
        cv_roc_auc_mean=('roc_auc', 'mean'), cv_roc_auc_std=('roc_auc', 'std'))
    summary = summary.sort_values(['cv_roc_auc_mean', 'cv_roc_auc_std', 'candidate'],
                                  ascending=[False, True, True], kind='mergesort')
    selected = json.loads(summary.iloc[0]['params'])
    best = clone(pipeline).set_params(**selected)
    print(f'\nRefit final {algoritmo} / {grupo} usando todos sus registros Train...')
    best.fit(X_train, y_train)
    val_proba = validate_probabilities(best, X_val)
    val_y = np.asarray(y_val)
    elapsed = time.perf_counter() - start
    folder = OUT / algoritmo / grupo
    if folder.exists():
        raise FileExistsError(f'Ya hay resultados en {folder}. No se sobrescriben ejecuciones MLOps. Renombra la carpeta o revisa la ejecución previa.')
    folder.mkdir(parents=True, exist_ok=False)
    detail.to_csv(folder / 'cv_folds.csv', index=False)
    summary.to_csv(folder / 'cv_candidatos.csv', index=False)
    # Modelo experimental: no confundir con artefactos oficiales de producción.
    model_path = folder / 'modelo_experimental.joblib'
    joblib.dump(best, model_path)
    # Smoke test de serialización y de inferencia con el artefacto recuperado.
    loaded = joblib.load(model_path)
    if not np.allclose(validate_probabilities(loaded, X_val.iloc[:min(5, len(X_val))]),
                       val_proba[:min(5, len(X_val))], atol=1e-12):
        raise RuntimeError('El modelo guardado no reproduce sus predicciones')
    model_sha = sha256_file(model_path)
    dataset_sha = sha256_file(data_path)
    report = {
        'algoritmo': algoritmo, 'grupo': grupo, 'semilla': SEED,
        'dataset_sha256': dataset_sha, 'dataset_path': str(data_path),
        'model_sha256': model_sha, 'git_commit': git_commit(),
        'features': list(FEATURES), 'train_indices_sha256': hashlib.sha256(
            json.dumps(X_train.index.tolist()).encode()).hexdigest(),
        'validation_indices_sha256': hashlib.sha256(
            json.dumps(X_val.index.tolist()).encode()).hexdigest(),
        'n_train': int(len(y_train)), 'n_val': int(len(y_val)),
        'n_positivos_train': int(np.sum(np.asarray(y_train) == 1)),
        'n_candidatos': len(grid), 'cv_folds': FOLDS,
        'protocolo_version': PROTOCOL_VERSION, 'search_method': search_method,
        'tamano_espacio_original': total_space,
        'search_space_sha256': sha256_file(search_path),
        'original_candidate_sha256': sha256_file(baseline_path),
        'original_candidate_included': True,
        'candidato_original': reference,
        'cv_roc_auc_mean': float(summary.iloc[0]['cv_roc_auc_mean']),
        'cv_roc_auc_std': float(summary.iloc[0]['cv_roc_auc_std']),
        'params_seleccionados': selected,
        'validation_roc_auc_exploratorio': float(roc_auc_score(val_y, val_proba)),
        'validation_brier_exploratorio': float(brier_score_loss(val_y, val_proba)),
        'validation_log_loss_exploratorio': float(log_loss(val_y, val_proba, labels=[0, 1])),
        'tiempo_segundos': round(elapsed, 2),
        'uso_test': False,
        'nota': 'No elegir modelos, calibradores o umbrales utilizando repetidamente estas metricas Validation.',
        'fecha_utc': datetime.now(timezone.utc).isoformat(),
    }
    # Tracking existente de PULSO: una ejecución MLflow por algoritmo y grupo.
    # En caso de fallo de MLflow, la ejecución falla explícitamente (no queda falsamente trazada).
    configure_mlflow()
    with mlflow.start_run(run_name=f'{algoritmo}_{grupo}') as active:
        run_id = active.info.run_id
        mlflow.log_params({
            'algoritmo': algoritmo, 'grupo': grupo, 'semilla': SEED,
            'cv_folds': FOLDS, 'n_candidatos': len(grid),
            'search_method': search_method, 'protocol_version': PROTOCOL_VERSION,
            'search_space_sha256': report['search_space_sha256'],
            'original_candidate_sha256': report['original_candidate_sha256'],
            'n_train': len(y_train), 'n_validation': len(y_val),
            'dataset_sha256': dataset_sha, 'git_commit': git_commit(),
            'model_sha256': model_sha,
            'validation_usage': 'exploratory_only',
        })
        for k, v in selected.items():
            mlflow.log_param('selected_' + k.replace('model__', ''), str(v))
        mlflow.set_tags({'stage': 'C2_hyperparameter_search', 'use_test': 'false',
                         'source': 'experiment/ml-age-analysis', 'model_status': 'experimental'})
        mlflow.log_metrics({
            'cv_roc_auc_mean': report['cv_roc_auc_mean'],
            'cv_roc_auc_std': report['cv_roc_auc_std'],
            'validation_roc_auc_exploratorio': report['validation_roc_auc_exploratorio'],
            'validation_brier_exploratorio': report['validation_brier_exploratorio'],
            'validation_log_loss_exploratorio': report['validation_log_loss_exploratorio'],
            'tiempo_segundos': report['tiempo_segundos'],
        })
        report['mlflow_run_id'] = run_id
        report['mlflow_tracking_uri'] = mlflow.get_tracking_uri()
        (folder / 'resumen.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        manifest = {k: report[k] for k in (
            'algoritmo', 'grupo', 'dataset_sha256', 'model_sha256', 'git_commit',
            'mlflow_run_id', 'features', 'semilla', 'train_indices_sha256',
            'validation_indices_sha256', 'uso_test', 'fecha_utc',
            'protocolo_version', 'search_method', 'search_space_sha256',
            'original_candidate_sha256')}
        (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
        mlflow.log_artifact(str(search_path), artifact_path='c2/configs')
        mlflow.log_artifact(str(baseline_path), artifact_path='c2/configs')
        mlflow.log_artifacts(str(folder), artifact_path='c2')

    print(f'Completado: {algoritmo} / {grupo} | CV ROC-AUC={report["cv_roc_auc_mean"]:.4f} '
          f'| Validation ROC-AUC={report["validation_roc_auc_exploratorio"]:.4f}')
    print(f'Resultados en: {folder.relative_to(ROOT)}')


def run(algoritmo):
    parser = argparse.ArgumentParser(description=f'C2 PULSO: {algoritmo}, ejecución independiente')
    parser.add_argument('--grupo', choices=GRUPOS, required=True,
                        help='Entrena solo este grupo; ejecutar una vez por grupo')
    args = parser.parse_args()
    X, y = load_dataset(DATA)
    (X_tr, y_tr), (X_val, y_val), _ = split_data(X, y)
    group_tr = grupo_edades(X_tr['age_years'])
    group_val = grupo_edades(X_val['age_years'])
    if args.grupo != 'global':
        train_mask = group_tr == args.grupo
        val_mask = group_val == args.grupo
        X_tr, y_tr = X_tr.iloc[np.flatnonzero(train_mask)], y_tr.iloc[np.flatnonzero(train_mask)]
        X_val, y_val = X_val.iloc[np.flatnonzero(val_mask)], y_val.iloc[np.flatnonzero(val_mask)]
    if y_tr.nunique() < 2 or y_val.nunique() < 2:
        raise ValueError('Train o Validation no contiene las dos clases')
    fit_one(algoritmo, args.grupo, X_tr, y_tr, X_val, y_val, DATA)
