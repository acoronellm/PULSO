import numpy as np
import pandas as pd
from experiments.age_specialized_models.c5.comparar import split_validation, summarize, GLOBAL_CONFIG

def test_split_disjoint_and_stratified():
    age=np.array([45]*40+[55]*40+[62]*40,dtype=float)
    X=pd.DataFrame({'age_years':age},index=np.arange(300,420))
    y=pd.Series(np.tile([0,1],60),index=X.index)
    xs,ys,xe,ye=split_validation(X,y)
    assert not set(xs.index).intersection(xe.index)
    assert len(xs)==60 and len(xe)==60
    assert (ys.groupby(
    pd.cut(xs.age_years, [0, 50, 60, 100]),observed=False).size()>0).all()

def test_metrics_no_leakage():
    r=summarize([0,0,1,1],[.1,.9,.8,.2],.5,'global','prueba','todos')
    assert (r['tp'],r['tn'],r['fp'],r['fn'])==(1,1,1,1)
    assert abs(r['balanced_accuracy']-.5)<1e-12

def test_global_config_v1():
    assert GLOBAL_CONFIG['model_type']=='xgboost'
    assert GLOBAL_CONFIG['model_params']['n_estimators']==300
