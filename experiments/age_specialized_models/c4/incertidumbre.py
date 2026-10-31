"""C4.1: intervalos Wilson y bootstrap pareado XGB vs GB; solo Validation."""
import argparse
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from .motor import (GROUPS,POLICIES,OUT,data_validation,get_group_arrays,
                    model_and_protocol,c3_thresholds,threshold_map,positive_prob,
                    metrics,ci_wilson,bootstrap_paired,save)

def run(reps=1000):
    Xv,yv,_,ei=data_validation(); rows=[]; comparisons=[]
    for group in GROUPS:
        Xg,yg=get_group_arrays(Xv,yv,ei,group); predictions={}; thresholds={}; hashes={}
        for algo in ('xgboost','gradient_boosting'):
            model,man,h=model_and_protocol(algo,group); th,_=c3_thresholds(algo,group)
            p=positive_prob(model,Xg); predictions[algo]=p;thresholds[algo]=threshold_map(th);hashes[algo]=h
            for policy,t in thresholds[algo].items():
                m=metrics(yg,p,t); rec_ci=ci_wilson(m['tp'],m['tp']+m['fn'])
                spec_ci=ci_wilson(m['tn'],m['tn']+m['fp'])
                rows.append({'algorithm':algo,'group':group,'policy':policy,'threshold':t,
                             **m,'recall_ci_low':rec_ci[0],'recall_ci_high':rec_ci[1],
                             'specificity_ci_low':spec_ci[0],'specificity_ci_high':spec_ci[1],
                             'roc_auc':roc_auc_score(yg,p)})
        for policy in POLICIES:
            a='xgboost';b='gradient_boosting'
            boot=bootstrap_paired(yg,predictions[a],predictions[b],thresholds[a][policy],thresholds[b][policy],n=reps)
            point_a=metrics(yg,predictions[a],thresholds[a][policy]);point_b=metrics(yg,predictions[b],thresholds[b][policy])
            record={'group':group,'policy':policy,'n_boot':len(boot)}
            for key in ('recall','specificity','balanced_accuracy'):
                col='delta_ba' if key=='balanced_accuracy' else 'delta_'+key
                record[f'{col}_xgb_minus_gb']=point_a[key]-point_b[key]
                record[f'{col}_ci_low']=boot[col].quantile(.025)
                record[f'{col}_ci_high']=boot[col].quantile(.975)
            col='delta_roc_auc';record[col+'_xgb_minus_gb']=roc_auc_score(yg,predictions[a])-roc_auc_score(yg,predictions[b])
            record[col+'_ci_low']=boot[col].quantile(.025);record[col+'_ci_high']=boot[col].quantile(.975)
            comparisons.append(record)
    save(OUT/'incertidumbre',{'metricas_wilson.csv':pd.DataFrame(rows),
                             'diferencias_pareadas_bootstrap.csv':pd.DataFrame(comparisons)},
         {'analysis':'C4 uncertainty','bootstrap_iterations':reps,
          'notes':'Intervalos condicionales a modelos y políticas fijados; Validation reutilizada, resultados exploratorios; no corrección por comparaciones múltiples.'})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--bootstrap',type=int,default=1000)
    run(ap.parse_args().bootstrap)
