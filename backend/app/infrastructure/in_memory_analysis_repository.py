"""Repositorio de análisis en memoria (implementa el puerto AnalysisRepository).

Funciona dentro de un único proceso: los análisis se pierden al reiniciar y no
se comparten entre workers o réplicas.
"""

from __future__ import annotations

from collections import OrderedDict
from threading import Lock
from time import monotonic
from uuid import UUID, uuid4

from ..domain.entities import AnalysisContext
from ..domain.errors import AnalysisNotFoundError


class InMemoryAnalysisRepository:
    def __init__(self, ttl_seconds: float, max_entries: int):
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than zero.")
        if max_entries <= 0:
            raise ValueError("max_entries must be greater than zero.")

        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        # Las entidades son inmutables, así que se pueden guardar sin copiarlas
        self._entries: OrderedDict[str, tuple[AnalysisContext, float]] = OrderedDict()
        self._lock = Lock()

    def save(self, context: AnalysisContext) -> UUID:
        analysis_id = uuid4()
        key = str(analysis_id)

        with self._lock:
            self._remove_expired_locked()
            self._entries[key] = (context, monotonic() + self._ttl_seconds)
            self._entries.move_to_end(key)

            while len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)

        return analysis_id

    def get(
        self,
        analysis_id: UUID,
        owner_id: UUID | None = None,
    ) -> AnalysisContext:
        key = str(analysis_id)

        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                raise AnalysisNotFoundError

            context, expires_at = entry
            if expires_at <= monotonic():
                del self._entries[key]
                raise AnalysisNotFoundError

            if owner_id is not None and context.owner_id != owner_id:
                raise AnalysisNotFoundError

            self._entries.move_to_end(key)
            return context

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    def _remove_expired_locked(self) -> None:
        now = monotonic()
        expired_keys = [
            key for key, (_, expires_at) in self._entries.items() if expires_at <= now
        ]
        for key in expired_keys:
            del self._entries[key]
