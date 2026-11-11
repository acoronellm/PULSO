from __future__ import annotations

from ...domain.entities import CardiovascularProfile, ScenarioChanges, SimulationOutcome
from ...domain.ports import CardiovascularModel


class SimulateScenario:
    """Compara la salida del modelo para el perfil original y un escenario hipotético."""

    def __init__(self, model: CardiovascularModel):
        self._model = model

    async def execute(
        self,
        profile: CardiovascularProfile,
        changes: ScenarioChanges,
    ) -> SimulationOutcome:
        return await self._model.simulate(profile, changes)
