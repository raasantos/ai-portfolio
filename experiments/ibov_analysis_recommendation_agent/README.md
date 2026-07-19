# IBOV Analysis & Recommendation Agent

A stock-analysis agent for Brazilian equities (B3/IBOV) that combines
technical and fundamental signals — built as a hands-on exercise for
Chapter 6 (*Agents*) of Chip Huyen's **AI Engineering**.

Two complete architectures live side by side in this repo, on purpose:

| | v1 — fixed pipeline | v2 — dynamic agent |
|---|---|---|
| Entry point | `python main.py` | `python agent.py [TICKER ...]` |
| Who plans | The code (fixed order, every step, every ticker) | The model (chooses tools per ticker, per context) |
| LLM calls | 1 (synthesis over precomputed signals, **no tool access**) | ~3 iterations × N tickers (function-calling loop) |
| Files | `screener.py`, `synthesis.py`, `main.py` | `schemas.py`, `handlers.py`, `cache.py`, `agent.py` |

Keeping both enabled an empirical comparison (see [Findings](#findings)),
which is exactly the exercise the chapter's *Tool Selection* section asks
for.

## Core design rule

**The LLM never sees raw market data and never computes a number.**

- Fetch tools store raw API data in a server-side cache and return only a
  summary (point count, date range) to the model.
- Compute tools take a `ticker` (never a price array), read the cache,
  run deterministic math from `indicators.py` / `fundamentals.py`, and
  return only the computed result.
- The model's only jobs: decide which tools to call, and interpret
  already-computed values.

This makes numeric hallucination structurally impossible rather than
merely discouraged — the raw series physically never enters the model's
context.

## The 7 tools

| Tool | Layer | Backed by |
|---|---|---|
| `fetch_price_history` | fetch | `BrapiClient.get_historical()` |
| `fetch_fundamental_statistics` | fetch | `BrapiClient.get_statistics()` |
| `fetch_financial_data` | fetch | `BrapiClient.get_financial_data()` |
| `compute_moving_average_crossover` | compute | `indicators.moving_average_crossover_signal()` |
| `compute_rsi` | compute | `indicators.rsi()` (Wilder's smoothing) |
| `compute_relative_volume` | compute | `indicators.relative_volume()` |
| `compute_debt_to_ebitda` | compute | `fundamentals.debt_to_ebitda_ratio()` |

Schemas (what the model sees) live in `schemas.py`; handlers (what
actually runs) live in `handlers.py`. Inter-tool dependencies are stated
in the descriptions **and** enforced by the handlers with explicit errors
— a description is a suggestion to the model, not a constraint.

## The function-calling loop

`agent.py` implements the loop by hand (that's the point of the
exercise): call the API with tools → execute every requested tool →
return all results in one message → repeat until the model stops asking.
Guards: a hard `MAX_ITERATIONS` cap with a loud failure, duplicate-call
detection, and tool errors returned as `is_error` results so the model
can self-correct instead of crashing.

Every run is appended to `runs.jsonl` (timestamp, full tool trace, error
and duplicate counts, final text) — the evaluation dataset for the
chapter's planning-failure metrics.

## Findings

From live runs against the 4 sandbox tickers (2026-07-19):

- **Genuine adaptation:** for ITUB4 (a bank, which returns null
  `totalDebt`/`ebitda`), the agent read `missing_fields` from the fetch
  result and *skipped* `compute_debt_to_ebitda` — 6 calls instead of 7,
  zero errors. Anticipation, not error-recovery.
- **Consistency:** the 3 complete-data tickers got identical plans;
  deviation happened only where context warranted it.
- **Narrative ≠ trace:** the model once claimed it "proceeded to
  fundamentals" after reading technicals, while the trace shows it
  fetched everything upfront. Audit the trace, not the story.
- **v1 vs v2:** identical numbers (shared math), diverging verdicts where
  judgment matters. v1's hard filter structurally fails banks on missing
  data; v2 judged ITUB4 on available data. v1 costs 1 LLM call per
  universe, v2 costs ~12 — the agent's adaptability is bought, not free.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add ANTHROPIC_API_KEY (and BRAPI_TOKEN if you have one)

pytest                 # 32 offline tests, no network, no API key needed
python main.py         # v1 fixed pipeline (4 sandbox tickers, tokenless)
python agent.py PETR4  # v2 dynamic agent (needs ANTHROPIC_API_KEY)
```

The four sandbox tickers (PETR4, MGLU3, VALE3, ITUB4) are served by
[brapi.dev](https://brapi.dev) without a token. Full-IBOV coverage
requires a paid brapi plan.

## Repo map

- `data_provider.py` — brapi.dev HTTP client; field names verified
  against live responses (raw evidence in `fixtures/`)
- `indicators.py` / `fundamentals.py` — deterministic math, pure functions
- `cache.py` — in-memory per-run cache keyed `(ticker, kind)`
- `schemas.py` / `handlers.py` / `agent.py` — the v2 agent
- `screener.py` / `synthesis.py` / `main.py` — the v1 baseline
- `BUILD_PLAN.md`, `TOOLS_GUIDE.md`, `AUDIT_CHECKLIST.md` — the build
  plan, tool design rationale, and audit trail (in Portuguese — session
  working documents)
- `test_screener.py` / `test_agent.py` — offline test suite

---

*Educational project. Nothing here is investment advice.*
