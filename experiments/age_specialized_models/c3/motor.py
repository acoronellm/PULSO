"""C3 calibración: selección OOF anidada en Train; no consulta Test ni Validation para elegir método."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from tqdm.auto import tqdm
from ml.common import load_dataset, split_data, make_pipeline, sha256_file, FEATURES

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'data' / 'processed' / 'cardio_clean_v1.csv'
C2 = ROOT / 'experiments' / 'age_specialized_models' / 'results' / 'c2_v2'
OUT = ROOT / 'experiments' / 'age_specialized_models' / 'results' / 'c3_calibracion'
GRUPOS = ('menor_50', '50_59', '60_64')
ALGORITMOS = ('xgboost', 'gradient_boosting')
METODOS = ('none', 'sigmoid', 'isotonic')
SEED = 42
OUTER = 3
INNER = 3


def age_mask(age, grupo):
    if grupo not in GRUPOS:
        raise ValueError(f'Grupo desconocido: {grupo}')
    if grupo == 'menor_50':
        return age < 50
    if grupo == '50_59':
        return (age >= 50) & (age < 60)
    return age >= 60


def get_prob(est, X):
    p = np.asarray(est.predict_proba(X)[:, list(est.classes_).index(1)], dtype=float)
    if p.ndim != 1 or len(p) != len(X) or not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError('Probabilidades inválidas')
    return p


def build_estimator(algoritmo, selected_params, metodo, seed=SEED):
    from experiments.age_specialized_models.c2.motor import CONFIGS
    config = {'model_type': algoritmo, 'model_params': CONFIGS[algoritmo]['base'], 'threshold': 0.38}
    pipeline = make_pipeline(config).set_params(**selected_params)
    if metodo == 'none':
        return pipeline
    return CalibratedClassifierCV(estimator=pipeline, method=metodo,
                                  cv=StratifiedKFold(n_splits=INNER, shuffle=True, random_state=seed),
                                  ensemble=False)


def load_c2(algoritmo, grupo):
    folder = C2 / algoritmo / grupo
    report = json.loads((folder / 'resumen.json').read_text(encoding='utf-8'))
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if report.get('uso_test') is not False or manifest.get('uso_test') is not False:
        raise RuntimeError('C2 no confirma exclusión de Test')
    if report['dataset_sha256'] != manifest['dataset_sha256']:
        raise RuntimeError('Hashes C2 inconsistentes')
    if report['algoritmo'] != algoritmo or report['grupo'] != grupo:
        raise RuntimeError('Algoritmo/grupo no coinciden')
    return report, manifest


def git_hash():
    try:
        return subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return 'not-available'


def run(algoritmo, grupo):
    if algoritmo not in ALGORITMOS or grupo not in GRUPOS:
        raise ValueError('Algoritmo o grupo no permitido')
    destination = OUT / algoritmo / grupo
    if destination.exists():
        raise FileExistsError(f'Ya existe {destination}; no sobrescribir ejecuciones experimentales')
    report, manifest = load_c2(algoritmo, grupo)
    if sha256_file(DATA) != report['dataset_sha256']:
        raise ValueError('El dataset ha cambiado respecto a C2')
    X,y = load_dataset(DATA)
    (Xtr,ytr),(Xv,yv),_ = split_data(X,y) # test intencionalmente ignorado
    Xtr, ytr = Xtr.loc[age_mask(Xtr['age_years'], grupo)], ytr.loc[age_mask(Xtr['age_years'], grupo)]
    if list(Xtr.columns) != list(FEATURES):
        raise ValueError('Características distintas de PULSO')
    if len(Xtr) != report['n_train'] or len(Xv.loc[age_mask(Xv['age_years'], grupo)]) != report['n_val']:
        raise ValueError('Tamaños de partición distintos de C2')
    if Xtr.index.intersection(Xv.index).size:
        raise ValueError('Solapamiento Train-Validation')
    Xtr, ytr = Xtr.copy(), ytr.copy()
    outer = StratifiedKFold(n_splits=OUTER, shuffle=True, random_state=SEED)
    rows, folds = [], list(outer.split(Xtr, ytr))
    started = time.perf_counter()
    with tqdm(total=len(METODOS)*len(folds), desc=f'C3 {algoritmo} {grupo}', unit='fold', dynamic_ncols=True) as progress:
        for metodo in METODOS:
            for i,(train_idx,valid_idx) in enumerate(folds,1):
                model = build_estimator(algoritmo, report['params_seleccionados'], metodo)
                model.fit(Xtr.iloc[train_idx], ytr.iloc[train_idx])
                prob = get_prob(model, Xtr.iloc[valid_idx])
                truth = np.asarray(ytr.iloc[valid_idx])
                rows.append({'metodo':metodo,'fold':i,'n':len(truth),
                             'brier':float(brier_score_loss(truth,prob)),
                             'log_loss':float(log_loss(truth,prob,labels=[0,1])),
                             'roc_auc':float(roc_auc_score(truth,prob))})
                progress.update(1)
                progress.set_postfix(faltan=len(METODOS)*len(folds)-progress.n)
    detail = pd.DataFrame(rows)
    summary = (detail.groupby('metodo',as_index=False)
               .agg(brier_mean=('brier','mean'),brier_std=('brier','std'),
                    log_loss_mean=('log_loss','mean'),roc_auc_mean=('roc_auc','mean')))
    # Regla prefijada: minimizar Brier promedio; empates numéricos favorecen no calibrar.
    priority = {'none':0,'sigmoid':1,'isotonic':2}
    summary['orden'] = summary['metodo'].map(priority)
    summary = summary.sort_values(['brier_mean','orden'], kind='mergesort')
    selected = str(summary.iloc[0]['metodo'])
    best = build_estimator(algoritmo, report['params_seleccionados'], selected)
    best.fit(Xtr,ytr)
    # Smoke test sin utilizar Validation para decidir ni evaluar calibración.
    get_prob(best, Xtr.iloc[:min(10,len(Xtr))])
    destination.mkdir(parents=True, exist_ok=False)
    detail.to_csv(destination/'cv_calibracion_folds.csv',index=False)
    summary.drop(columns='orden').to_csv(destination/'cv_calibracion_resumen.csv',index=False)
    artifact = destination/'modelo_calibrado_experimental.joblib'
    joblib.dump(best,artifact)
    loaded = joblib.load(artifact)
    if not np.allclose(get_prob(best,Xtr.iloc[:10]),get_prob(loaded,Xtr.iloc[:10]),atol=1e-12):
        raise RuntimeError('El artefacto no reproduce las probabilidades')
    payload = {'experimento':'C3_calibracion', 'algoritmo':algoritmo,'grupo':grupo,
               'metodo_seleccionado':selected,'criterio':'menor Brier medio en CV externa sobre Train',
               'outer_folds':OUTER,'inner_folds':INNER,'semilla':SEED,'n_train':len(Xtr),
               'dataset_sha256':sha256_file(DATA),'c2_run_id':report['mlflow_run_id'],
               'c2_model_sha256':report['model_sha256'], 'c2_params':report['params_seleccionados'],
               'model_sha256':sha256_file(artifact),'git_commit':git_hash(),
               'uso_test':False,'validation_para_seleccion':False,
               'nota':'C3 selecciona calibración solo con Train; C3 umbrales vendrá después. La evaluación CV de la opción elegida tiene sesgo de selección: validación externa pendiente.',
               'fecha_utc':datetime.now(timezone.utc).isoformat(),'duracion_segundos':round(time.perf_counter()-started,2)}
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI','sqlite:///mlflow.db'))
    mlflow.set_experiment('PULSO-C3-Age-Calibration')
    with mlflow.start_run(run_name=f'{algoritmo}_{grupo}_calibracion') as active:
        mlflow.log_params({'algoritmo':algoritmo,'grupo':grupo,'metodo_seleccionado':selected,
                           'outer_folds':OUTER,'inner_folds':INNER,'dataset_sha256':payload['dataset_sha256'],
                           'git_commit':payload['git_commit'],'c2_run_id':report['mlflow_run_id']})
        for _,row in summary.iterrows():
            mlflow.log_metric('brier_'+row['metodo'],float(row['brier_mean']))
        mlflow.log_artifact(str(destination/'cv_calibracion_folds.csv'),artifact_path='evidencia')
        mlflow.log_artifact(str(destination/'cv_calibracion_resumen.csv'),artifact_path='evidencia')
        mlflow.log_artifact(str(artifact),artifact_path='modelo_experimental')
        payload['mlflow_run_id'] = active.info.run_id
        (destination/'manifest.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
        mlflow.log_artifact(str(destination/'manifest.json'),artifact_path='evidencia')
    print(json.dumps({'algoritmo':algoritmo,'grupo':grupo,'calibracion_elegida':selected,
                      'brier_cv':float(summary.iloc[0]['brier_mean']),
                      'mlflow_run_id':payload['mlflow_run_id']},ensure_ascii=False,indent=2))
    return payload


def main(algoritmo):
    parser=argparse.ArgumentParser()
    parser.add_argument('--grupo',required=True,choices=GRUPOS)
    args=parser.parse_args()
    run(algoritmo,args.grupo)
