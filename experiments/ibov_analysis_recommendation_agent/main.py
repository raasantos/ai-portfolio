"""v1 orchestrator: fixed pipeline over the sandbox tickers.

Usage: python main.py
Requires no token for the 4 sandbox tickers. Synthesis runs only if
ANTHROPIC_API_KEY is set (in .env or the environment); otherwise the
computed signals are printed and synthesis is skipped.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from data_provider import BrapiClient
from screener import screen_universe
from universe import get_universe


def print_result(result) -> None:
    print(f"\n=== {result.ticker} ===")
    if result.technicals:
        tech = result.technicals
        cross = tech["ma_crossover"]
        print(
            f"  MA{cross['short_window']}/{cross['long_window']}: "
            f"{cross['position']} (crossover: {cross['crossover']})"
        )
        print(f"  RSI({tech['rsi_period']}): {tech['rsi']}")
        print(
            f"  Relative volume ({tech['volume_lookback_days']}d): "
            f"{tech['relative_volume']}x"
        )
    if result.fundamentals:
        f = result.fundamentals
        def fmt(value, suffix=""):
            return f"{value:.2f}{suffix}" if value is not None else "n/a"
        print(
            f"  P/E: {fmt(f['pe'])} | DY: {fmt(f['dividend_yield_pct'], '%')} | "
            f"P/B: {fmt(f['price_to_book'])} | ROE: {fmt(f['roe_pct'], '%')} | "
            f"Debt/EBITDA: {fmt(f['debt_to_ebitda'])}"
        )
        if f["missing_fields"]:
            print(f"  Missing fields: {', '.join(f['missing_fields'])}")
    status = "PASS" if result.fundamental_passed else "FAIL"
    if result.fundamental_passed is not None:
        print(f"  Fundamental filter: {status}")
        for reason in result.fundamental_reasons:
            print(f"    - {reason}")
    for signal in result.bullish_signals:
        print(f"  Bullish: {signal}")
    for error in result.data_errors:
        print(f"  DATA ERROR: {error}")
    print(f"  Shortlisted: {'YES' if result.is_shortlisted else 'no'}")


def main() -> None:
    load_dotenv()
    client = BrapiClient()
    tickers = get_universe()
    print(f"Screening {len(tickers)} tickers: {', '.join(tickers)}")

    results = screen_universe(client, tickers)
    for result in results:
        print_result(result)

    shortlisted = [r.ticker for r in results if r.is_shortlisted]
    print(f"\nShortlist: {', '.join(shortlisted) if shortlisted else '(empty)'}")

    if os.getenv("ANTHROPIC_API_KEY"):
        from synthesis import synthesize

        print("\n--- LLM synthesis ---\n")
        print(synthesize(results))
    else:
        print("\nANTHROPIC_API_KEY not set - skipping LLM synthesis.")


if __name__ == "__main__":
    main()
