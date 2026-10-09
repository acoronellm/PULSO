from typing import Literal

from pydantic import BaseModel, Field


class PredictionData(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    classification: int = Field(..., ge=0, le=1)
    threshold: float = Field(..., ge=0, le=1)
    model_version: str


class UserData(BaseModel):
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


class ShapFactor(BaseModel):
    feature: str
    value: float
    shap_value: float
    direction: Literal["increase", "decrease"]


class ShapData(BaseModel):
    top_factors: list[ShapFactor]


class RagRequest(BaseModel):
    prediction: PredictionData
    user_data: UserData
    shap: ShapData


class RagSourceLines(BaseModel):
    from_: int = Field(..., alias="from")
    to: int

    model_config = {
        "populate_by_name": True
    }


class RagSource(BaseModel):
    source_id: str
    source: str
    score: float
    lines: RagSourceLines


class RagRecommendation(BaseModel):
    factor: str
    recommendation: str

    source_ids: list[str] = Field(
        default_factory=list
    )

    sources: list[RagSource] = Field(
        default_factory=list
    )


class RagResponse(BaseModel):
    summary: str

    recommendations: list[RagRecommendation] = Field(
        default_factory=list
    )

    considerations: str
    note: str
    insufficient_information: bool