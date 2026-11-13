"""Contratos JSON de la API de PULSO y su conversión desde y hacia el dominio.

Los nombres y validaciones son los mismos que usa el frontend; las reglas de
coherencia del perfil se delegan en el dominio.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from ...application.use_cases.analyze_profile import AnalysisResult
from ...application.use_cases.list_analysis_history import AnalysisHistoryPage
from ...domain import rules
from ...domain.entities import (
    CardiovascularProfile,
    AnalysisHistoryEntry,
    Explanation,
    Prediction,
    RecommendationReport,
    ScenarioChanges,
    SimulationOutcome,
)
from ...domain.errors import InvalidProfileError


def _apply_rule(rule, *args) -> None:
    """Convierte una regla del dominio en un error de validación de Pydantic (HTTP 422)."""
    try:
        rule(*args)
    except InvalidProfileError as exc:
        raise ValueError(str(exc)) from exc


class PredictionData(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    classification: int = Field(..., ge=0, le=1)
    threshold: float = Field(..., ge=0, le=1)
    model_version: str

    @classmethod
    def from_domain(cls, prediction: Prediction) -> PredictionData:
        return cls(**asdict(prediction))


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
    bmi: float | None = Field(default=None, gt=0)


    @model_validator(mode="after")
    def validate_consistency(self):
        calculated_bmi = rules.expected_bmi(self.weight, self.height)

        if self.bmi is not None:
            _apply_rule(
                rules.validate_bmi,
                self.bmi,
                self.weight,
                self.height,
            )

        self.bmi = calculated_bmi

        _apply_rule(
            rules.validate_profile,
            self.ap_hi,
            self.ap_lo,
            self.bmi,
            self.weight,
            self.height,
        )
        return self


    def to_domain(self) -> CardiovascularProfile:
        return CardiovascularProfile(**self.model_dump())


class ShapFactor(BaseModel):
    feature: str
    value: float
    shap_value: float
    direction: Literal["increase", "decrease"]


class ShapData(BaseModel):
    top_factors: list[ShapFactor]

    @classmethod
    def from_domain(cls, explanation: Explanation) -> ShapData:
        return cls(top_factors=[asdict(factor) for factor in explanation.top_factors])


class AnalysisResponse(BaseModel):
    analysis_id: UUID
    prediction: PredictionData
    shap: ShapData

    @classmethod
    def from_domain(cls, result: AnalysisResult) -> AnalysisResponse:
        return cls(
            analysis_id=result.analysis_id,
            prediction=PredictionData.from_domain(result.prediction),
            shap=ShapData.from_domain(result.explanation),
        )


class AnalysisHistoryItem(BaseModel):
    analysis_id: UUID
    created_at: datetime
    prediction: PredictionData

    @classmethod
    def from_domain(cls, entry: AnalysisHistoryEntry) -> AnalysisHistoryItem:
        return cls(
            analysis_id=entry.analysis_id,
            created_at=entry.created_at,
            prediction=PredictionData(
                probability=entry.probability,
                classification=entry.classification,
                threshold=entry.threshold,
                model_version=entry.model_version,
            ),
        )


class AnalysisHistoryResponse(BaseModel):
    items: list[AnalysisHistoryItem]
    limit: int
    offset: int
    has_more: bool

    @classmethod
    def from_domain(cls, page: AnalysisHistoryPage) -> AnalysisHistoryResponse:
        return cls(
            items=[AnalysisHistoryItem.from_domain(entry) for entry in page.items],
            limit=page.limit,
            offset=page.offset,
            has_more=page.has_more,
        )


# -------------------------
# Recomendaciones (RAG)
# -------------------------

class RagRequest(BaseModel):
    analysis_id: UUID


class RagSourceLines(BaseModel):
    from_: int = Field(..., alias="from")
    to: int

    model_config = {"populate_by_name": True}


class RagSource(BaseModel):
    source_id: str
    source: str
    score: float
    lines: RagSourceLines


class RagRecommendation(BaseModel):
    factor: str
    recommendation: str
    source_ids: list[str] = Field(default_factory=list)
    sources: list[RagSource] = Field(default_factory=list)


class RagResponse(BaseModel):
    summary: str
    recommendations: list[RagRecommendation] = Field(default_factory=list)
    considerations: str
    note: str
    insufficient_information: bool

    @classmethod
    def from_domain(cls, report: RecommendationReport) -> RagResponse:
        return cls(
            summary=report.summary,
            considerations=report.considerations,
            note=report.note,
            insufficient_information=report.insufficient_information,
            recommendations=[
                RagRecommendation(
                    factor=item.factor,
                    recommendation=item.recommendation,
                    source_ids=list(item.source_ids),
                    sources=[
                        RagSource(
                            source_id=source.source_id,
                            source=source.source,
                            score=source.score,
                            lines=RagSourceLines(from_=source.lines.start, to=source.lines.end),
                        )
                        for source in item.sources
                    ],
                )
                for item in report.recommendations
            ],
        )


# -------------------------
# Simulación
# -------------------------

class SimulationChanges(BaseModel):
    weight: float | None = Field(default=None, ge=30, le=200)
    ap_hi: float | None = Field(default=None, ge=70, le=250)
    ap_lo: float | None = Field(default=None, ge=40, le=150)
    smoke: int | None = Field(default=None, ge=0, le=1)
    alco: int | None = Field(default=None, ge=0, le=1)
    active: int | None = Field(default=None, ge=0, le=1)

    def to_domain(self) -> ScenarioChanges:
        return ScenarioChanges(**self.model_dump())


class SimulationRequest(BaseModel):
    original: UserData
    changes: SimulationChanges

    @model_validator(mode="after")
    def validate_simulated_bmi(self):
        simulated_weight = (
            self.changes.weight
            if self.changes.weight is not None
            else self.original.weight
        )
        _apply_rule(rules.validate_simulated_weight, simulated_weight, self.original.height)
        return self


class SimulationResult(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    classification: int = Field(..., ge=0, le=1)


class SimulationResponse(BaseModel):
    original: SimulationResult
    simulated: SimulationResult
    probability_difference: float
    applied_changes: dict
    model_version: str
    threshold: float = Field(..., ge=0, le=1)

    @classmethod
    def from_domain(cls, outcome: SimulationOutcome) -> SimulationResponse:
        return cls(
            original=SimulationResult(**asdict(outcome.original)),
            simulated=SimulationResult(**asdict(outcome.simulated)),
            probability_difference=outcome.probability_difference,
            applied_changes=dict(outcome.applied_changes),
            model_version=outcome.model_version,
            threshold=outcome.threshold,
        )
