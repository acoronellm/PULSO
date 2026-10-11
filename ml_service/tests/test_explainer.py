import numpy as np

from ml_service.app.explainer import explain
from ml_service.app.schemas import PredictionRequest


class FakePreprocessor:
    def transform(self, X):
        return np.array([
            [
                1.0,
                172.0,
                88.0,
                150.0,
                92.0,
                1.0,
                0.0,
                0.0,
                61.0,
                29.75,
            ]
        ])

    def get_feature_names_out(self):
        return np.array([
            "gender",
            "height",
            "weight",
            "ap_hi",
            "ap_lo",
            "smoke",
            "alco",
            "active",
            "age_years",
            "bmi",
        ])


class FakePipeline:
    named_steps = {
        "preprocessor": FakePreprocessor(),
    }


class FakeExplanation:
    values = np.array([
        [
            0.05,   # gender
            0.02,   # height
            0.10,   # weight
            0.44,   # ap_hi
            0.03,   # ap_lo
            0.31,   # smoke
            -0.01,  # alco
            -0.19,  # active
            0.08,   # age_years
            0.04,   # bmi
        ]
    ])


class FakeExplainer:
    def __call__(self, X):
        return FakeExplanation()


def build_request():
    return PredictionRequest(
        gender=1,
        height=172,
        weight=88,
        ap_hi=150,
        ap_lo=92,
        smoke=1,
        alco=0,
        active=0,
        age_years=61,
        bmi=29.75,
    )


def test_explain_returns_top_three_factors(
    monkeypatch,
):
    monkeypatch.setattr(
        "ml_service.app.explainer.load_model",
        lambda: FakePipeline(),
    )

    monkeypatch.setattr(
        "ml_service.app.explainer.get_explainer",
        lambda: FakeExplainer(),
    )

    result = explain(
        build_request(),
        top_n=3,
    )

    assert len(result.top_factors) == 3

    assert [
        factor.feature
        for factor in result.top_factors
    ] == [
        "ap_hi",
        "smoke",
        "active",
    ]


def test_explain_orders_by_absolute_shap_value(
    monkeypatch,
):
    monkeypatch.setattr(
        "ml_service.app.explainer.load_model",
        lambda: FakePipeline(),
    )

    monkeypatch.setattr(
        "ml_service.app.explainer.get_explainer",
        lambda: FakeExplainer(),
    )

    result = explain(
        build_request(),
        top_n=3,
    )

    values = [
        abs(factor.shap_value)
        for factor in result.top_factors
    ]

    assert values == sorted(
        values,
        reverse=True,
    )


def test_explain_sets_direction_from_sign(
    monkeypatch,
):
    monkeypatch.setattr(
        "ml_service.app.explainer.load_model",
        lambda: FakePipeline(),
    )

    monkeypatch.setattr(
        "ml_service.app.explainer.get_explainer",
        lambda: FakeExplainer(),
    )

    result = explain(
        build_request(),
        top_n=3,
    )

    factors = {
        factor.feature: factor
        for factor in result.top_factors
    }

    assert (
        factors["ap_hi"].direction
        == "increase"
    )

    assert (
        factors["smoke"].direction
        == "increase"
    )

    assert (
        factors["active"].direction
        == "decrease"
    )