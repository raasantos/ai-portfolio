"""Ticker universe.

SANDBOX_TICKERS are the four tickers brapi.dev serves WITHOUT a token
(verified live on 2026-07-18: these four returned 200 tokenless, while
WEGE3/ABEV3 returned 401). Full-IBOV coverage requires the paid plan —
that is a Fase 7 decision, not a default.
"""

SANDBOX_TICKERS = ["PETR4", "MGLU3", "VALE3", "ITUB4"]


def get_universe() -> list[str]:
    return list(SANDBOX_TICKERS)
