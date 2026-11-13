from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ...domain.entities import AnalysisHistoryEntry
from ...domain.ports import AnalysisHistoryRepository


@dataclass(frozen=True)
class AnalysisHistoryPage:
    items: tuple[AnalysisHistoryEntry, ...]
    limit: int
    offset: int
    has_more: bool


class ListAnalysisHistory:
    def __init__(self, repository: AnalysisHistoryRepository):
        self._repository = repository

    def execute(self, owner_id: UUID, limit: int, offset: int) -> AnalysisHistoryPage:
        entries = self._repository.list_for_user(owner_id, limit + 1, offset)
        return AnalysisHistoryPage(
            items=tuple(entries[:limit]),
            limit=limit,
            offset=offset,
            has_more=len(entries) > limit,
        )
