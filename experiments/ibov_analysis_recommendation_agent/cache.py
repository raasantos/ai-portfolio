"""Server-side data cache (Fase 3).

The core design rule of this project: compute tools receive only a ticker,
never raw price arrays. Fetch handlers store raw API data here; compute
handlers read from here. The LLM only ever sees computed results.

In-memory and per-run by design (BUILD_PLAN Fase 3): persistence across
sessions is deferred until the Memory chapter section is applied.

Keys are (ticker, kind) tuples — per-ticker keying is an explicit
AUDIT_CHECKLIST item #7 requirement: a single global slot would silently
serve one ticker's data to another when screening a batch.
"""

from __future__ import annotations

HISTORY = "history"
STATISTICS = "statistics"
FINANCIAL_DATA = "financial_data"


class TickerCache:
    def __init__(self) -> None:
        self._data: dict[tuple[str, str], object] = {}

    @staticmethod
    def _key(ticker: str, kind: str) -> tuple[str, str]:
        # Normalized so "petr4" and "PETR4" are the same entry — the model
        # controls the ticker string, so casing must not split the cache.
        return (ticker.strip().upper(), kind)

    def put(self, ticker: str, kind: str, value: object) -> None:
        self._data[self._key(ticker, kind)] = value

    def get(self, ticker: str, kind: str):
        """Returns the cached value, or None when nothing was fetched yet.
        Callers decide what an empty cache means (compute handlers turn it
        into an explicit tool error, never a silent fallback)."""
        return self._data.get(self._key(ticker, kind))

    def has(self, ticker: str, kind: str) -> bool:
        return self._key(ticker, kind) in self._data
