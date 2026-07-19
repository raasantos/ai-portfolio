"""Tool handlers (Fases 2-3): the server side of each tool schema.

Every handler has the same signature — (client, cache, tool_input) -> dict —
and connects one schema in schemas.py to the already-tested modules
(data_provider.py, indicators.py, fundamentals.py). Handlers never return
raw price/volume arrays to the model: fetch handlers return summaries and
store the raw data in the cache; compute handlers read the cache and
return only computed values (the project's core design rule).

Field names come from data_provider.py / fundamentals.py, which were
verified against live brapi.dev responses (AUDIT_CHECKLIST #1) — do not
introduce new API field names here.
"""

from __future__ import annotations

from datetime import datetime, timezone

from cache import FINANCIAL_DATA, HISTORY, STATISTICS, TickerCache
from data_provider import BrapiClient
from fundamentals import debt_to_ebitda_ratio, extract_financial, extract_statistics
from indicators import moving_average_crossover_signal, relative_volume, rsi


class ToolError(Exception):
    """A tool could not run with the given input/state (e.g. empty cache).

    The agent loop converts this into a tool_result with is_error=True so
    the model sees what went wrong and can correct course (Reflection and
    Error Correction) instead of the whole run crashing. Messages are
    written for the model: they say which tool to call to fix the state.
    """


def _ticker(tool_input: dict) -> str:
    return str(tool_input["ticker"]).strip().upper()


def _iso_date(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).date().isoformat()


def _cached_history(cache: TickerCache, ticker: str) -> list[dict]:
    points = cache.get(ticker, HISTORY)
    if points is None:
        # Explicit error, never a silent auto-fetch: fetching is a decision
        # that belongs to the agent (genuine Tool Selection), and the error
        # path is exactly what AUDIT_CHECKLIST #7 requires us to verify.
        raise ToolError(
            f"No price history cached for {ticker}. "
            "Call fetch_price_history for this ticker first."
        )
    return points


# --- Fetch layer ---


def fetch_price_history(client: BrapiClient, cache: TickerCache, tool_input: dict) -> dict:
    ticker = _ticker(tool_input)
    range_ = tool_input.get("range", "3mo")
    points = client.get_historical(ticker, range_=range_)
    cache.put(ticker, HISTORY, points)
    # Summary only — the raw series stays server-side.
    return {
        "ticker": ticker,
        "range": range_,
        "interval": "1d",
        "data_points": len(points),
        "first_date": _iso_date(points[0]["date"]),
        "last_date": _iso_date(points[-1]["date"]),
        "cached": True,
    }


def fetch_fundamental_statistics(
    client: BrapiClient, cache: TickerCache, tool_input: dict
) -> dict:
    ticker = _ticker(tool_input)
    statistics = client.get_statistics(ticker)
    cache.put(ticker, STATISTICS, statistics)
    return {"ticker": ticker, **extract_statistics(statistics)}


def fetch_financial_data(client: BrapiClient, cache: TickerCache, tool_input: dict) -> dict:
    ticker = _ticker(tool_input)
    financial = client.get_financial_data(ticker)
    cache.put(ticker, FINANCIAL_DATA, financial)
    return {"ticker": ticker, **extract_financial(financial)}


# --- Compute layer ---


def compute_moving_average_crossover(
    client: BrapiClient, cache: TickerCache, tool_input: dict
) -> dict:
    ticker = _ticker(tool_input)
    short_window = int(tool_input.get("short_window", 9))
    long_window = int(tool_input.get("long_window", 21))
    closes = [point["close"] for point in _cached_history(cache, ticker)]
    signal = moving_average_crossover_signal(closes, short_window, long_window)
    return {"ticker": ticker, **signal}


def compute_rsi(client: BrapiClient, cache: TickerCache, tool_input: dict) -> dict:
    ticker = _ticker(tool_input)
    period = int(tool_input.get("period", 14))
    closes = [point["close"] for point in _cached_history(cache, ticker)]
    return {"ticker": ticker, "period": period, "rsi": round(rsi(closes, period), 2)}


def compute_relative_volume(
    client: BrapiClient, cache: TickerCache, tool_input: dict
) -> dict:
    ticker = _ticker(tool_input)
    lookback = int(tool_input.get("lookback", 20))
    volumes = [float(point["volume"]) for point in _cached_history(cache, ticker)]
    return {
        "ticker": ticker,
        "lookback_days": lookback,
        "relative_volume": round(relative_volume(volumes, lookback), 2),
    }


def compute_debt_to_ebitda(
    client: BrapiClient, cache: TickerCache, tool_input: dict
) -> dict:
    ticker = _ticker(tool_input)
    financial = cache.get(ticker, FINANCIAL_DATA)
    if financial is None:
        raise ToolError(
            f"No financial data cached for {ticker}. "
            "Call fetch_financial_data for this ticker first."
        )
    total_debt = financial.get("totalDebt")
    ebitda = financial.get("ebitda")
    ratio = debt_to_ebitda_ratio(total_debt, ebitda)
    if ratio is None:
        raise ToolError(
            f"Cannot compute debt/EBITDA for {ticker}: totalDebt or ebitda "
            "is missing, or EBITDA is not positive."
        )
    return {
        "ticker": ticker,
        "debt_to_ebitda": round(ratio, 2),
        "total_debt": total_debt,
        "ebitda": ebitda,
    }


TOOL_HANDLERS = {
    "fetch_price_history": fetch_price_history,
    "fetch_fundamental_statistics": fetch_fundamental_statistics,
    "fetch_financial_data": fetch_financial_data,
    "compute_moving_average_crossover": compute_moving_average_crossover,
    "compute_rsi": compute_rsi,
    "compute_relative_volume": compute_relative_volume,
    "compute_debt_to_ebitda": compute_debt_to_ebitda,
}
