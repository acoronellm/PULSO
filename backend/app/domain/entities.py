"""Entidades del dominio de PULSO.

Son objetos inmutables de Python puro: no dependen de FastAPI, Pydantic
ni de los servicios externos. Las capas externas los traducen desde y
hacia sus propios formatos (JSON de la API, contratos del ML Service y n8n).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Optional
from uuid import UUID

ShapDirection = Literal["increase", "decrease"]


@dataclass(frozen=True)
class AuthUser:
    """Cuenta de usuario; las interfaces deben excluir el hash de la respuesta."""

    id: UUID
    email: str
    password_hash: str


@dataclass(frozen=True)
class CardiovascularProfile:
    """Perfil de entrada del modelo PULSO v1 (las 10 variables del modelo)."""

    gender: int
    height: float
    weight: float
    ap_hi: float
    ap_lo: float
    smoke: int
    alco: int
    active: int
    age_years: float
    bmi: float

    def as_dict(self) -> dict[str, float | int]:
        return {
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "ap_hi": self.ap_hi,
            "ap_lo": self.ap_lo,
            "smoke": self.smoke,
            "alco": self.alco,
            "active": self.active,
            "age_years": self.age_years,
            "bmi": self.bmi,
        }


@dataclass(frozen=True)
class Prediction:
    """Salida del clasificador XGBoost para la clase cardio = 1."""

    probability: float
    classification: int
    threshold: float
    model_version: str


@dataclass(frozen=True)
class ShapFactor:
    feature: str
    value: float
    shap_value: float
    direction: ShapDirection


@dataclass(frozen=True)
class Explanation:
    """Factores SHAP con mayor contribución a la salida del modelo."""

    top_factors: tuple[ShapFactor, ...] = ()


@dataclass(frozen=True)
class AnalysisContext:
    """Contexto guardado tras un análisis para pedir recomendaciones sin repetir la inferencia."""

    profile: CardiovascularProfile
    prediction: Prediction
    explanation: Explanation
    owner_id: UUID | None = None


@dataclass(frozen=True)
class SourceLines:
    start: int
    end: int


@dataclass(frozen=True)
class DocumentSource:
    """Fragmento documental recuperado por el módulo RAG."""

    source_id: str
    source: str
    score: float
    lines: SourceLines


@dataclass(frozen=True)
class Recommendation:
    factor: str
    recommendation: str
    source_ids: tuple[str, ...] = ()
    sources: tuple[DocumentSource, ...] = ()


@dataclass(frozen=True)
class RecommendationReport:
    """Recomendaciones educativas generadas por el módulo RAG."""

    summary: str
    considerations: str
    note: str
    insufficient_information: bool
    recommendations: tuple[Recommendation, ...] = ()


@dataclass(frozen=True)
class ScenarioChanges:
    """Variables del perfil que la simulación permite modificar."""

    weight: Optional[float] = None
    ap_hi: Optional[float] = None
    ap_lo: Optional[float] = None
    smoke: Optional[int] = None
    alco: Optional[int] = None
    active: Optional[int] = None

    def as_dict(self) -> dict[str, float | int]:
        """Solo los cambios indicados (sin los valores vacíos)."""
        values = {
            "weight": self.weight,
            "ap_hi": self.ap_hi,
            "ap_lo": self.ap_lo,
            "smoke": self.smoke,
            "alco": self.alco,
            "active": self.active,
        }
        return {name: value for name, value in values.items() if value is not None}


@dataclass(frozen=True)
class ScenarioResult:
    probability: float
    classification: int


@dataclass(frozen=True)
class SimulationOutcome:
    """Comparación entre el perfil original y el escenario hipotético."""

    original: ScenarioResult
    simulated: ScenarioResult
    probability_difference: float
    model_version: str
    threshold: float
    applied_changes: Mapping[str, Any] = field(default_factory=dict)
