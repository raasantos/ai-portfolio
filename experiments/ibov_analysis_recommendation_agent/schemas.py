"""Tool schemas (Fase 2): the contract the LLM sees.

Each entry is a standard Anthropic tool definition (name, description,
input_schema). The descriptions are the agent's ONLY documentation — it
never sees handlers.py — so each one states not just what the tool does
but WHEN to call it and what it depends on. Tool Selection quality depends
entirely on this text.

Design decisions embedded here (see BUILD_PLAN.md / TOOLS_GUIDE.md):
- Compute tools take only `ticker` (+ window parameters), never price
  arrays: prices live in the server-side cache (cache.py), so the LLM
  never sees a raw series — the project's core design rule.
- Fetch tools return values normalized with explicit units
  (dividend_yield_pct = 6.0 means 6%) so the model never converts units.
- Defaults mirror the v1 pipeline constants (3mo, 9/21, 14, 20) to keep
  the Fase 6 v1-vs-v2 comparison apples-to-apples.
- Inter-tool dependencies (fetch before compute) are stated in the
  descriptions AND enforced by the handlers with explicit errors — a
  description is a suggestion to the model, not a constraint
  (AUDIT_CHECKLIST item #7).
"""

_TICKER_PROPERTY = {
    "type": "string",
    "description": "B3 ticker symbol, e.g. 'PETR4', 'VALE3'.",
}

TOOLS = [
    {
        "name": "fetch_price_history",
        "description": (
            "Fetch daily OHLCV price history for a B3 ticker from brapi.dev "
            "and store it in the server-side cache. Returns only a summary "
            "(number of data points, date range) — never the raw price "
            "series. Call this ONCE per ticker BEFORE any compute_* "
            "technical tool (compute_moving_average_crossover, compute_rsi, "
            "compute_relative_volume); those tools read prices from this "
            "cache and return an error if it is empty. Do not call it again "
            "for the same ticker unless you need a different range."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": _TICKER_PROPERTY,
                "range": {
                    "type": "string",
                    "enum": ["1mo", "3mo", "6mo", "1y"],
                    "description": (
                        "History window. Defaults to '3mo', which is enough "
                        "for the default indicator windows (MA 9/21, RSI 14, "
                        "volume lookback 20). '1mo' is usually too short for "
                        "those defaults; pick a longer range only if you "
                        "plan to use longer indicator windows."
                    ),
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "fetch_fundamental_statistics",
        "description": (
            "Fetch valuation statistics for a B3 ticker from brapi.dev: "
            "trailing P/E (`pe`), dividend yield (`dividend_yield_pct`, in "
            "percentage points — 6.0 means 6%), and price-to-book "
            "(`price_to_book`). Values arrive already normalized; never "
            "convert units yourself. Independent of every other tool — no "
            "prerequisite. Fields the API did not return are listed in "
            "`missing_fields`; treat those as unavailable, never guess them."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"ticker": _TICKER_PROPERTY},
            "required": ["ticker"],
        },
    },
    {
        "name": "fetch_financial_data",
        "description": (
            "Fetch profitability and leverage inputs for a B3 ticker from "
            "brapi.dev: ROE (`roe_pct`, in percentage points), total gross "
            "debt (`total_debt`, BRL) and EBITDA (`ebitda`, BRL). Also "
            "stores the raw data in the server-side cache for "
            "compute_debt_to_ebitda — call this BEFORE that tool. Do NOT "
            "divide total_debt by ebitda yourself; compute_debt_to_ebitda "
            "exists for that. Missing fields are listed in `missing_fields`."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"ticker": _TICKER_PROPERTY},
            "required": ["ticker"],
        },
    },
    {
        "name": "compute_moving_average_crossover",
        "description": (
            "Compute whether the short simple moving average crossed the "
            "long one at the most recent bar, from prices in the "
            "server-side cache. Requires fetch_price_history to have run "
            "for this ticker first (returns an explicit error otherwise). "
            "Returns the two SMA values, `position` ('above'/'below'/"
            "'equal': short relative to long now) and `crossover` "
            "('bullish'/'bearish'/null: did the relation flip at the last "
            "bar). Defaults 9/21 match the project baseline; override only "
            "with a reason."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": _TICKER_PROPERTY,
                "short_window": {
                    "type": "integer",
                    "description": "Short SMA window in trading days. Default 9.",
                },
                "long_window": {
                    "type": "integer",
                    "description": (
                        "Long SMA window in trading days; must be greater "
                        "than short_window. Default 21."
                    ),
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "compute_rsi",
        "description": (
            "Compute the Relative Strength Index (Wilder's smoothing) for a "
            "ticker from cached prices. Requires fetch_price_history first "
            "(explicit error otherwise). Returns one value between 0 and "
            "100 — conventional reading: <= 30 oversold, >= 70 overbought. "
            "Default period 14 matches the project baseline."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": _TICKER_PROPERTY,
                "period": {
                    "type": "integer",
                    "description": "RSI period in trading days. Default 14.",
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "compute_relative_volume",
        "description": (
            "Compute the last day's traded volume relative to the average "
            "of the previous N days, from cached prices. Requires "
            "fetch_price_history first (explicit error otherwise). This is "
            "a SHORT-TERM signal only: a high ratio (e.g. >= 1.5) means "
            "unusual activity, but volume spikes accompany selloffs as "
            "well as rallies — never treat high relative volume alone as "
            "bullish. Default lookback 20 days."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": _TICKER_PROPERTY,
                "lookback": {
                    "type": "integer",
                    "description": (
                        "Number of previous days in the volume baseline "
                        "(the last day is excluded from its own baseline). "
                        "Default 20."
                    ),
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "compute_debt_to_ebitda",
        "description": (
            "Compute the Debt/EBITDA leverage ratio (totalDebt / ebitda) "
            "from financial data cached by fetch_financial_data. This "
            "ratio is DERIVED — brapi.dev does not return it directly, "
            "which is why it has its own compute tool while P/E, dividend "
            "yield and ROE do not. Requires fetch_financial_data to have "
            "run for this ticker first (explicit error otherwise). The "
            "project's baseline filter treats <= 3.5 as acceptable "
            "leverage."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"ticker": _TICKER_PROPERTY},
            "required": ["ticker"],
        },
    },
]

TOOL_NAMES = [tool["name"] for tool in TOOLS]
