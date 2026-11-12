"""Adaptador HTTP del workflow RAG de n8n (implementa el puerto RecommendationGenerator)."""

from __future__ import annotations

from dataclasses import asdict
from typing import Optional

import httpx
from pydantic import BaseModel, Field

from ..domain.entities import (
    AnalysisContext,
    DocumentSource,
    Recommendation,
    RecommendationReport,
    SourceLines,
)
from ..domain.errors import RecommendationServiceError


# Contrato de respuesta del workflow RAG
class _SourceLinesContract(BaseModel):
    from_: int = Field(..., alias="from")
    to: int


class _SourceContract(BaseModel):
    source_id: str
    source: str
    score: float
    lines: _SourceLinesContract


class _RecommendationContract(BaseModel):
    factor: str
    recommendation: str
    source_ids: list[str] = Field(default_factory=list)
    sources: list[_SourceContract] = Field(default_factory=list)


class _ReportContract(BaseModel):
    summary: str
    recommendations: list[_RecommendationContract] = Field(default_factory=list)
    considerations: str
    note: str
    insufficient_information: bool


class N8nRecommendationClient:
    def __init__(
        self,
        url: str,
        timeout_seconds: float,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ):
        self._url = url
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def generate(self, context: AnalysisContext) -> RecommendationReport:
        if not self._url:
            raise RecommendationServiceError("RAG_SERVICE_URL no está configurado.")

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.post(self._url, json=_request_payload(context))
        except httpx.RequestError as exc:
            raise RecommendationServiceError(
                "No fue posible comunicarse con el servicio RAG."
            ) from exc

        if response.status_code >= 400:
            raise RecommendationServiceError(
                f"El servicio RAG respondió con HTTP {response.status_code}."
            )

        try:
            response_data = response.json()
        except Exception as exc:
            raise RecommendationServiceError(
                "El servicio RAG devolvió una respuesta que no es JSON válido."
            ) from exc

        if not isinstance(response_data, dict):
            raise RecommendationServiceError(
                "La respuesta del servicio RAG debe ser un objeto JSON."
            )

        try:
            report = _ReportContract.model_validate(response_data)
        except Exception as exc:
            raise RecommendationServiceError(
                "La respuesta del servicio RAG no cumple el contrato esperado."
            ) from exc

        return _to_domain(report)


def _request_payload(context: AnalysisContext) -> dict:
    """Mismo cuerpo que espera el workflow de n8n: prediction, user_data y shap."""
    return {
        "prediction": asdict(context.prediction),
        "user_data": context.profile.as_dict(),
        "shap": {
            "top_factors": [asdict(factor) for factor in context.explanation.top_factors]
        },
    }


def _to_domain(report: _ReportContract) -> RecommendationReport:
    return RecommendationReport(
        summary=report.summary,
        considerations=report.considerations,
        note=report.note,
        insufficient_information=report.insufficient_information,
        recommendations=tuple(
            Recommendation(
                factor=item.factor,
                recommendation=item.recommendation,
                source_ids=tuple(item.source_ids),
                sources=tuple(
                    DocumentSource(
                        source_id=source.source_id,
                        source=source.source,
                        score=source.score,
                        lines=SourceLines(start=source.lines.from_, end=source.lines.to),
                    )
                    for source in item.sources
                ),
            )
            for item in report.recommendations
        ),
    )
