"""C4.3: comparaciones contrafactuales locales a 50 y 60 años; no causal."""
import argparse
import numpy as np
import pandas as pd
from .motor import (OUT,POLICIES,data_validation,model_and_protocol,
                    c3_thresholds,threshold_map,positive_prob,save)

def run(window=1.0,epsilon=.01):
    Xv,yv,_,_=data_validation(); rows=[]; details=[]
    for cut,left,right in [(50,'menor_50','50_59'),(60,'50_59','60_64')]:
        # Misma población de perfiles próximos al corte. Cambiar edad es una simulación
        # estadística aislada: no reproduce el envejecimiento ni efectos clínicos.
        near=Xv.loc[(Xv['age_years']>=cut-window)&(Xv['age_years']<=cut+window)].copy()
        if near.empty: continue
        before=near.copy();after=near.copy()
        before['age_years']=cut-epsilon;after['age_years']=cut+epsilon
        for algo in ('xgboost','gradient_boosting'):
            ml,_,_=model_and_protocol(algo,left);mr,_,_=model_and_protocol(algo,right)
            tl=threshold_map(c3_thresholds(algo,left)[0]);tr=threshold_map(c3_thresholds(algo,right)[0])
            pb=positive_prob(ml,before);pa=positive_prob(mr,after)
            for policy in POLICIES:
                yb=(pb>=tl[policy]);ya=(pa>=tr[policy]);changed=(yb!=ya)
                rows.append({'boundary':cut,'algorithm':algo,'policy':policy,'n':len(near),
                             'window_years':window,'epsilon_years':epsilon,
                             'mean_abs_probability_jump':float(np.mean(np.abs(pa-pb))),
                             'median_abs_probability_jump':float(np.median(np.abs(pa-pb))),
                             'p95_abs_probability_jump':float(np.quantile(np.abs(pa-pb),.95)),
                             'classification_switch_rate':float(changed.mean()),
                             'switches':int(changed.sum()),
                             'threshold_left':tl[policy],'threshold_right':tr[policy]})
                for k,index in enumerate(near.index):
                    details.append({'boundary':cut,'algorithm':algo,'policy':policy,
                                    'record_index':index,'age_original':near.loc[index,'age_years'],
                                    'p_left':pb[k],'p_right':pa[k],
                                    'class_left':int(yb[k]),'class_right':int(ya[k])})
    save(OUT/'continuidad',{'resumen_continuidad.csv':pd.DataFrame(rows),
                           'detalle_contrafactual.csv':pd.DataFrame(details)},
         {'analysis':'C4 age boundary continuity','window_years':window,
          'epsilon_years':epsilon,'notes':'Perfiles cercanos al corte, edad modificada artificialmente y cambio de modelo. No predice evolución real ni permite inferencia causal.'})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--ventana',type=float,default=1.0)
    ap.add_argument('--epsilon',type=float,default=.01)
    args=ap.parse_args();run(args.ventana,args.epsilon)
