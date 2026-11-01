from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock
from time import monotonic
from uuid import UUID, uuid4

from backend.app.schemas.analysis import (
    PredictionData,
    ShapData,
    UserData,
)


@dataclass(frozen=True)
class AnalysisContext:
    user_data: UserData
    prediction: PredictionData
    shap: ShapData
    expires_at: float


class AnalysisNotFoundError(Exception):
    """The requested analysis is missing or expired."""


class AnalysisCache:
    def __init__(self, ttl_seconds: float, max_entries: int):
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than zero.")
        if max_entries <= 0:
            raise ValueError("max_entries must be greater than zero.")

        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._entries: OrderedDict[str, AnalysisContext] = OrderedDict()
        self._lock = Lock()

    def store(
        self,
        user_data: UserData,
        prediction: PredictionData,
        shap: ShapData,
    ) -> UUID:
        analysis_id = uuid4()
        context = AnalysisContext(
            user_data=user_data.model_copy(deep=True),
            prediction=prediction.model_copy(deep=True),
            shap=shap.model_copy(deep=True),
            expires_at=monotonic() + self._ttl_seconds,
        )

        with self._lock:
            self._remove_expired_locked()
            self._entries[str(analysis_id)] = context
            self._entries.move_to_end(str(analysis_id))

            while len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)

        return analysis_id

    def get(self, analysis_id: UUID) -> AnalysisContext:
        key = str(analysis_id)

        with self._lock:
            context = self._entries.get(key)
            if context is None:
                raise AnalysisNotFoundError

            if context.expires_at <= monotonic():
                del self._entries[key]
                raise AnalysisNotFoundError

            self._entries.move_to_end(key)
            return AnalysisContext(
                user_data=context.user_data.model_copy(deep=True),
                prediction=context.prediction.model_copy(deep=True),
                shap=context.shap.model_copy(deep=True),
                expires_at=context.expires_at,
            )

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    def _remove_expired_locked(self) -> None:
        now = monotonic()
        expired_keys = [
            key
            for key, context in self._entries.items()
            if context.expires_at <= now
        ]
        for key in expired_keys:
            del self._entries[key]
