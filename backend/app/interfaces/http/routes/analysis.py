"""Rutas de análisis: solo traducen HTTP a casos de uso.

Los errores del dominio se convierten en 404, 422 o 502 en interfaces/http/errors.py.
"""

from fastapi import APIRouter, Depends, Query

from ....application.use_cases.analyze_profile import AnalyzeProfile
from ....application.use_cases.list_analysis_history import ListAnalysisHistory
from ....application.use_cases.request_recommendations import RequestRecommendations
from ....application.use_cases.simulate_scenario import SimulateScenario
from ....domain.entities import AuthUser
from ..dependencies import (
    get_analyze_profile,
    get_current_user,
    get_list_analysis_history,
    get_request_recommendations,
    get_simulate_scenario,
)
from ..schemas import (
    AnalysisResponse,
    AnalysisHistoryResponse,
    RagRequest,
    RagResponse,
    SimulationRequest,
    SimulationResponse,
    UserData,
)

router = APIRouter()


@router.get("/analyses", response_model=AnalysisHistoryResponse)
def list_analysis_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    use_case: ListAnalysisHistory = Depends(get_list_analysis_history),
    user: AuthUser = Depends(get_current_user),
) -> AnalysisHistoryResponse:
    page = use_case.execute(user.id, limit, offset)
    return AnalysisHistoryResponse.from_domain(page)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    user_data: UserData,
    use_case: AnalyzeProfile = Depends(get_analyze_profile),
    _user: AuthUser = Depends(get_current_user),
) -> AnalysisResponse:
    result = await use_case.execute(user_data.to_domain(), _user.id)
    return AnalysisResponse.from_domain(result)


@router.post("/rag", response_model=RagResponse)
async def rag_analysis(
    payload: RagRequest,
    use_case: RequestRecommendations = Depends(get_request_recommendations),
    _user: AuthUser = Depends(get_current_user),
) -> RagResponse:
    report = await use_case.execute(payload.analysis_id, _user.id)
    return RagResponse.from_domain(report)


@router.post("/simulate", response_model=SimulationResponse)
async def simulate(
    payload: SimulationRequest,
    use_case: SimulateScenario = Depends(get_simulate_scenario),
    _user: AuthUser = Depends(get_current_user),
) -> SimulationResponse:
    outcome = await use_case.execute(
        payload.original.to_domain(),
        payload.changes.to_domain(),
    )
    return SimulationResponse.from_domain(outcome)
