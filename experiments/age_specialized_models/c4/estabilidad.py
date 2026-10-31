"""C4.2: 100 redistribuciones Validation con modelo fijo; sin Test."""
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from .motor import (GROUPS,POLICIES,OUT,data_validation,age_group,model_and_protocol,
                    positive_prob,select_threshold,metrics,save)

def run(reps=100):
    Xv,yv,_,_=data_validation()
    strata=pd.Series(age_group(Xv['age_years']),index=Xv.index).astype(str)+'_'+yv.astype(str)
    model_probs={}
    for group in GROUPS:
        m=age_group(Xv['age_years'])==group
        Xg=Xv.loc[m]
        for algo in ('xgboost','gradient_boosting'):
            model,_,_=model_and_protocol(algo,group)
            p=pd.Series(positive_prob(model,Xg),index=Xg.index)
            model_probs[(algo,group)]=p
    rows=[]
    for i in range(reps):
        si,ei=train_test_split(np.arange(len(Xv)),test_size=.5,random_state=42+i,stratify=strata)
        sel=Xv.iloc[si];ev=Xv.iloc[ei]
        for group in GROUPS:
            sm=age_group(sel['age_years'])==group;em=age_group(ev['age_years'])==group
            sy=yv.loc[sel.loc[sm].index];ey=yv.loc[ev.loc[em].index]
            for algo in ('xgboost','gradient_boosting'):
                probabilities=model_probs[(algo,group)]
                sp=probabilities.loc[sy.index].to_numpy();ep=probabilities.loc[ey.index].to_numpy()
                for pol in POLICIES:
                    s,_=select_threshold(sy,sp,pol)
                    row={'repetition':i,'algorithm':algo,'group':group,'policy':pol,
                         'status':s['status'],'threshold':s['threshold']}
                    if s['threshold'] is not None: row.update(metrics(ey,ep,s['threshold']))
                    rows.append(row)
    df=pd.DataFrame(rows)
    summary=df.groupby(['algorithm','group','policy']).agg(
        repetitions=('repetition','count'),feasible=('threshold','count'),
        threshold_median=('threshold','median'),threshold_p05=('threshold',lambda x:x.quantile(.05)),
        threshold_p95=('threshold',lambda x:x.quantile(.95)),
        recall_mean=('recall','mean'),specificity_mean=('specificity','mean'),
        ba_mean=('balanced_accuracy','mean'),fp_mean=('fp','mean'),fn_mean=('fn','mean')).reset_index()
    save(OUT/'estabilidad',{'repeticiones.csv':df,'resumen_estabilidad.csv':summary},
         {'analysis':'C4 threshold stability','repetitions':reps,'notes':
          'Mismo modelo, mismas observaciones redistribuidas; cuantiles NO son intervalos de confianza ni muestras independientes.'})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repeticiones',type=int,default=100)
    run(ap.parse_args().repeticiones)
