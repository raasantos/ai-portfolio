"""Offline tests for the v2 agent components — no network, no API key.

Covers what AUDIT_CHECKLIST #7 asks for that CAN be verified offline:
cache keyed per ticker, compute-before-fetch failing explicitly, the
iteration cap being loud, and schema/handler parity. Real tool-selection
auditing (Fase 5) still requires live runs.
"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from agent import AgentResult, MAX_ITERATIONS, execute_tool, log_run, run_agent
from cache import FINANCIAL_DATA, HISTORY, TickerCache
from data_provider import parse_financial_data, parse_historical, parse_statistics
from handlers import TOOL_HANDLERS, ToolError
from schemas import TOOL_NAMES, TOOLS

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


class StubBrapiClient:
    """Serves the real PETR4 fixtures for any ticker; records calls."""

    def __init__(self):
        self.calls = []

    def get_historical(self, ticker, range_="3mo", interval="1d"):
        self.calls.append(("historical", ticker, range_))
        return parse_historical(load_fixture("petr4_historical.json"))

    def get_statistics(self, ticker):
        self.calls.append(("statistics", ticker))
        return parse_statistics(load_fixture("petr4_statistics.json"))

    def get_financial_data(self, ticker):
        self.calls.append(("financial", ticker))
        return parse_financial_data(load_fixture("petr4_financial.json"))


# --- schemas ---


def test_every_schema_has_a_handler_and_vice_versa():
    assert set(TOOL_NAMES) == set(TOOL_HANDLERS)


def test_schemas_are_well_formed():
    for tool in TOOLS:
        assert len(tool["description"]) > 40, tool["name"]
        schema = tool["input_schema"]
        assert schema["type"] == "object"
        assert "ticker" in schema["properties"]
        assert "ticker" in schema["required"]


# --- cache (AUDIT #7: per-ticker keying) ---


def test_cache_is_keyed_per_ticker():
    cache = TickerCache()
    cache.put("PETR4", HISTORY, [{"close": 1.0}])
    assert cache.get("VALE3", HISTORY) is None
    assert cache.get("PETR4", HISTORY) == [{"close": 1.0}]


def test_cache_normalizes_ticker_case():
    cache = TickerCache()
    cache.put("petr4 ", HISTORY, "x")
    assert cache.get("PETR4", HISTORY) == "x"


# --- fetch handlers ---


def test_fetch_price_history_returns_summary_never_the_series():
    cache = TickerCache()
    result = TOOL_HANDLERS["fetch_price_history"](
        StubBrapiClient(), cache, {"ticker": "petr4"}
    )
    assert result["data_points"] == 61
    assert result["ticker"] == "PETR4"
    # The model-facing result must not contain any raw array.
    assert not any(isinstance(v, (list, dict)) for v in result.values())
    # But the raw series IS in the server-side cache.
    assert len(cache.get("PETR4", HISTORY)) == 61
    json.dumps(result)  # must be serializable as a tool_result


def test_fetch_fundamental_statistics_normalizes_units():
    result = TOOL_HANDLERS["fetch_fundamental_statistics"](
        StubBrapiClient(), TickerCache(), {"ticker": "PETR4"}
    )
    # Live PETR4 fixture: dividendYield = 0.06 fraction -> 6.0 pct points.
    assert result["dividend_yield_pct"] == pytest.approx(6.0)
    assert result["missing_fields"] == []


# --- compute handlers: explicit error on empty cache ---


@pytest.mark.parametrize(
    "tool", ["compute_moving_average_crossover", "compute_rsi", "compute_relative_volume"]
)
def test_compute_technical_before_fetch_raises_explicit_error(tool):
    with pytest.raises(ToolError, match="fetch_price_history"):
        TOOL_HANDLERS[tool](StubBrapiClient(), TickerCache(), {"ticker": "PETR4"})


def test_compute_debt_to_ebitda_before_fetch_raises_explicit_error():
    with pytest.raises(ToolError, match="fetch_financial_data"):
        TOOL_HANDLERS["compute_debt_to_ebitda"](
            StubBrapiClient(), TickerCache(), {"ticker": "PETR4"}
        )


# --- compute handlers: full fetch -> compute flow ---


def test_technical_flow_fetch_then_compute():
    client, cache = StubBrapiClient(), TickerCache()
    TOOL_HANDLERS["fetch_price_history"](client, cache, {"ticker": "PETR4"})

    rsi_result = TOOL_HANDLERS["compute_rsi"](client, cache, {"ticker": "PETR4"})
    assert 0.0 <= rsi_result["rsi"] <= 100.0

    ma = TOOL_HANDLERS["compute_moving_average_crossover"](
        client, cache, {"ticker": "PETR4"}
    )
    assert ma["position"] in ("above", "below", "equal")
    assert ma["short_window"] == 9 and ma["long_window"] == 21

    vol = TOOL_HANDLERS["compute_relative_volume"](client, cache, {"ticker": "PETR4"})
    assert vol["relative_volume"] > 0
    # Only one upstream fetch happened for all three computes.
    assert client.calls == [("historical", "PETR4", "3mo")]


def test_debt_to_ebitda_flow_matches_verified_value():
    client, cache = StubBrapiClient(), TickerCache()
    TOOL_HANDLERS["fetch_financial_data"](client, cache, {"ticker": "PETR4"})
    result = TOOL_HANDLERS["compute_debt_to_ebitda"](client, cache, {"ticker": "PETR4"})
    # 676977000000 / 230884000000, verified live on 2026-07-18.
    assert result["debt_to_ebitda"] == pytest.approx(2.93, abs=0.01)


# --- execute_tool: malformed requests are errors, never crashes ---


def test_missing_required_parameter_is_error_not_crash():
    # Model emits input without "ticker" (possible without strict mode):
    # must come back as is_error, not a KeyError killing the whole run.
    result, is_error = execute_tool("compute_rsi", {}, StubBrapiClient(), TickerCache())
    assert is_error is True
    assert "ticker" in result["error"]


def test_unknown_tool_is_error_not_crash():
    result, is_error = execute_tool(
        "delete_portfolio", {"ticker": "PETR4"}, StubBrapiClient(), TickerCache()
    )
    assert is_error is True
    assert "Unknown tool" in result["error"]


# --- run persistence (the evaluation dataset) ---


def test_log_run_appends_json_lines(tmp_path):
    log_path = tmp_path / "runs.jsonl"
    result = AgentResult(
        ticker="PETR4",
        final_text="ok",
        trace=[
            {
                "iteration": 1,
                "tool": "compute_rsi",
                "input": {"ticker": "PETR4"},
                "is_error": True,
                "duplicate": False,
            }
        ],
        iterations=2,
        hit_iteration_cap=False,
    )
    log_run(result, path=log_path)
    log_run(result, path=log_path)
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 2
    record = json.loads(lines[0])
    assert record["ticker"] == "PETR4"
    assert record["tool_calls"] == 1
    assert record["error_calls"] == 1
    assert record["duplicate_calls"] == 0
    assert record["hit_iteration_cap"] is False


# --- agent loop (fake Anthropic client, no network) ---


def _text_response(text):
    return SimpleNamespace(
        stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)]
    )


def _tool_response(name, tool_input, tool_id):
    return SimpleNamespace(
        stop_reason="tool_use",
        content=[
            SimpleNamespace(type="tool_use", name=name, input=tool_input, id=tool_id)
        ],
    )


class ScriptedAnthropic:
    """Returns a fixed sequence of responses; repeats the last one after."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.requests = []
        self.messages = self  # so client.messages.create resolves here

    def create(self, **kwargs):
        self.requests.append(kwargs)
        if len(self._responses) > 1:
            return self._responses.pop(0)
        return self._responses[0]


def test_loop_executes_tool_and_finishes():
    fake = ScriptedAnthropic(
        [
            _tool_response("fetch_price_history", {"ticker": "PETR4"}, "tu_1"),
            _text_response("Final answer."),
        ]
    )
    result = run_agent(
        "PETR4",
        brapi_client=StubBrapiClient(),
        cache=TickerCache(),
        anthropic_client=fake,
    )
    assert result.final_text == "Final answer."
    assert result.hit_iteration_cap is False
    assert [t["tool"] for t in result.trace] == ["fetch_price_history"]
    # Second request must carry: user, assistant(tool_use), user(tool_result).
    second_messages = fake.requests[1]["messages"]
    assert [m["role"] for m in second_messages] == ["user", "assistant", "user"]
    tool_result = second_messages[2]["content"][0]
    assert tool_result["type"] == "tool_result"
    assert tool_result["tool_use_id"] == "tu_1"
    assert tool_result["is_error"] is False


def test_loop_reports_tool_errors_instead_of_crashing():
    # compute before fetch -> handler raises ToolError -> is_error result.
    fake = ScriptedAnthropic(
        [
            _tool_response("compute_rsi", {"ticker": "PETR4"}, "tu_1"),
            _text_response("Recovered."),
        ]
    )
    result = run_agent(
        "PETR4",
        brapi_client=StubBrapiClient(),
        cache=TickerCache(),
        anthropic_client=fake,
    )
    assert result.trace[0]["is_error"] is True
    tool_result = fake.requests[1]["messages"][2]["content"][0]
    assert tool_result["is_error"] is True
    assert "fetch_price_history" in tool_result["content"]


def test_loop_hits_iteration_cap_loudly():
    # A model that never stops asking for tools must hit the hard cap
    # and be reported as failed — not returned as a normal completion.
    fake = ScriptedAnthropic(
        [_tool_response("compute_rsi", {"ticker": "PETR4"}, "tu_x")]
    )
    result = run_agent(
        "PETR4",
        brapi_client=StubBrapiClient(),
        cache=TickerCache(),
        anthropic_client=fake,
    )
    assert result.hit_iteration_cap is True
    assert result.final_text == ""
    assert result.iterations == MAX_ITERATIONS
    assert len(result.trace) == MAX_ITERATIONS
    # Identical repeated calls are flagged as duplicates in the trace.
    assert all(t["duplicate"] for t in result.trace[1:])
