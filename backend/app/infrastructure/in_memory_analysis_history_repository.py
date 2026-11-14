from datetime import datetime, timezone
from threading import Lock
from uuid import UUID

from ..domain.entities import AnalysisHistoryEntry, Prediction


class InMemoryAnalysisHistoryRepository:
    """Test double for the persistent analysis-history port."""

    def __init__(self) -> None:
        self._entries: list[tuple[UUID, AnalysisHistoryEntry]] = []
        self._lock = Lock()

    def save(
        self,
        analysis_id: UUID,
        owner_id: UUID,
        prediction: Prediction,
    ) -> AnalysisHistoryEntry:
        entry = AnalysisHistoryEntry(
            analysis_id=analysis_id,
            probability=prediction.probability,
            classification=prediction.classification,
            threshold=prediction.threshold,
            model_version=prediction.model_version,
            created_at=datetime.now(timezone.utc),
        )
        with self._lock:
            self._entries.append((owner_id, entry))
        return entry

    def list_for_user(
        self,
        owner_id: UUID,
        limit: int,
        offset: int,
    ) -> list[AnalysisHistoryEntry]:
        with self._lock:
            entries = [
                entry for user_id, entry in reversed(self._entries) if user_id == owner_id
            ]
            return entries[offset : offset + limit]
