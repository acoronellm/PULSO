import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.metrics import brier_score_loss
from experiments.age_specialized_models.c3.motor import age_mask, get_prob, build_estimator, METODOS


def test_age_masks():
    age = np.array([49.999,50.0,59.999,60.0])
    assert age_mask(age,'menor_50').tolist()==[True,False,False,False]
    assert age_mask(age,'50_59').tolist()==[False,True,True,False]
    assert age_mask(age,'60_64').tolist()==[False,False,False,True]
    with pytest.raises(ValueError):
        age_mask(age,'global')


def test_methods_and_probability_contract():
    assert set(METODOS)=={'none','sigmoid','isotonic'}
    from sklearn.linear_model import LogisticRegression
    X, y = make_classification(n_samples=120,n_features=5,random_state=42)
    m=LogisticRegression(max_iter=1000).fit(X,y)
    p=get_prob(m,X)
    assert p.shape==(120,)
    assert np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
    assert np.isfinite(brier_score_loss(y,p))


def test_build_estimator_without_data():
    for metodo in METODOS:
        m=build_estimator('xgboost',{},metodo)
        assert hasattr(m,'fit') and hasattr(m,'predict_proba')
