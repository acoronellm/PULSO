"""Traducción de los errores del dominio a respuestas HTTP."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ...domain.errors import (
    AnalysisNotFoundError,
    ExternalServiceError,
    InvalidProfileError,
    InvalidScenarioError,
)


async def _analysis_not_found(_: Request, __: AnalysisNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "El análisis no existe o ya expiró."})


async def _invalid_input(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def _external_service(_: Request, exc: ExternalServiceError) -> JSONResponse:
    # Una dependencia (ML Service o RAG) falló: el backend actúa como gateway
    return JSONResponse(status_code=502, content={"detail": str(exc)})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AnalysisNotFoundError, _analysis_not_found)
    app.add_exception_handler(InvalidProfileError, _invalid_input)
    app.add_exception_handler(InvalidScenarioError, _invalid_input)
    app.add_exception_handler(ExternalServiceError, _external_service)
