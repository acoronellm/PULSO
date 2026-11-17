import pytest
from pydantic import ValidationError

from backend.app.interfaces.http.schemas import RagResponse, UserData, SimulationRequest

from conftest import PROFILE, PROFILE_PAYLOAD, REPORT

from dataclasses import replace

from backend.app.domain import rules

def test_user_data_rejects_invalid_blood_pressure():
    with pytest.raises(ValidationError, match="ap_hi debe ser mayor que ap_lo"):
        UserData(**{**PROFILE_PAYLOAD, "ap_hi": 80, "ap_lo": 90})


def test_user_data_rejects_inconsistent_bmi():
    with pytest.raises(ValidationError, match="bmi no coincide"):
        UserData(**{**PROFILE_PAYLOAD, "bmi": 40})

def test_user_data_calculates_bmi_when_omitted():
    payload = {
        key: value
        for key, value in PROFILE_PAYLOAD.items()
        if key != "bmi"
    }

    user_data = UserData(**payload)

    expected_bmi = rules.expected_bmi(
        PROFILE_PAYLOAD["weight"],
        PROFILE_PAYLOAD["height"],
    )

    assert user_data.bmi == pytest.approx(expected_bmi)
    assert user_data.to_domain().bmi == pytest.approx(expected_bmi)


def test_user_data_normalizes_consistent_bmi():
    user_data = UserData(**PROFILE_PAYLOAD)

    expected_bmi = rules.expected_bmi(
        PROFILE_PAYLOAD["weight"],
        PROFILE_PAYLOAD["height"],
    )

    assert user_data.bmi == pytest.approx(expected_bmi)

def test_user_data_converts_to_domain_profile():
    expected_bmi = rules.expected_bmi(
        PROFILE_PAYLOAD["weight"],
        PROFILE_PAYLOAD["height"],
    )

    expected_profile = replace(PROFILE, bmi=expected_bmi)

    assert UserData(**PROFILE_PAYLOAD).to_domain() == expected_profile

def test_rag_response_keeps_the_frontend_contract():
    body = RagResponse.from_domain(REPORT).model_dump(by_alias=True)

    source = body["recommendations"][0]["sources"][0]
    assert source["lines"] == {"from": 20, "to": 26}
    assert body["recommendations"][0]["source_ids"] == ["SOURCE_1"]


def test_simulation_rejects_inconsistent_blood_pressure():
    with pytest.raises(ValidationError, match="ap_hi debe ser mayor que ap_lo"):
        SimulationRequest(
            original=PROFILE_PAYLOAD,
            changes={"ap_hi": 80, "ap_lo": 90},
        )
