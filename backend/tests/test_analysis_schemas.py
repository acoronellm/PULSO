import pytest
from pydantic import ValidationError

from backend.app.schemas.analysis import UserData


def test_user_data_rejects_invalid_blood_pressure():
    with pytest.raises(
        ValidationError,
        match="ap_hi debe ser mayor que ap_lo",
    ):
        UserData(
            gender=1,
            height=172,
            weight=88,
            ap_hi=80,
            ap_lo=90,
            smoke=1,
            alco=0,
            active=0,
            age_years=61,
            bmi=29.75,
        )