"""C4: evaluaciones exploratorias de PULSO; nunca utiliza Test."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from ml.common import load_dataset, split_data, sha256_file
from experiments.age_specialized_models.c3.umbrales.motor_umbrales import (
    age_group, metrics, positive_prob, select_threshold, POLICIES, GROUPS, ALGORITHMS,
)

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'data/processed/cardio_clean_v1.csv'
CAL = ROOT / 'experiments/age_specialized_models/results/c3_calibracion'
C3 = ROOT / 'experiments/age_specialized_models/results/c3_umbrales'
OUT = ROOT / 'experiments/age_specialized_models/results/c4'
SEED = 42

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def commit():
    try: return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError): return 'not-available'

def data_validation():
    X,y=load_dataset(DATA)
    (_, _),(Xv,yv),_=split_data(X,y)
    strata=pd.Series(age_group(Xv['age_years']),index=Xv.index).astype(str)+'_'+yv.astype(str)
    s,e=train_test_split(np.arange(len(Xv)),test_size=.5,random_state=SEED,stratify=strata)
    return Xv,yv,np.asarray(s),np.asarray(e)

def model_and_protocol(algo, group):
    path=CAL/algo/group
    mf=path/'manifest.json'; model_file=path/'modelo_calibrado_experimental.joblib'
    if not mf.is_file() or not model_file.is_file(): raise FileNotFoundError(f'Falta C3 calibración: {path}')
    man=json.loads(mf.read_text(encoding='utf-8'))
    if man.get('algoritmo')!=algo or man.get('grupo')!=group or man.get('uso_test') is not False:
        raise ValueError('Manifiesto C3 incompatible')
    if man.get('dataset_sha256')!=sha256_file(DATA) or man.get('model_sha256')!=sha(model_file):
        raise ValueError('Hashes C3 incompatibles')
    return joblib.load(model_file),man,sha(model_file)

def c3_thresholds(algo,group):
    path=C3/algo/group
    t=path/'umbrales_seleccionados.csv'; proto=path/'protocolo.json'
    if not t.is_file() or not proto.is_file(): raise FileNotFoundError(f'Falta C3 umbrales: {path}')
    frame=pd.read_csv(t)
    p=json.loads(proto.read_text(encoding='utf-8'))
    return frame,p

def threshold_map(df):
    if 'policy' not in df or 'threshold' not in df: raise ValueError('CSV de umbrales requiere policy y threshold')
    result={}
    for _,r in df.iterrows():
        if r['policy'] in POLICIES and pd.notna(r['threshold']): result[str(r['policy'])]=float(r['threshold'])
    if set(result)!=set(POLICIES): raise ValueError(f'Políticas incompletas: {result}')
    return result

def ci_wilson(k,n,z=1.959963984540054):
    if n==0: return (float('nan'),float('nan'))
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d
    r=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (float(max(0,c-r)),float(min(1,c+r)))

def bootstrap_paired(y, p1,p2,t1,t2,n=1000,seed=42):
    """IC percentil pareado, condicional a modelos/políticas fijos y muestra de evaluación."""
    rng=np.random.default_rng(seed); y=np.asarray(y); p1=np.asarray(p1);p2=np.asarray(p2)
    out=[]
    for i in range(n):
        idx=rng.integers(0,len(y),len(y))
        yy=y[idx]
        if len(np.unique(yy))<2: continue
        a=metrics(yy,p1[idx],t1); b=metrics(yy,p2[idx],t2)
        row={'delta_recall':a['recall']-b['recall'],
             'delta_specificity':a['specificity']-b['specificity'],
             'delta_ba':a['balanced_accuracy']-b['balanced_accuracy'],
             'delta_roc_auc':roc_auc_score(yy,p1[idx])-roc_auc_score(yy,p2[idx])}
        out.append(row)
    return pd.DataFrame(out)

def get_group_arrays(Xv,yv,idx,group):
    mask=age_group(Xv.iloc[idx]['age_years'])==group
    return Xv.iloc[idx].loc[mask], yv.iloc[idx].loc[mask]

def save(dest, files, meta):
    if dest.exists(): raise FileExistsError(f'{dest} ya existe; no sobrescribir')
    dest.mkdir(parents=True)
    for name,df in files.items(): df.to_csv(dest/name,index=False)
    meta.update({'git_commit':commit(),'dataset_sha256':sha256_file(DATA),
                 'seed':SEED,'test_used':False,'created_utc':datetime.now(timezone.utc).isoformat()})
    (dest/'protocolo.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    mlflow.set_tracking_uri('sqlite:///mlflow.db')
    mlflow.set_experiment('PULSO-C4-Age-Robustness')
    with mlflow.start_run(run_name=str(meta.get('analysis','C4')).replace(' ','_')) as run:
        mlflow.log_params({'analysis':str(meta.get('analysis','C4')),
                           'dataset_sha256':meta['dataset_sha256'],
                           'git_commit':meta['git_commit'],'seed':SEED,
                           'test_used':False})
        for key in ('repetitions','bootstrap_iterations','window_years','epsilon_years'):
            if key in meta: mlflow.log_param(key,meta[key])
        mlflow.log_artifacts(str(dest),artifact_path='c4_results')
        (dest/'mlflow_run_id.txt').write_text(run.info.run_id,encoding='utf-8')
