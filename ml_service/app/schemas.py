from pydantic import BaseModel, Field, model_validator
from typing import Literal
from typing import Optional


class PredictionRequest(BaseModel):
    gender: int = Field(..., ge=1, le=2)
    height: float = Field(..., ge=120, le=220)
    weight: float = Field(..., ge=30, le=200)
    ap_hi: float = Field(..., ge=70, le=250)
    ap_lo: float = Field(..., ge=40, le=150)
    smoke: int = Field(..., ge=0, le=1)
    alco: int = Field(..., ge=0, le=1)
    active: int = Field(..., ge=0, le=1)
    age_years: float = Field(..., gt=0)
    bmi: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_blood_pressure(self):
        if self.ap_hi <= self.ap_lo:
            raise ValueError(
                "ap_hi debe ser mayor que ap_lo."
            )

        return self


class PredictionResponse(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    classification: int = Field(..., ge=0, le=1)
    threshold: float = Field(..., ge=0, le=1)
    model_version: str

class ShapFactor(BaseModel):
    feature: str
    value: float
    shap_value: float
    direction: Literal[
        "increase",
        "decrease",
    ]


class ExplanationResponse(BaseModel):
    top_factors: list[ShapFactor]   

class SimulationChanges(BaseModel):
    weight: Optional[float] = Field(
        default=None,
        ge=30,
        le=200,
    )

    ap_hi: Optional[float] = Field(
        default=None,
        ge=70,
        le=250,
    )

    ap_lo: Optional[float] = Field(
        default=None,
        ge=40,
        le=150,
    )

    smoke: Optional[int] = Field(
        default=None,
        ge=0,
        le=1,
    )

    alco: Optional[int] = Field(
        default=None,
        ge=0,
        le=1,
    )

    active: Optional[int] = Field(
        default=None,
        ge=0,
        le=1,
    )


class SimulationRequest(BaseModel):
    original: PredictionRequest
    changes: SimulationChanges


class SimulationResult(BaseModel):
    probability: float = Field(
        ...,
        ge=0,
        le=1,
    )

    classification: int = Field(
        ...,
        ge=0,
        le=1,
    )


class SimulationResponse(BaseModel):
    original: SimulationResult
    simulated: SimulationResult
    probability_difference: float
    applied_changes: dict
    model_version: str
    threshold: float