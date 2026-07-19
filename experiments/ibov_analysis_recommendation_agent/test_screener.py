"""Offline test suite — no network calls.

Fixtures in fixtures/ are RAW brapi.dev responses pulled live on
2026-07-18 (PETR4, tokenless sandbox). Parsing tests run against real
payload shapes, not hand-invented ones; indicator tests use small
hand-computed datasets so the expected numbers are verifiable by hand.
"""

import json
import random
from pathlib import Path

import pytest

from data_provider import (
    BrapiError,
    parse_financial_data,
    parse_historical,
    parse_statistics,
)
from fundamentals import extract_fundamentals, passes_fundamental_filter
from indicators import (
    moving_average_crossover_signal,
    relative_volume,
    rsi,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


# --- data_provider parsing (real payload shapes) ---


def test_parse_historical_sorts_oldest_first():
    payload = load_fixture("petr4_historical.json")
    # Shuffle to prove sorting is explicit, not inherited from the API.
    random.Random(42).shuffle(payload["results"][0]["historicalDataPrice"])
    points = parse_historical(payload)
    dates = [p["date"] for p in points]
    assert dates == sorted(dates)
    assert len(points) == 61


def test_parse_historical_field_names():
    points = parse_historical(load_fixture("petr4_historical.json"))
    for key in ("date", "open", "high", "low", "close", "volume"):
        assert key in points[0], f"missing verified field {key}"


def test_parse_historical_raises_without_prices():
    with pytest.raises(BrapiError):
        parse_historical({"results": [{"symbol": "XXXX4"}]})


def test_parse_statistics_has_verified_fields():
    stats = parse_statistics(load_fixture("petr4_statistics.json"))
    for key in ("trailingPE", "dividendYield", "priceToBook"):
        assert key in stats, f"missing verified field {key}"


def test_parse_financial_data_has_verified_fields():
    financial = parse_financial_data(load_fixture("petr4_financial.json"))
    for key in ("returnOnEquity", "totalDebt", "ebitda"):
        assert key in financial, f"missing verified field {key}"


# --- indicators (hand-computed expectations) ---


def test_crossover_bullish_detected():
    # Designed so short SMA(3) crosses above long SMA(5) at the last bar:
    # prev bar: sma3=9.33 < sma5=9.60; last bar: sma3=10.67 > sma5=10.40.
    closes = [10, 10, 10, 10, 10, 10, 9, 9, 14]
    signal = moving_average_crossover_signal(closes, 3, 5)
    assert signal["crossover"] == "bullish"
    assert signal["position"] == "above"


def test_crossover_none_in_steady_uptrend():
    closes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    signal = moving_average_crossover_signal(closes, 3, 5)
    assert signal["crossover"] is None
    assert signal["position"] == "above"


def test_rsi_wilder_hand_computed():
    # period=3, closes [10,11,12,11,12] -> changes [+1,+1,-1,+1]
    # seed: avg_gain=2/3, avg_loss=1/3
    # step: avg_gain=(2/3*2+1)/3=7/9, avg_loss=(1/3*2+0)/3=2/9
    # RS=3.5 -> RSI = 100 - 100/4.5 = 77.777...
    assert rsi([10, 11, 12, 11, 12], period=3) == pytest.approx(77.7778, abs=1e-3)


def test_rsi_extremes():
    assert rsi([1, 2, 3, 4, 5], period=3) == 100.0
    assert rsi([5, 4, 3, 2, 1], period=3) == 0.0


def test_relative_volume():
    volumes = [100.0] * 20 + [300.0]
    assert relative_volume(volumes, lookback=20) == pytest.approx(3.0)


def test_indicators_reject_insufficient_data():
    with pytest.raises(ValueError):
        rsi([1, 2], period=14)
    with pytest.raises(ValueError):
        moving_average_crossover_signal([1, 2, 3], 3, 5)
    with pytest.raises(ValueError):
        relative_volume([1, 2, 3], lookback=20)


# --- fundamentals (real fixture values, unit conversion) ---


def test_extract_fundamentals_units_from_real_response():
    stats = parse_statistics(load_fixture("petr4_statistics.json"))
    financial = parse_financial_data(load_fixture("petr4_financial.json"))
    f = extract_fundamentals(stats, financial)
    # Live PETR4 values on 2026-07-18: fraction -> percentage conversion.
    assert f["dividend_yield_pct"] == pytest.approx(6.0)
    assert f["roe_pct"] == pytest.approx(24.267222, abs=1e-4)
    # Derived ratio: 676977000000 / 230884000000
    assert f["debt_to_ebitda"] == pytest.approx(2.9321, abs=1e-3)
    assert f["missing_fields"] == []


def test_missing_ebitda_fails_filter_explicitly():
    f = extract_fundamentals(
        {"trailingPE": 10.0, "dividendYield": 0.05, "priceToBook": 1.0},
        {"returnOnEquity": 0.15, "totalDebt": 1000.0, "ebitda": None},
    )
    assert f["debt_to_ebitda"] is None
    assert "ebitda" in f["missing_fields"]
    passed, reasons = passes_fundamental_filter(f)
    assert passed is False
    assert any("debt/EBITDA missing" in r for r in reasons)


def test_filter_pass_and_reject():
    good = {"pe": 8.0, "roe_pct": 18.0, "debt_to_ebitda": 1.5}
    passed, reasons = passes_fundamental_filter(good)
    assert passed is True and reasons == []

    expensive = {"pe": 30.0, "roe_pct": 18.0, "debt_to_ebitda": 1.5}
    passed, reasons = passes_fundamental_filter(expensive)
    assert passed is False
    assert any("P/E" in r for r in reasons)
