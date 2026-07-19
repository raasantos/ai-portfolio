"""HTTP client for brapi.dev.

Field names below were verified against LIVE API responses pulled on
2026-07-18 (see fixtures/petr4_*.json for the raw evidence):

- historical points: date, open, high, low, close, volume, adjustedClose
- defaultKeyStatistics: trailingPE, dividendYield, priceToBook
- financialData: returnOnEquity, totalDebt, ebitda

Observed on 2026-07-18: `historicalDataPrice` arrived OLDEST-FIRST
(ascending `date`), contradicting earlier docs that said newest-first.
We do not trust either order: parse_historical() sorts explicitly.

Units verified against the live PETR4 response:
- dividendYield = 0.06  -> fraction (6%), not a percentage
- returnOnEquity = 0.2427 -> fraction (24.3%), not a percentage
"""

from __future__ import annotations

import os

import requests

BASE_URL = "https://brapi.dev/api"
DEFAULT_TIMEOUT = 15.0


class BrapiError(Exception):
    """Raised when brapi.dev returns an error or an unusable payload."""


def _first_result(payload: dict) -> dict:
    results = payload.get("results")
    if not results or not isinstance(results, list):
        raise BrapiError(f"No 'results' in payload: {str(payload)[:200]}")
    return results[0]


def parse_historical(payload: dict) -> list[dict]:
    """Extract OHLCV points from a /quote response, sorted oldest-first.

    Sorting is explicit because brapi's default order has drifted between
    docs and reality before; downstream indicators assume oldest-first.
    """
    result = _first_result(payload)
    prices = result.get("historicalDataPrice")
    if not prices:
        raise BrapiError(
            f"No 'historicalDataPrice' for {result.get('symbol', '?')}"
        )
    return sorted(prices, key=lambda point: point["date"])


def parse_statistics(payload: dict) -> dict:
    result = _first_result(payload)
    stats = result.get("defaultKeyStatistics")
    if not stats:
        raise BrapiError(
            f"No 'defaultKeyStatistics' for {result.get('symbol', '?')}"
        )
    return stats


def parse_financial_data(payload: dict) -> dict:
    result = _first_result(payload)
    financial = result.get("financialData")
    if not financial:
        raise BrapiError(
            f"No 'financialData' for {result.get('symbol', '?')}"
        )
    return financial


class BrapiClient:
    """Thin HTTP wrapper; all payload interpretation lives in the
    module-level parse_* functions so they stay testable offline."""

    def __init__(self, token: str | None = None, timeout: float = DEFAULT_TIMEOUT):
        self.token = token if token is not None else os.getenv("BRAPI_TOKEN")
        self.timeout = timeout

    def _get(self, path: str, params: dict | None = None) -> dict:
        params = dict(params or {})
        if self.token:
            params["token"] = self.token
        response = requests.get(
            f"{BASE_URL}/{path}", params=params, timeout=self.timeout
        )
        if response.status_code != 200:
            raise BrapiError(
                f"GET /{path} -> {response.status_code}: {response.text[:200]}"
            )
        return response.json()

    def get_historical(
        self, ticker: str, range_: str = "3mo", interval: str = "1d"
    ) -> list[dict]:
        payload = self._get(
            f"quote/{ticker}", {"range": range_, "interval": interval}
        )
        return parse_historical(payload)

    def get_statistics(self, ticker: str) -> dict:
        payload = self._get(
            f"quote/{ticker}", {"modules": "defaultKeyStatistics"}
        )
        return parse_statistics(payload)

    def get_financial_data(self, ticker: str) -> dict:
        payload = self._get(f"quote/{ticker}", {"modules": "financialData"})
        return parse_financial_data(payload)
