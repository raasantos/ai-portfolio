# Audit Checklist — IBOV Screener (Technical + Fundamental)

This agent has a different risk profile than Agent 1: it touches real
financial data at scale, and a wrong number here isn't just a bug, it's a
number you might act on with real money. Audit accordingly.

## 1. Field-name correctness (the alucination risk this whole exercise exists to catch)

- [x] (verified 2026-07-18 against live pulls, raw evidence in `fixtures/`) Every brapi field name used in `data_provider.py` and `fundamentals.py`
      (`trailingPE`, `dividendYield`, `returnOnEquity`, `totalDebt`, `ebitda`,
      `historicalDataPrice`, `close`, `volume`) — cross-check each one
      against a REAL API response you've pulled yourself, not just against
      this file's comments. Docs and reality can drift.
- [x] (verified 2026-07-18 on live PETR4: 0.06 and 0.2427 are fractions) Confirm `dividendYield` and `returnOnEquity` are genuinely returned as
      fractions (0.03 = 3%) and not already as percentages — the code
      multiplies by 100 in `extract_fundamentals()`. If brapi ever changes
      this convention, every dividend yield and ROE number silently becomes
      100x wrong with no error thrown. This is the single highest-risk line
      in the whole codebase — check it against a live response first.

## 2. Ordering assumptions (silent-failure risk)

- [x] (verified 2026-07-18/19) `indicators.py` assumes prices are
      oldest-to-newest. brapi's documented order has already drifted from
      reality once (docs said newest-first; the live 2026-07-18 pull
      arrived oldest-first), so `parse_historical()` trusts NEITHER claim:
      it sorts explicitly by `date` regardless of API order. Locked in by
      `test_parse_historical_sorts_oldest_first`, which shuffles the real
      fixture before parsing — if anyone removes the sort, that test fails.

## 3. Numeric correctness of hand-written indicators (Tools/Planning: don't trust untested math)

- [x] (verified via `test_rsi_wilder_hand_computed`, hand-worked example) RSI implementation: does it match the textbook Wilder's-smoothing
      formula exactly? Compare `indicators.rsi()` line by line against a
      reference definition, not against "it ran without crashing."
- [x] (PETR4 live: 677/231 = 2.93, plausible real-world leverage) `debt_to_ebitda` is DERIVED (totalDebt / ebitda), not pulled directly
      from brapi. Confirm this ratio actually means what you think it means
      for a few real tickers you already know well from your professional
      background — does the computed number match your intuition for that
      company's real leverage?

## 4. Fixed-pipeline enforcement (the design decision from this session)

- [x] (verified 2026-07-19; re-check on ANY future edit to synthesis.py) Confirm `synthesis.py`'s `client.messages.create()` call has NO
      `tools=` parameter. This is the actual enforcement mechanism for
      "fixed pipeline, not dynamic agent" — if a `tools=` parameter is ever
      added here without a corresponding deliberate design decision, the
      agent silently becomes dynamic again.
- [x] (verified 2026-07-19: `build_signals_payload` serializes ScreenerResult only, which never holds raw arrays) Confirm the LLM in `synthesis.py` never receives raw price arrays or
      raw API payloads — only the already-computed signals dict. If a
      future edit passes raw `closes` or `volumes` into the prompt, the
      LLM could start "eyeballing" trends itself instead of relying on the
      computed indicators, silently reintroducing numeric hallucination
      risk into a pipeline that was specifically designed to avoid it.

## 5. Filter transparency (Failure Modes & Evaluation: opaque scores hide bad calls)

- [ ] `passes_fundamental_filter()` uses hard cutoffs (P/L 0-25, ROE >=10%,
      Dívida/EBITDA <=3.5). Are these actually the right thresholds for
      YOUR use case, or defaults I picked that need your judgment? This is
      explicitly meant to be argued with — pick a few real IBOV tickers you
      have an opinion on and check whether the filter agrees with you.
- [ ] `ScreenerResult.is_shortlisted` requires fundamentals to pass AND at
      least one bullish technical signal. Is "OR" the right logic between
      short-term and medium-term technicals, or should a genuinely
      short-term play need short-term signals specifically (not get
      shortlisted purely on a medium-term crossover)?

Note (2026-07-19): the ITUB4 live run exposed a structural blind spot —
banks return null `totalDebt`/`ebitda`, so the debt/EBITDA gate fails every
bank regardless of quality. Deliberate decision: thresholds unchanged for
now; revisit when the universe expands beyond the 4 sandbox tickers. The
v2 agent handled the same case gracefully (skipped the ratio, judged on
available data) — see Fase 6 comparison in README.md.

## 6. Data quality vs. silent gaps

- [x] (verified: `test_missing_ebitda_fails_filter_explicitly` + ITUB4 live FAIL with explicit reason) If `missing_fields` in `fundamentals.py` is non-empty, the ticker
      still gets a `fundamental_filter` result — verify it correctly FAILS
      the filter (via the `None` checks) rather than passing by accident
      because a `None` comparison happened to evaluate favorably somewhere.
- [x] (verified by code review: `screen_ticker` isolates failures per ticker via separate try/except blocks; no dedicated batch test yet — known acceptable gap) Trace what happens end-to-end if `get_historical()` succeeds but
      `get_statistics()` or `get_financial_data()` fails for only SOME
      tickers in a batch call (partial failure). Does `screener.py`
      correctly mark just those tickers as failed, or does one failing
      ticker's error string leak into every other ticker's `data_errors`?

## 7. Dynamic-agent-specific risks (v2 architecture only)

These apply once the fixed pipeline (`screener.py`/`synthesis.py`) is
replaced by the dynamic tool-selecting agent described in `BUILD_PLAN.md`
v2 and `TOOLS_GUIDE.md`. Skip this section while still on v1.

- [x] (verified 2026-07-19: `MAX_ITERATIONS=10` in agent.py, loud failure + `hit_iteration_cap` flag, `test_loop_hits_iteration_cap_loudly`) **Infinite loop guard.** Does the function-calling loop have a hard
      maximum number of iterations? Without one, a model that keeps
      requesting tools (or requests the same tool with the same
      parameters repeatedly) never terminates. Verify there's an explicit
      cap and that hitting it produces a logged, visible failure — not a
      silent truncation that looks like a normal completion.
- [x] (verified 2026-07-19: 5 live runs in runs.jsonl, zero duplicates, zero compute-before-fetch; loop flags duplicates in the trace) **Redundant tool calls.** For a single ticker, does the agent ever
      call `fetch_price_history` more than once, or call a compute tool
      before the fetch it depends on has run? Check the raw trace, not
      just the final answer — a redundant call that still produces a
      correct final answer is still a cost/latency problem worth knowing
      about.
- [x] (verified 2026-07-19: PETR4/MGLU3/VALE3 in one process sharing one cache, each got its own indicator values; + `test_cache_is_keyed_per_ticker`) **Cache correctness across tickers.** If the server-side cache is
      keyed incorrectly (e.g. a single global slot instead of per-ticker),
      screening a second ticker in the same run could silently return the
      first ticker's data. Test this directly: run two different tickers
      in sequence and confirm the second one's computed indicators
      actually differ from the first's raw inputs.
- [x] (verified 2026-07-19: identical 7-call plans for the 3 complete-data tickers; principled 6-call deviation for ITUB4 — deviation only where context warranted. Sample still small: 5 runs, 1 intra-ticker repetition) **Tool selection consistency.** Run the agent against 2-3 similar
      tickers (same sector, similar fundamentals). Does it make comparable
      tool-selection decisions across them, or does it arbitrarily skip a
      tool for one and not the other with no principled reason visible in
      its reasoning? Inconsistent tool selection with no explanation is a
      planning failure, even if each individual run "worked."
- [x] (verified 2026-07-19: handlers raise ToolError with actionable message, covered by tests; live, the model went one better — read `missing_fields` and skipped the doomed call entirely) **Dependency communicated only via description text.** Confirm
      whether `compute_debt_to_ebitda` actually fails gracefully (clear
      error) when called before `fetch_financial_data`, versus silently
      returning a wrong or default value. A tool description saying "call
      X first" is a suggestion to the model, not an enforced constraint —
      the code must handle the case where the model ignores it.

## How to use this

1. Run against the 4 free sandbox tickers first (`python main.py`), no
   token needed.
2. Pull at least one RAW response per endpoint yourself (curl or Python)
   and manually verify field names/units before trusting anything computed
   downstream — especially item #1 above.
3. Once the free-tier run looks right, decide whether the R$99,99/mo
   Startup plan is worth it for full-IBOV coverage — that's a real budget
   decision, not just a technical one.
