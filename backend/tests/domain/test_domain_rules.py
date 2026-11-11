import pytest

from backend.app.domain import rules
from backend.app.domain.entities import ScenarioChanges
from backend.app.domain.errors import InvalidProfileError


def test_profile_rejects_systolic_not_above_diastolic():
    with pytest.raises(InvalidProfileError, match="ap_hi debe ser mayor que ap_lo"):
        rules.validate_profile(ap_hi=80, ap_lo=90, bmi=29.75, weight=88, height_cm=172)


def test_profile_rejects_inconsistent_bmi():
    with pytest.raises(InvalidProfileError, match="bmi no coincide"):
        rules.validate_profile(ap_hi=150, ap_lo=92, bmi=40, weight=88, height_cm=172)


def test_profile_accepts_bmi_within_rounding_tolerance():
    rules.validate_profile(ap_hi=150, ap_lo=92, bmi=29.75, weight=88, height_cm=172)


def test_scenario_changes_only_include_given_values():
    assert ScenarioChanges(weight=80, smoke=0).as_dict() == {"weight": 80, "smoke": 0}
