import pytest
from pydantic import ValidationError

from backend.app.interfaces.http.schemas import RagResponse, UserData

from conftest import PROFILE, PROFILE_PAYLOAD, REPORT


def test_user_data_rejects_invalid_blood_pressure():
    with pytest.raises(ValidationError, match="ap_hi debe ser mayor que ap_lo"):
        UserData(**{**PROFILE_PAYLOAD, "ap_hi": 80, "ap_lo": 90})


def test_user_data_rejects_inconsistent_bmi():
    with pytest.raises(ValidationError, match="bmi no coincide"):
        UserData(**{**PROFILE_PAYLOAD, "bmi": 40})


def test_user_data_converts_to_domain_profile():
    result = UserData(**PROFILE_PAYLOAD).to_domain()

    assert result.bmi == pytest.approx(
        PROFILE.weight / ((PROFILE.height / 100) ** 2)
    )

    assert result.gender == PROFILE.gender
    assert result.height == PROFILE.height
    assert result.weight == PROFILE.weight
    assert result.ap_hi == PROFILE.ap_hi
    assert result.ap_lo == PROFILE.ap_lo
    assert result.smoke == PROFILE.smoke
    assert result.alco == PROFILE.alco
    assert result.active == PROFILE.active
    assert result.age_years == PROFILE.age_years


def test_rag_response_keeps_the_frontend_contract():
    body = RagResponse.from_domain(REPORT).model_dump(by_alias=True)

    source = body["recommendations"][0]["sources"][0]
    assert source["lines"] == {"from": 20, "to": 26}
    assert body["recommendations"][0]["source_ids"] == ["SOURCE_1"]


def test_user_data_calculates_bmi_when_omitted():
    payload = PROFILE_PAYLOAD.copy()
    payload.pop("bmi", None)

    result = UserData(**payload).to_domain()

    assert result.bmi == pytest.approx(
        payload["weight"] / ((payload["height"] / 100) ** 2)
    )


def test_user_data_rejects_inconsistent_bmi():
    payload = PROFILE_PAYLOAD.copy()
    payload["bmi"] = 40.0

    with pytest.raises(ValidationError):
        UserData(**payload)
