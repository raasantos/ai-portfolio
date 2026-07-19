"""Fundamental data extraction and hard-cutoff filter.

Unit convention (verified against the LIVE PETR4 response on 2026-07-18,
see fixtures/): brapi returns `dividendYield` and `returnOnEquity` as
FRACTIONS (0.06 = 6%). We convert to percentage points here, once, at the
extraction boundary. If brapi ever changes this convention, every yield
and ROE silently becomes 100x wrong — AUDIT_CHECKLIST item #1 exists to
re-check this against a fresh live response.

`debt_to_ebitda` is DERIVED (totalDebt / ebitda) — brapi does not return
it directly. Note: totalDebt is GROSS debt (includes leases); for PETR4
this gave 677/231 = 2.93, consistent with real-world leverage.
"""

from __future__ import annotations

PE_MIN = 0.0
PE_MAX = 25.0
ROE_MIN_PCT = 10.0
DEBT_TO_EBITDA_MAX = 3.5


def debt_to_ebitda_ratio(total_debt: float | None, ebitda: float | None) -> float | None:
    """Derived leverage ratio (totalDebt / ebitda) — brapi does not return
    this directly. None when either input is missing or EBITDA <= 0 (a
    non-positive EBITDA makes the ratio meaningless, not risk-free)."""
    if total_debt is None or ebitda is None or ebitda <= 0:
        return None
    return total_debt / ebitda


def _pick(source: dict, field: str, missing: list[str]):
    value = source.get(field)
    if value is None:
        missing.append(field)
    return value


def extract_statistics(statistics: dict) -> dict:
    """Normalize the `defaultKeyStatistics` payload. dividendYield arrives
    as a fraction (0.06 = 6%) and is converted to percentage points here,
    once — the highest-risk conversion in the codebase (module docstring).
    """
    missing: list[str] = []
    pe = _pick(statistics, "trailingPE", missing)
    dividend_yield = _pick(statistics, "dividendYield", missing)
    price_to_book = _pick(statistics, "priceToBook", missing)
    return {
        "pe": pe,
        "dividend_yield_pct": dividend_yield * 100 if dividend_yield is not None else None,
        "price_to_book": price_to_book,
        "missing_fields": missing,
    }


def extract_financial(financial_data: dict) -> dict:
    """Normalize the `financialData` payload. returnOnEquity arrives as a
    fraction and is converted to percentage points here, once."""
    missing: list[str] = []
    roe = _pick(financial_data, "returnOnEquity", missing)
    total_debt = _pick(financial_data, "totalDebt", missing)
    ebitda = _pick(financial_data, "ebitda", missing)
    return {
        "roe_pct": roe * 100 if roe is not None else None,
        "total_debt": total_debt,
        "ebitda": ebitda,
        "missing_fields": missing,
    }


def extract_fundamentals(statistics: dict, financial_data: dict) -> dict:
    """Normalize the two brapi module payloads into one flat dict.

    Composed from extract_statistics() + extract_financial() so the v2
    agent's fetch tools reuse the exact same unit conversions (single
    source of truth). Absent or null source fields are recorded in
    `missing_fields` (by their original brapi names) and surface as None —
    never as a default number that could pass a filter by accident.
    """
    stats = extract_statistics(statistics)
    financial = extract_financial(financial_data)
    return {
        "pe": stats["pe"],
        "dividend_yield_pct": stats["dividend_yield_pct"],
        "price_to_book": stats["price_to_book"],
        "roe_pct": financial["roe_pct"],
        "total_debt": financial["total_debt"],
        "ebitda": financial["ebitda"],
        "debt_to_ebitda": debt_to_ebitda_ratio(
            financial["total_debt"], financial["ebitda"]
        ),
        "missing_fields": stats["missing_fields"] + financial["missing_fields"],
    }


def passes_fundamental_filter(fundamentals: dict) -> tuple[bool, list[str]]:
    """Hard cutoffs: 0 < P/E <= 25, ROE >= 10%, debt/EBITDA <= 3.5.

    A missing metric FAILS the filter with an explicit reason — missing
    data must never pass by accident (AUDIT_CHECKLIST item #6). Thresholds
    are deliberate defaults meant to be argued with (item #5).
    """
    reasons: list[str] = []

    pe = fundamentals.get("pe")
    if pe is None:
        reasons.append("P/E missing")
    elif not (PE_MIN < pe <= PE_MAX):
        reasons.append(f"P/E {pe:.1f} outside ({PE_MIN:g}, {PE_MAX:g}]")

    roe_pct = fundamentals.get("roe_pct")
    if roe_pct is None:
        reasons.append("ROE missing")
    elif roe_pct < ROE_MIN_PCT:
        reasons.append(f"ROE {roe_pct:.1f}% below {ROE_MIN_PCT:g}%")

    debt_to_ebitda = fundamentals.get("debt_to_ebitda")
    if debt_to_ebitda is None:
        reasons.append("debt/EBITDA missing (totalDebt or ebitda unavailable)")
    elif debt_to_ebitda > DEBT_TO_EBITDA_MAX:
        reasons.append(
            f"debt/EBITDA {debt_to_ebitda:.2f} above {DEBT_TO_EBITDA_MAX:g}"
        )

    return (len(reasons) == 0, reasons)
