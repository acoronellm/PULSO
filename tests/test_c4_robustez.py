import numpy as np
from experiments.age_specialized_models.c4.motor import ci_wilson,bootstrap_paired,threshold_map

def test_wilson_bounds():
    lo,hi=ci_wilson(8,10)
    assert 0<=lo<=.8<=hi<=1

def test_bootstrap_identity():
    y=np.array([0,1]*30)
    p=np.array([.1,.9]*30)
    out=bootstrap_paired(y,p,p,.5,.5,n=25)
    assert (out.abs().max()<1e-12).all()

def test_policy_names():
    import pandas as pd
    f=pd.DataFrame({'policy':['recall80','balanced_accuracy','minimax','weighted_60_40'],
                    'threshold':[.2,.3,.4,.5]})
    assert len(threshold_map(f))==4
