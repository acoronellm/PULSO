"""Adaptador HTTP del ML Service (implementa el puerto CardiovascularModel)."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Literal, Optional

import httpx
from pydantic import BaseModel, Field

from ..domain.entities import (
    CardiovascularProfile,
    Explanation,
    Prediction,
    ScenarioChanges,
    ScenarioResult,
    ShapFactor,
    SimulationOutcome,
)
from ..domain.errors import InvalidScenarioError, ModelServiceError


# Contratos de respuesta del ML Service
class _PredictionContract(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    classification: int = Field(..., ge=0, le=1)
    threshold: float = Field(..., ge=0, le=1)
    model_version: str


class _ShapFactorContract(BaseModel):
    feature: str
    value: float
    shap_value: float
    direction: Literal["increase", "decrease"]


class _ExplanationContract(BaseModel):
    top_factors: list[_ShapFactorContract]


class _ScenarioResultContract(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    classification: int = Field(..., ge=0, le=1)


class _SimulationContract(BaseModel):
    original: _ScenarioResultContract
    simulated: _ScenarioResultContract
    probability_difference: float
    applied_changes: dict
    model_version: str
    threshold: float = Field(..., ge=0, le=1)


class MLServiceClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def predict(self, profile: CardiovascularProfile) -> Prediction:
        response = await self._post(
            "/predict",
            profile.as_dict(),
            unavailable_message="No fue posible comunicarse con el ML Service.",
        )
        self._raise_for_status(response, "")
        data = self._parse(
            response,
            _PredictionContract,
            "La respuesta de predicción no cumple el contrato esperado.",
        )
        return Prediction(**data.model_dump())

    async def explain(self, profile: CardiovascularProfile) -> Explanation:
        response = await self._post(
            "/explain",
            profile.as_dict(),
            unavailable_message="No fue posible obtener la explicación del ML Service.",
        )
        self._raise_for_status(response, " al generar SHAP")
        data = self._parse(
            response,
            _ExplanationContract,
            "La explicación SHAP no cumple el contrato esperado.",
        )
        return Explanation(
            top_factors=tuple(
                ShapFactor(**factor.model_dump()) for factor in data.top_factors
            )
        )

    async def simulate(
        self,
        profile: CardiovascularProfile,
        changes: ScenarioChanges,
    ) -> SimulationOutcome:
        response = await self._post(
            "/simulate",
            {"original": profile.as_dict(), "changes": asdict(changes)},
            unavailable_message="No fue posible ejecutar la simulación en el ML Service.",
        )
        if response.status_code == 422:
            raise InvalidScenarioError("El escenario de simulación no es válido.")
        self._raise_for_status(response, " al simular")
        data = self._parse(
            response,
            _SimulationContract,
            "La respuesta de simulación no cumple el contrato esperado.",
        )
        return SimulationOutcome(
            original=ScenarioResult(**data.original.model_dump()),
            simulated=ScenarioResult(**data.simulated.model_dump()),
            probability_difference=data.probability_difference,
            model_version=data.model_version,
            threshold=data.threshold,
            applied_changes=data.applied_changes,
        )

    async def _post(
        self,
        path: str,
        payload: dict[str, Any],
        unavailable_message: str,
    ) -> httpx.Response:
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_seconds,
                transport=self._transport,
            ) as client:
                return await client.post(f"{self._base_url}{path}", json=payload)
        except httpx.RequestError as exc:
            raise ModelServiceError(unavailable_message) from exc

    @staticmethod
    def _raise_for_status(response: httpx.Response, action: str) -> None:
        if response.status_code >= 400:
            raise ModelServiceError(
                f"El ML Service respondió con HTTP {response.status_code}{action}."
            )

    @staticmethod
    def _parse(response: httpx.Response, contract: type[BaseModel], message: str):
        try:
            return contract.model_validate(response.json())
        except Exception as exc:
            raise ModelServiceError(message) from exc
