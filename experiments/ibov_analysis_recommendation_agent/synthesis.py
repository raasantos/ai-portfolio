"""v1 synthesis: ONE LLM call, NO tool access.

Design enforcement (AUDIT_CHECKLIST #4): the messages.create() call below
must NEVER receive a `tools=` parameter — adding one silently turns this
fixed pipeline back into a dynamic agent. Likewise, the prompt receives
only the already-computed signals dict, never raw price/volume arrays:
the LLM interprets numbers, it does not produce them.
"""

from __future__ import annotations

import json
from dataclasses import asdict

import anthropic

from screener import ScreenerResult

MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = """You are an equity analysis assistant for Brazilian stocks (B3/IBOV).

You receive ONLY precomputed technical and fundamental signals per ticker
— never raw price series. All math has already been done by deterministic
code. Do not calculate, estimate, or extrapolate any number; interpret the
provided values exactly as given. If a value is missing (null), say the
data was unavailable — do not guess it.

For each ticker, produce:
1. A short technical read (trend, momentum, volume context).
2. A short fundamental read (valuation, profitability, leverage).
3. A synthesized recommendation: Watchlist / Neutral / Avoid, with the
   one or two decisive factors named.

End with a ranked shortlist of the tickers worth watching, if any.
Be direct and concise. This is an educational screener, not investment
advice — include a one-line disclaimer at the end."""


def build_signals_payload(results: list[ScreenerResult]) -> str:
    """Serialize computed signals only. ScreenerResult never holds raw
    arrays, so a full asdict() is safe by construction."""
    return json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2)


def synthesize(
    results: list[ScreenerResult], client: anthropic.Anthropic | None = None
) -> str:
    if client is None:
        client = anthropic.Anthropic()

    payload = build_signals_payload(results)
    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Computed screener signals for today's run:\n\n"
                    f"{payload}\n\n"
                    "Write the analysis and recommendations."
                ),
            }
        ],
    )
    return "".join(block.text for block in response.content if block.type == "text")
