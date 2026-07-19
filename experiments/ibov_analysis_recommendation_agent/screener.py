"""v1 fixed pipeline: fetch -> compute indicators -> fundamental filter.

Runs every step in a fixed order for every ticker — no LLM decisions here.
Kept as the baseline for the Fase 6 comparison against the v2 dynamic
agent (which chooses which tools to call per ticker).

Partial-failure isolation (AUDIT_CHECKLIST #6): each ticker collects its
own data_errors; one ticker failing never contaminates another.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from data_provider import BrapiClient, BrapiError
from fundamentals import extract_fundamentals, passes_fundamental_filter
from indicators import moving_average_crossover_signal, relative_volume, rsi

PRICE_RANGE = "3mo"
SHORT_WINDOW = 9
LONG_WINDOW = 21
RSI_PERIOD = 14
VOLUME_LOOKBACK = 20
RSI_OVERSOLD = 30.0
HIGH_RELATIVE_VOLUME = 1.5


@dataclass
class ScreenerResult:
    ticker: str
    technicals: dict | None = None
    fundamentals: dict | None = None
    fundamental_passed: bool | None = None
    fundamental_reasons: list[str] = field(default_factory=list)
    bullish_signals: list[str] = field(default_factory=list)
    is_shortlisted: bool = False
    data_errors: list[str] = field(default_factory=list)


def _collect_bullish_signals(technicals: dict) -> list[str]:
    """Bullish = fresh bullish crossover, short MA above long, or RSI
    oversold. High relative volume is recorded in technicals but is NOT
    counted as bullish on its own — volume spikes accompany selloffs too
    (deliberate call; AUDIT_CHECKLIST #5 asks you to argue with this).
    """
    signals = []
    crossover = technicals["ma_crossover"]
    if crossover["crossover"] == "bullish":
        signals.append(
            f"MA({SHORT_WINDOW}/{LONG_WINDOW}) bullish crossover at last bar"
        )
    elif crossover["position"] == "above":
        signals.append(f"MA({SHORT_WINDOW}) above MA({LONG_WINDOW})")
    if technicals["rsi"] <= RSI_OVERSOLD:
        signals.append(f"RSI {technicals['rsi']:.1f} oversold (<= {RSI_OVERSOLD:g})")
    return signals


def screen_ticker(client: BrapiClient, ticker: str) -> ScreenerResult:
    result = ScreenerResult(ticker=ticker)

    try:
        prices = client.get_historical(ticker, range_=PRICE_RANGE)
        closes = [point["close"] for point in prices]
        volumes = [float(point["volume"]) for point in prices]
        result.technicals = {
            "ma_crossover": moving_average_crossover_signal(
                closes, SHORT_WINDOW, LONG_WINDOW
            ),
            "rsi": round(rsi(closes, RSI_PERIOD), 2),
            "rsi_period": RSI_PERIOD,
            "relative_volume": round(relative_volume(volumes, VOLUME_LOOKBACK), 2),
            "volume_lookback_days": VOLUME_LOOKBACK,
            "high_relative_volume": None,  # set below
            "data_points": len(prices),
        }
        result.technicals["high_relative_volume"] = (
            result.technicals["relative_volume"] >= HIGH_RELATIVE_VOLUME
        )
    except (BrapiError, ValueError) as exc:
        result.data_errors.append(f"technicals: {exc}")

    try:
        statistics = client.get_statistics(ticker)
        financial = client.get_financial_data(ticker)
        result.fundamentals = extract_fundamentals(statistics, financial)
        passed, reasons = passes_fundamental_filter(result.fundamentals)
        result.fundamental_passed = passed
        result.fundamental_reasons = reasons
    except BrapiError as exc:
        result.data_errors.append(f"fundamentals: {exc}")

    if result.technicals is not None:
        result.bullish_signals = _collect_bullish_signals(result.technicals)

    result.is_shortlisted = bool(
        result.fundamental_passed and result.bullish_signals
    )
    return result


def screen_universe(client: BrapiClient, tickers: list[str]) -> list[ScreenerResult]:
    return [screen_ticker(client, ticker) for ticker in tickers]
