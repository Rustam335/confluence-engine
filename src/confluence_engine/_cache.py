"""A small bounded, TTL-based cache used internally by market adapters."""
from __future__ import annotations

import time
from collections import OrderedDict
from typing import Callable, Generic, Hashable, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class TTLCache(Generic[K, V]):
    """LRU cache with per-entry time-to-live and a hard entry cap.

    Entries expire `ttl_seconds` after insertion. On insert, expired entries are
    purged and, if still over `max_entries`, the oldest entries are evicted.
    Not thread-safe — intended for single-threaded adapter use.
    """

    def __init__(self, ttl_seconds: float, max_entries: int = 128, *, time_fn: Callable[[], float] = time.time) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._ttl = ttl_seconds
        self._max = max_entries
        self._time = time_fn
        self._store: "OrderedDict[K, tuple[float, V]]" = OrderedDict()

    def get(self, key: K) -> V | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        ts, value = entry
        if self._time() - ts >= self._ttl:
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: K, value: V) -> None:
        now = self._time()
        expired = [k for k, (ts, _) in self._store.items() if now - ts >= self._ttl]
        for k in expired:
            del self._store[k]
        self._store[key] = (now, value)
        self._store.move_to_end(key)
        while len(self._store) > self._max:
            self._store.popitem(last=False)

    def __len__(self) -> int:
        return len(self._store)
