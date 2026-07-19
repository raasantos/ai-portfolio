"""v2 dynamic agent: the real function-calling loop (Fase 4).

The loop pattern (the pedagogical core of this phase):
  1. call the Messages API with the 7 tools;
  2. if stop_reason == "tool_use", execute every requested tool;
  3. append the assistant turn verbatim + ONE user turn with ALL
     tool_results (splitting them across messages breaks parallel calls);
  4. repeat until the model stops asking for tools.

Guards, mapped to AUDIT_CHECKLIST #7:
- hard MAX_ITERATIONS cap with a loud, visible failure (never a silent
  truncation that looks like a normal completion);
- duplicate-call detection: repeated (tool, input) pairs are still
  executed (reads are idempotent) but flagged in the trace and on stdout;
- tool failures return tool_result with is_error=True so the model can
  self-correct (Reflection and Error Correction) instead of crashing.

Usage: python agent.py [TICKER ...]   (defaults to the sandbox universe)
Requires ANTHROPIC_API_KEY (in .env or the environment).
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from cache import TickerCache
from data_provider import BrapiClient, BrapiError
from handlers import TOOL_HANDLERS, ToolError
from schemas import TOOLS
from universe import get_universe

MODEL = "claude-opus-4-8"
MAX_TOKENS = 16000
MAX_ITERATIONS = 10

SYSTEM_PROMPT = """You are an equity analysis agent for Brazilian stocks (B3/IBOV).

Your tools fetch real market data and compute technical and fundamental
indicators. All math is done by deterministic server-side code — you NEVER
calculate, estimate, or extrapolate any number yourself. You decide which
tools to call, in what order, and when you have enough information; then
you interpret the computed results. If a tool reports a value as missing,
treat it as unavailable — do not guess it.

Workflow constraints:
- fetch_price_history must run for a ticker before any compute_* technical tool.
- fetch_financial_data must run before compute_debt_to_ebitda.
- Never derive ratios from raw values yourself (e.g. never divide
  total_debt by ebitda) — there is a compute tool for that.
- Call only the tools you actually need. If the technical read alone
  already disqualifies the ticker, you may skip the fundamental tools —
  but say explicitly that you skipped them and why.

Deliver, for the ticker analyzed:
1. A short technical read (trend, momentum, volume context).
2. A short fundamental read (valuation, profitability, leverage) — or the
   reason you skipped it.
3. A recommendation: Watchlist / Neutral / Avoid, naming the one or two
   decisive factors.
End with a one-line disclaimer that this is an educational exercise, not
investment advice."""


@dataclass
class AgentResult:
    ticker: str
    final_text: str
    trace: list[dict] = field(default_factory=list)
    iterations: int = 0
    hit_iteration_cap: bool = False


RUNS_LOG = Path(__file__).parent / "runs.jsonl"


def log_run(result: AgentResult, path: Path = RUNS_LOG) -> None:
    """Append one run as a JSON line — the evaluation dataset.

    Failure Modes & Evaluation: the planning metrics (invalid calls, bad
    parameters, redundancy, consistency across runs) are all AGGREGATE
    questions, and aggregates need persisted traces — a trace that only
    lives on stdout dies with the process. Every live run recorded here
    becomes a data point for free.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": MODEL,
        "ticker": result.ticker,
        "iterations": result.iterations,
        "hit_iteration_cap": result.hit_iteration_cap,
        "tool_calls": len(result.trace),
        "error_calls": sum(1 for t in result.trace if t["is_error"]),
        "duplicate_calls": sum(1 for t in result.trace if t["duplicate"]),
        "trace": result.trace,
        "final_text": result.final_text,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def execute_tool(
    name: str, tool_input: dict, brapi_client: BrapiClient, cache: TickerCache
) -> tuple[dict, bool]:
    """Run one tool call; never raises. Returns (result, is_error)."""
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return {"error": f"Unknown tool: {name}"}, True
    try:
        return handler(brapi_client, cache, dict(tool_input)), False
    except KeyError as exc:
        # The model emitted an input missing a required field (possible
        # without strict tool use). This must surface as a failed call the
        # model can retry — a crash here would kill the whole run over one
        # malformed request.
        return {"error": f"Missing required parameter: {exc}"}, True
    except (ToolError, BrapiError, ValueError, TypeError) as exc:
        # ToolError: bad state (empty cache); BrapiError: upstream API;
        # ValueError/TypeError: bad parameter values or types.
        # All are actionable messages the model can react to.
        return {"error": str(exc)}, True


def run_agent(
    ticker: str,
    *,
    brapi_client: BrapiClient | None = None,
    cache: TickerCache | None = None,
    anthropic_client=None,
) -> AgentResult:
    brapi_client = brapi_client or BrapiClient()
    cache = cache if cache is not None else TickerCache()
    anthropic_client = anthropic_client or anthropic.Anthropic()

    messages: list[dict] = [
        {"role": "user", "content": f"Analyze {ticker} and give your recommendation."}
    ]
    trace: list[dict] = []
    seen_calls: set[tuple[str, str]] = set()

    for iteration in range(1, MAX_ITERATIONS + 1):
        response = anthropic_client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            return AgentResult(ticker, final_text, trace, iteration, False)

        # Assistant turn goes back verbatim: thinking + tool_use blocks
        # must be preserved for the next request to be valid.
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            call_key = (block.name, json.dumps(block.input, sort_keys=True))
            duplicate = call_key in seen_calls
            seen_calls.add(call_key)
            if duplicate:
                print(f"  WARNING duplicate call: {block.name}({block.input})")

            result, is_error = execute_tool(block.name, block.input, brapi_client, cache)
            trace.append(
                {
                    "iteration": iteration,
                    "tool": block.name,
                    "input": dict(block.input),
                    "is_error": is_error,
                    "duplicate": duplicate,
                }
            )
            status = " -> ERROR" if is_error else ""
            print(f"  [{iteration}] {block.name}({block.input}){status}")

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                    "is_error": is_error,
                }
            )

        # ALL results from this iteration go back in ONE user message.
        messages.append({"role": "user", "content": tool_results})

    print(
        f"ERROR: {ticker}: hit MAX_ITERATIONS={MAX_ITERATIONS} without a final "
        "answer — treat this run as failed, do not trust partial output."
    )
    return AgentResult(ticker, "", trace, MAX_ITERATIONS, True)


def main() -> None:
    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY not set (in .env or the environment).")

    tickers = [t.upper() for t in sys.argv[1:]] or get_universe()
    brapi_client = BrapiClient()
    anthropic_client = anthropic.Anthropic()
    # One cache shared across tickers on purpose: screening a second ticker
    # must not reuse the first one's data — AUDIT_CHECKLIST #7 asks us to
    # verify exactly that, and a per-ticker cache would hide the bug.
    cache = TickerCache()

    for ticker in tickers:
        print(f"\n=== {ticker} ===")
        result = run_agent(
            ticker,
            brapi_client=brapi_client,
            cache=cache,
            anthropic_client=anthropic_client,
        )
        # Log BEFORE the cap check: failed runs are the most valuable
        # evaluation data, not the ones to drop.
        log_run(result)
        if result.hit_iteration_cap:
            continue
        print(f"\n{result.final_text}")
        print(f"\n  ({result.iterations} iterations, {len(result.trace)} tool calls)")


if __name__ == "__main__":
    main()
