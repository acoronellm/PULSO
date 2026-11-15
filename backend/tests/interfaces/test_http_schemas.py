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
    assert UserData(**PROFILE_PAYLOAD).to_domain() == PROFILE


def test_rag_response_keeps_the_frontend_contract():
    body = RagResponse.from_domain(REPORT).model_dump(by_alias=True)

    source = body["recommendations"][0]["sources"][0]
    assert source["lines"] == {"from": 20, "to": 26}
    assert body["recommendations"][0]["source_ids"] == ["SOURCE_1"]
