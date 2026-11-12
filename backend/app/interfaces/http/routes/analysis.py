"""Rutas de análisis: solo traducen HTTP a casos de uso.

Los errores del dominio se convierten en 404, 422 o 502 en interfaces/http/errors.py.
"""

from fastapi import APIRouter, Depends

from ....application.use_cases.analyze_profile import AnalyzeProfile
from ....application.use_cases.request_recommendations import RequestRecommendations
from ....application.use_cases.simulate_scenario import SimulateScenario
from ..dependencies import (
    get_analyze_profile,
    get_request_recommendations,
    get_simulate_scenario,
)
from ..schemas import (
    AnalysisResponse,
    RagRequest,
    RagResponse,
    SimulationRequest,
    SimulationResponse,
    UserData,
)

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    user_data: UserData,
    use_case: AnalyzeProfile = Depends(get_analyze_profile),
) -> AnalysisResponse:
    result = await use_case.execute(user_data.to_domain())
    return AnalysisResponse.from_domain(result)


@router.post("/rag", response_model=RagResponse)
async def rag_analysis(
    payload: RagRequest,
    use_case: RequestRecommendations = Depends(get_request_recommendations),
) -> RagResponse:
    report = await use_case.execute(payload.analysis_id)
    return RagResponse.from_domain(report)


@router.post("/simulate", response_model=SimulationResponse)
async def simulate(
    payload: SimulationRequest,
    use_case: SimulateScenario = Depends(get_simulate_scenario),
) -> SimulationResponse:
    outcome = await use_case.execute(
        payload.original.to_domain(),
        payload.changes.to_domain(),
    )
    return SimulationResponse.from_domain(outcome)
