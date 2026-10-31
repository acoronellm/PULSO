"""C5: Train-only global vs C3 especializados en el mismo holdout de Validation.

No lee ni usa Test, no carga el modelo oficial entrenado con Train+Validation.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.model_selection import train_test_split
from ml.common import load_dataset, split_data, sha256_file, make_pipeline, FEATURES
from experiments.age_specialized_models.c3.umbrales.motor_umbrales import (
    GROUPS, POLICIES, age_group, positive_prob, metrics, select_threshold,
)

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/'data/processed/cardio_clean_v1.csv'
CAL = ROOT/'experiments/age_specialized_models/results/c3_calibracion'
C3_THRESH = ROOT/'experiments/age_specialized_models/results/c3_umbrales'
OUT = ROOT/'experiments/age_specialized_models/results/c5_comparacion'
SEED = 42
OFFICIAL_THRESHOLD = 0.38
GLOBAL_CONFIG = dict(model_type='xgboost',model_params=dict(
    colsample_bytree=.8,learning_rate=.03,max_depth=3,min_child_weight=5,
    n_estimators=300,reg_lambda=5,subsample=.8,objective='binary:logistic',
    eval_metric='logloss',tree_method='hist',random_state=42,n_jobs=-1),threshold=OFFICIAL_THRESHOLD)

def git_commit():
    try: return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()
    except Exception: return 'not-available'

def sha(path):
    return sha256_file(path)

def checked_model(algo,group,expected_data_hash):
    d=CAL/algo/group; f=d/'modelo_calibrado_experimental.joblib'; mf=d/'manifest.json'
    if not f.is_file() or not mf.is_file(): raise FileNotFoundError(f'Faltan artefactos C3 calibración: {d}')
    m=json.loads(mf.read_text(encoding='utf-8'))
    if (m.get('algoritmo'),m.get('grupo'),m.get('uso_test'))!=(algo,group,False):
        raise ValueError(f'Manifiesto incompatible: {mf}')
    if m.get('dataset_sha256')!=expected_data_hash or m.get('model_sha256')!=sha(f):
        raise ValueError(f'Integridad inválida: {f}')
    return joblib.load(f),sha(f)

def checked_thresholds(algo,group,expected_data_hash,ns,ne):
    d=C3_THRESH/algo/group
    mf=d/'protocolo.json'; f=d/'umbrales_seleccionados.csv'
    if not f.is_file() or not mf.is_file(): raise FileNotFoundError(f'Faltan umbrales C3: {d}')
    proto=json.loads(mf.read_text(encoding='utf-8'))
    if (proto.get('algorithm'),proto.get('group'),proto.get('test_used'))!=(algo,group,False):
        raise ValueError(f'Protocolo incompatible: {mf}')
    if proto.get('dataset_sha256')!=expected_data_hash or proto.get('validation_selection_total')!=ns or proto.get('validation_evaluation_total')!=ne:
        raise ValueError(f'Split o dataset distinto a C3: {mf}')
    df=pd.read_csv(f)
    if df['policy'].duplicated().any():raise ValueError('Políticas duplicadas')
    threshold={str(r['policy']):float(r['threshold']) for _,r in df.iterrows() if pd.notna(r['threshold'])}
    if set(threshold)!=set(POLICIES): raise ValueError(f'Políticas faltantes: {d}')
    return threshold

def split_validation(Xv,yv):
    strata=pd.Series(age_group(Xv['age_years']),index=Xv.index).astype(str)+'_'+yv.astype(str)
    si,ei=train_test_split(np.arange(len(Xv)),test_size=.5,stratify=strata,random_state=SEED)
    assert set(si).isdisjoint(ei)
    return Xv.iloc[si],yv.iloc[si],Xv.iloc[ei],yv.iloc[ei]

def summarize(y,p,t,configuration,policy,group):
    yy=np.asarray(y,dtype=int); pp=np.asarray(p,dtype=float)
    m=metrics(yy,pp,t)
    return dict(configuration=configuration,policy=policy,group=group,threshold=float(t),**m,
                roc_auc=float(roc_auc_score(yy,pp)) if len(np.unique(yy))==2 else np.nan,
                pr_auc=float(average_precision_score(yy,pp)),brier=float(brier_score_loss(yy,pp)))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--solo-verificar',action='store_true',help='Verifica artefactos sin crear salidas ni entrenar')
    args=parser.parse_args()
    if OUT.exists():raise FileExistsError(f'{OUT} ya existe; conserve resultados y renombre la carpeta para repetir')
    digest=sha(DATA)
    X,y=load_dataset(DATA)
    (Xt,yt),(Xv,yv),_=split_data(X,y)  # Test nunca se materializa en variables.
    if list(Xt.columns)!=list(FEATURES) or list(Xv.columns)!=list(FEATURES):raise ValueError('Orden de FEATURES distinto')
    Xs,ys,Xe,ye=split_validation(Xv,yv)
    if len(Xs)!=5145 or len(Xe)!=5146:raise ValueError('Tamaños inesperados respecto a C3')
    if Xt.index.intersection(Xv.index).size:raise ValueError('Train y Validation solapados')
    special={}; source_hashes={}; thresholds={}
    for algo in ('xgboost','gradient_boosting'):
        for group in GROUPS:
            model,h=checked_model(algo,group,digest)
            special[(algo,group)]=model;source_hashes[f'{algo}/{group}']=h
            thresholds[(algo,group)]=checked_thresholds(algo,group,digest,len(Xs),len(Xe))
    if args.solo_verificar:
        print('OK: seis modelos C3 verificados, políticas completas, partición de Validation compatible, Test excluido.')
        return
    print('Entrenando referente global exclusivamente sobre Train...',flush=True)
    global_model=make_pipeline(GLOBAL_CONFIG)
    global_model.fit(Xt,yt)
    pg_s=positive_prob(global_model,Xs); pg_e=positive_prob(global_model,Xe)
    global_thresholds={}
    for policy in POLICIES:
        decision,_=select_threshold(ys,pg_s,policy)
        if decision['threshold'] is None: raise ValueError(f'Global: {policy} sin umbral factible')
        global_thresholds[policy]=float(decision['threshold'])
    print('Calculando probabilidades especializadas y métricas...',flush=True)
    # Asignación sin reutilizar filas entre grupos; no se entrena ni se escoge sobre evaluación.
    age_e=age_group(Xe['age_years'])
    cache={}
    for algo in ('xgboost','gradient_boosting'):
        for group in GROUPS:
            mask=age_e==group
            cache[(algo,group)]=(mask,positive_prob(special[(algo,group)],Xe.loc[mask]))
    rows=[];predrows=[]
    cases=[('global_train_only','referencia_038',{'todos':OFFICIAL_THRESHOLD}),
           *[( 'global_train_only',policy,{'todos':v}) for policy,v in global_thresholds.items()]]
    for config,policy,tt in cases:
        t=tt['todos']; rows.append(summarize(ye,pg_e,t,config,policy,'todos'))
        for group in GROUPS:
            m=age_e==group;rows.append(summarize(ye.loc[m],pg_e[m],t,config,policy,group))
        for idx,truth,age,p in zip(Xe.index,ye,age_e,pg_e):
            predrows.append(dict(index=idx,y=int(truth),group=age,configuration=config,policy=policy,probability=float(p),threshold=t,predicted=int(p>=t)))
    for algo in ('xgboost','gradient_boosting'):
        for policy in POLICIES:
            ps=pd.Series(index=Xe.index,dtype=float);ts=pd.Series(index=Xe.index,dtype=float)
            for group in GROUPS:
                mask,pr=cache[(algo,group)];t=thresholds[(algo,group)][policy]
                ps.loc[Xe.index[mask]]=pr;ts.loc[Xe.index[mask]]=t
                rows.append(summarize(ye.loc[mask],pr,t,f'especializado_{algo}',policy,group))
            if ps.isna().any() or ts.isna().any():raise ValueError('Predicciones especializadas incompletas')
            # para agregado los umbrales son individuales; no reutilizar summarize con uno solo.
            truth=ye.to_numpy(dtype=int); pp=ps.to_numpy(dtype=float); tt=ts.to_numpy(dtype=float)
            pred=(pp>=tt).astype(int)
            tp=int(np.sum((truth==1)&(pred==1))); fn=int(np.sum((truth==1)&(pred==0)))
            tn=int(np.sum((truth==0)&(pred==0))); fp=int(np.sum((truth==0)&(pred==1)))
            from sklearn.metrics import precision_score,f1_score,accuracy_score
            recall=tp/(tp+fn);spec=tn/(tn+fp)
            rows.append(dict(configuration=f'especializado_{algo}',policy=policy,group='todos',threshold=np.nan,
                n=len(truth),tp=tp,tn=tn,fp=fp,fn=fn,recall=recall,specificity=spec,balanced_accuracy=(recall+spec)/2,
                precision=float(precision_score(truth,pred,zero_division=0)),npv=tn/(tn+fn) if tn+fn else np.nan,
                f1=float(f1_score(truth,pred,zero_division=0)),accuracy=float(accuracy_score(truth,pred)),
                roc_auc=float(roc_auc_score(truth,pp)),pr_auc=float(average_precision_score(truth,pp)),
                brier=float(brier_score_loss(truth,pp))))
            for idx,truth_i,age,p,t in zip(Xe.index,truth,age_e,pp,tt):
                predrows.append(dict(index=idx,y=int(truth_i),group=age,configuration=f'especializado_{algo}',
                    policy=policy,probability=float(p),threshold=float(t),predicted=int(p>=t)))
    results=pd.DataFrame(rows)
    # Diferencias pareadas, contra global con misma política, referidas al mismo conjunto de evaluación.
    pairs=[]
    for policy in POLICIES:
        base=results[(results.configuration=='global_train_only')&(results.policy==policy)]
        for config in ('especializado_xgboost','especializado_gradient_boosting'):
            comp=results[(results.configuration==config)&(results.policy==policy)]
            for group in (*GROUPS,'todos'):
                b=base[base.group==group].iloc[0]; c=comp[comp.group==group].iloc[0]
                pairs.append(dict(policy=policy,configuration=config,group=group,
                    delta_recall=c.recall-b.recall,delta_specificity=c.specificity-b.specificity,
                    delta_balanced_accuracy=c.balanced_accuracy-b.balanced_accuracy,
                    delta_roc_auc=c.roc_auc-b.roc_auc,delta_brier=c.brier-b.brier,
                    delta_fp=int(c.fp-b.fp),delta_fn=int(c.fn-b.fn)))
    OUT.mkdir(parents=True,exist_ok=False)
    results.to_csv(OUT/'metricas_comparadas.csv',index=False)
    pd.DataFrame(pairs).to_csv(OUT/'diferencias_pareadas_puntuales.csv',index=False)
    pd.DataFrame(predrows).to_csv(OUT/'predicciones_pareadas.csv',index=False)
    pd.DataFrame([{'policy':k,'threshold':v} for k,v in global_thresholds.items()]).to_csv(OUT/'umbrales_globales.csv',index=False)
    provenance=dict(analysis='C5 global-vs-specialized exploratory',date_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=git_commit(),seed=SEED,dataset_sha256=digest,train_n=len(Xt),validation_n=len(Xv),
        selection_n=len(Xs),evaluation_n=len(Xe),test_used=False,
        global_model='XGBoost v1 hyperparameters trained exclusively on original Train',
        global_threshold_reference=OFFICIAL_THRESHOLD,global_threshold_policies=global_thresholds,
        c3_model_sha256=source_hashes,
        note='Validation revisitada múltiples veces; diferencias exploratorias. Referencia 0.38 no es umbral óptimo. '
             'No se utiliza el artefacto oficial ajustado sobre Train+Validation. '
             'Comparar políticas iguales; las probabilidades de diferentes modelos no están calibradas de forma equivalente necesariamente. '
             'No usar Test de PULSO como confirmatorio si ya fue consultado para decisiones previas.')
    (OUT/'protocolo.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI','sqlite:///mlflow.db'))
    mlflow.set_experiment('PULSO-C5-Global-vs-Age')
    with mlflow.start_run(run_name='global_train_only_vs_age_C3') as r:
        mlflow.log_params(dict(dataset_sha256=digest,git_commit=provenance['git_commit'],seed=SEED,
                               test_used=False,train_n=len(Xt),selection_n=len(Xs),evaluation_n=len(Xe)))
        for _,rr in results[results.group=='todos'].iterrows():
            mlflow.log_metric(f"{rr.configuration}_{rr.policy}_recall",float(rr.recall))
            mlflow.log_metric(f"{rr.configuration}_{rr.policy}_balanced_accuracy",float(rr.balanced_accuracy))
        provenance['mlflow_run_id']=r.info.run_id
        (OUT/'protocolo.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
        mlflow.log_artifacts(str(OUT),artifact_path='c5_results')
    print(results[results.group=='todos'][['configuration','policy','recall','specificity','balanced_accuracy','roc_auc','fp','fn']].to_string(index=False))
    print(f'\nResultados C5: {OUT}')

if __name__=='__main__': main()
