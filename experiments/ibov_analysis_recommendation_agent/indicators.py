"""Hand-written technical indicators.

All functions assume prices/volumes are ordered OLDEST-FIRST — the order
guaranteed by data_provider.parse_historical(). Pure functions, no I/O:
the LLM never computes these numbers, it only interprets the results
(core design rule of this project).
"""

from __future__ import annotations


def sma(values: list[float], window: int) -> float:
    """Simple moving average of the LAST `window` values."""
    if window <= 0:
        raise ValueError("window must be positive")
    if len(values) < window:
        raise ValueError(f"need at least {window} values, got {len(values)}")
    return sum(values[-window:]) / window


def moving_average_crossover_signal(
    closes: list[float], short_window: int = 9, long_window: int = 21
) -> dict:
    """Compare short vs long SMA at the last point and one point before.

    Returns position ("above"/"below"/"equal": short relative to long now)
    and crossover ("bullish"/"bearish"/None: did the relation flip at the
    most recent point).
    """
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window")
    if len(closes) < long_window + 1:
        raise ValueError(
            f"need at least {long_window + 1} closes, got {len(closes)}"
        )

    short_now = sma(closes, short_window)
    long_now = sma(closes, long_window)
    short_prev = sma(closes[:-1], short_window)
    long_prev = sma(closes[:-1], long_window)

    if short_now > long_now:
        position = "above"
    elif short_now < long_now:
        position = "below"
    else:
        position = "equal"

    crossover = None
    if short_prev <= long_prev and short_now > long_now:
        crossover = "bullish"
    elif short_prev >= long_prev and short_now < long_now:
        crossover = "bearish"

    return {
        "short_window": short_window,
        "long_window": long_window,
        "short_ma": round(short_now, 4),
        "long_ma": round(long_now, 4),
        "position": position,
        "crossover": crossover,
    }


def rsi(closes: list[float], period: int = 14) -> float:
    """Relative Strength Index with Wilder's smoothing.

    Seed averages = simple mean of gains/losses over the first `period`
    changes; each later average = (prev_avg * (period - 1) + current) / period.
    """
    if period <= 0:
        raise ValueError("period must be positive")
    if len(closes) < period + 1:
        raise ValueError(
            f"need at least {period + 1} closes, got {len(closes)}"
        )

    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(change, 0.0) for change in changes]
    losses = [max(-change, 0.0) for change in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for gain, loss in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    if avg_loss == 0:
        return 100.0
    relative_strength = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + relative_strength)


def relative_volume(volumes: list[float], lookback: int = 20) -> float:
    """Last day's volume relative to the mean of the `lookback` days
    before it (the last day is excluded from its own baseline)."""
    if lookback <= 0:
        raise ValueError("lookback must be positive")
    if len(volumes) < lookback + 1:
        raise ValueError(
            f"need at least {lookback + 1} volumes, got {len(volumes)}"
        )
    baseline = volumes[-(lookback + 1):-1]
    mean_baseline = sum(baseline) / lookback
    if mean_baseline == 0:
        raise ValueError("baseline volume is zero; cannot compute ratio")
    return volumes[-1] / mean_baseline
