"""C3-umbrales: 4 políticas, selección/evaluación separadas; Test no se utiliza."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             confusion_matrix, f1_score, log_loss, precision_score,
                             roc_auc_score)
from sklearn.model_selection import train_test_split
from tqdm.auto import tqdm
from ml.common import load_dataset, split_data, sha256_file

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / 'data/processed/cardio_clean_v1.csv'
C3_ROOT = ROOT / 'experiments/age_specialized_models/results/c3_calibracion'
OUT_ROOT = ROOT / 'experiments/age_specialized_models/results/c3_umbrales'
GROUPS = ('menor_50','50_59','60_64')
ALGORITHMS = ('xgboost','gradient_boosting')
POLICIES = ('recall80','balanced_accuracy','minimax','weighted_60_40')
SEED = 42
GRID = np.round(np.arange(0.01,1.00,0.01),2)


def age_group(age):
    age = np.asarray(age, dtype=float)
    return np.where(age < 50,'menor_50',np.where(age < 60,'50_59','60_64'))


def positive_prob(model,X):
    p=np.asarray(model.predict_proba(X), dtype=float)
    classes=list(model.classes_)
    if 1 not in classes or p.ndim!=2: raise ValueError('El modelo no expone clase positiva 1')
    q=p[:,classes.index(1)]
    if len(q)!=len(X) or not np.isfinite(q).all() or np.any((q<0)|(q>1)):
        raise ValueError('Probabilidades inválidas')
    return q


def metrics(y,p,threshold):
    y=np.asarray(y,dtype=int); p=np.asarray(p,dtype=float)
    pred=(p>=threshold).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    recall=tp/(tp+fn) if tp+fn else np.nan
    specificity=tn/(tn+fp) if tn+fp else np.nan
    return {'n':len(y),'tp':int(tp),'tn':int(tn),'fp':int(fp),'fn':int(fn),
            'recall':float(recall),'specificity':float(specificity),
            'balanced_accuracy':float((recall+specificity)/2),
            'precision':float(precision_score(y,pred,zero_division=0)),
            'npv':float(tn/(tn+fn)) if tn+fn else float('nan'),
            'f1':float(f1_score(y,pred,zero_division=0)),
            'accuracy':float(accuracy_score(y,pred))}


def select_threshold(y,p,policy,grid=GRID):
    if policy not in POLICIES: raise ValueError('Política desconocida')
    scores=[]
    for threshold in grid:
        row=metrics(y,p,float(threshold)); row['threshold']=float(threshold)
        if policy=='recall80': score=row['specificity'] if row['recall']>=0.8 else -np.inf
        elif policy=='balanced_accuracy': score=row['balanced_accuracy']
        elif policy=='minimax': score=min(row['recall'],row['specificity'])
        else: score=.6*row['recall']+.4*row['specificity']
        row['selection_score']=float(score)
        scores.append(row)
    frame=pd.DataFrame(scores)
    feasible=frame[np.isfinite(frame['selection_score'])]
    if feasible.empty:
        return {'policy':policy,'status':'sin_umbral_factible','threshold':None,'selection_score':None},frame
    # Desempate reproducible, sin referirse al umbral de producción.
    best=feasible.sort_values(['selection_score','balanced_accuracy','threshold'],
                              ascending=[False,False,False],kind='mergesort').iloc[0]
    return {'policy':policy,'status':'seleccionado','threshold':float(best['threshold']),
            'selection_score':float(best['selection_score']),
            'recall_selection':float(best['recall']),
            'specificity_selection':float(best['specificity'])},frame


def provenance_hash(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def git_commit():
    try: return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError): return 'not-available'


def run(algorithm,group):
    if algorithm not in ALGORITHMS or group not in GROUPS: raise ValueError('Algoritmo/grupo inválido')
    source=C3_ROOT/algorithm/group
    model_file=source/'modelo_calibrado_experimental.joblib'
    manifest_file=source/'manifest.json'
    if not model_file.is_file() or not manifest_file.is_file():
        raise FileNotFoundError(f'Faltan artefactos C3 en {source}')
    manifest=json.loads(manifest_file.read_text(encoding='utf-8'))
    if manifest.get('algoritmo')!=algorithm or manifest.get('grupo')!=group or manifest.get('uso_test') is not False:
        raise ValueError('Manifiesto C3 incompatible')
    if manifest.get('dataset_sha256')!=sha256_file(DATA): raise ValueError('Dataset no coincide con C3')
    if manifest.get('model_sha256')!=provenance_hash(model_file): raise ValueError('Hash de modelo C3 no coincide')
    dest=OUT_ROOT/algorithm/group
    if dest.exists(): raise FileExistsError(f'Ya existe {dest}; no se sobrescriben resultados')
    X,y=load_dataset(DATA)
    (_, _),(X_val,y_val),_=split_data(X,y)  # Test excluido del cálculo.
    strata=pd.Series(age_group(X_val['age_years']),index=X_val.index).astype(str)+'_'+y_val.astype(str)
    sel_idx, eval_idx=train_test_split(np.arange(len(X_val)),test_size=.5,
                                      stratify=strata,random_state=SEED)
    sel_group=age_group(X_val.iloc[sel_idx]['age_years'])==group
    eval_group=age_group(X_val.iloc[eval_idx]['age_years'])==group
    Xsel=X_val.iloc[sel_idx].loc[sel_group]; ysel=y_val.iloc[sel_idx].loc[sel_group]
    Xeval=X_val.iloc[eval_idx].loc[eval_group]; yeval=y_val.iloc[eval_idx].loc[eval_group]
    if len(Xsel)==0 or len(Xeval)==0 or ysel.nunique()<2 or yeval.nunique()<2:
        raise RuntimeError('Grupo insuficiente para evaluación')
    if Xsel.index.intersection(Xeval.index).size:raise RuntimeError('Solapamiento entre selección/evaluación')
    model=joblib.load(model_file)
    ps=positive_prob(model,Xsel); pe=positive_prob(model,Xeval)
    rows_select=[];rows_eval=[];curve=[]
    with tqdm(total=len(POLICIES),desc=f'C3 umbrales {algorithm} {group}',unit='política',dynamic_ncols=True) as bar:
        for policy in POLICIES:
            selection, scan=select_threshold(ysel,ps,policy)
            scan['policy']=policy;curve.append(scan)
            rows_select.append({'algorithm':algorithm,'group':group,**selection,
                                'n_selection':len(ysel)})
            if selection['threshold'] is not None:
                metric=metrics(yeval,pe,selection['threshold'])
                row={'algorithm':algorithm,'group':group,'policy':policy,
                     'threshold':selection['threshold'],'status':'evaluado',**metric,
                     'roc_auc':float(roc_auc_score(yeval,pe)),
                     'pr_auc':float(average_precision_score(yeval,pe)),
                     'brier':float(brier_score_loss(yeval,pe)),
                     'log_loss':float(log_loss(yeval,pe,labels=[0,1]))}
            else:
                row={'algorithm':algorithm,'group':group,'policy':policy,'threshold':None,
                     'status':'sin_umbral_factible'}
            rows_eval.append(row)
            bar.update(1);bar.set_postfix(faltan=len(POLICIES)-bar.n)
    dest.mkdir(parents=True,exist_ok=False)
    sel_file=dest/'umbrales_seleccionados.csv';eval_file=dest/'metricas_evaluacion.csv';curve_file=dest/'curvas_seleccion.csv'
    pd.DataFrame(rows_select).to_csv(sel_file,index=False)
    pd.DataFrame(rows_eval).to_csv(eval_file,index=False)
    pd.concat(curve,ignore_index=True).to_csv(curve_file,index=False)
    protocol={'experiment':'C3_thresholds','algorithm':algorithm,'group':group,
              'policies':list(POLICIES),'objective_recall80':'recall >= 0.80, then maximize specificity',
              'grid':'0.01..0.99 step 0.01','random_state':SEED,
              'validation_selection_total':len(sel_idx),'validation_evaluation_total':len(eval_idx),
              'selection_group':len(Xsel),'evaluation_group':len(Xeval),
              'dataset_sha256':manifest['dataset_sha256'],
              'c3_calibration_run_id':manifest.get('mlflow_run_id'),
              'c3_calibration_model_sha256':manifest['model_sha256'],
              'git_commit':git_commit(),'test_used':False,
              'caution':'Validation ya explorada en experimentos anteriores; evaluación interna exploratoria, no confirmatoria. La elección posterior entre políticas reutiliza esta evaluación.',
              'timestamp_utc':datetime.now(timezone.utc).isoformat()}
    pfile=dest/'protocolo.json';pfile.write_text(json.dumps(protocol,indent=2,ensure_ascii=False),encoding='utf-8')
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI','sqlite:///mlflow.db'))
    mlflow.set_experiment('PULSO-C3-Age-Thresholds')
    with mlflow.start_run(run_name=f'{algorithm}_{group}_umbrales') as run_ctx:
        mlflow.log_params({'algorithm':algorithm,'group':group,'seed':SEED,
                           'dataset_sha256':manifest['dataset_sha256'],
                           'c3_calibration_run_id':str(manifest.get('mlflow_run_id')),
                           'policies':'recall80,balanced_accuracy,minimax,weighted_60_40',
                           'test_used':False,'git_commit':protocol['git_commit']})
        for row in rows_eval:
            if row['status']=='evaluado':
                for key in ('recall','specificity','balanced_accuracy','precision','f1','npv'):
                    mlflow.log_metric(f"{row['policy']}_{key}",float(row[key]))
        for path in (sel_file,eval_file,curve_file,pfile):mlflow.log_artifact(str(path),artifact_path='resultados')
        protocol['mlflow_run_id']=run_ctx.info.run_id
        pfile.write_text(json.dumps(protocol,indent=2,ensure_ascii=False),encoding='utf-8')
        mlflow.log_artifact(str(pfile),artifact_path='resultados')
    print(json.dumps({'algorithm':algorithm,'group':group,'thresholds':rows_select,
                      'mlflow_run_id':protocol['mlflow_run_id']},indent=2,ensure_ascii=False))
    return protocol


def cli(algorithm):
    parser=argparse.ArgumentParser()
    parser.add_argument('--grupo',choices=GROUPS,required=True)
    a=parser.parse_args();run(algorithm,a.grupo)
