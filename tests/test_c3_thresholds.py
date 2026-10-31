import numpy as np
import pytest
from experiments.age_specialized_models.c3.umbrales.motor_umbrales import (age_group, metrics, select_threshold, POLICIES, GRID)

def test_age_group_boundaries():
    assert age_group([49.99,50,59.99,60]).tolist()==['menor_50','50_59','50_59','60_64']

def test_four_policies_no_fixed_threshold():
    assert POLICIES==('recall80','balanced_accuracy','minimax','weighted_60_40')

def test_metrics_known_counts():
    m=metrics([0,0,1,1],[.1,.8,.9,.2],.5)
    assert (m['tp'],m['tn'],m['fp'],m['fn'])==(1,1,1,1)
    assert m['recall']==m['specificity']==.5

def test_select_threshold_deterministic():
    y=np.array([0,0,0,1,1,1]);p=np.array([.1,.2,.4,.6,.8,.9])
    for policy in POLICIES:
        a,_=select_threshold(y,p,policy);b,_=select_threshold(y,p,policy)
        assert a==b

def test_recall_requirement_and_no_feasible_grid():
    y=np.array([0,0,1,1]);p=np.array([.01,.02,.01,.02])
    sel,_=select_threshold(y,p,'recall80',grid=np.array([.5,.7]))
    assert sel['status']=='sin_umbral_factible'

def test_recall80_selection_constraint():
    y=np.array([0,0,1,1,1]);p=np.array([.1,.25,.3,.45,.8])
    selection,_=select_threshold(y,p,'recall80')
    assert selection['recall_selection']>=.8
