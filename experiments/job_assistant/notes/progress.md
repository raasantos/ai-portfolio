# Progress — job_assistant

## Project Goal
Job search assistant with a complete autonomous function calling cycle using the Anthropic API. The model decides on its own when to call tools, executing job search and fit evaluation against `jobs.json`.

---

## Current State

### Files — done
| File | Status | Purpose |
|---|---|---|
| `models.py` | ✅ Done | `Job` dataclass with all fields |
| `jobs_populator.py` | ✅ Done | Reads Excel → writes `data/jobs.json` |
| `data/jobs.json` | ✅ Populated | Real job listings from Funil_Vagas.sheets.xlsx |
| `tools/__init__.py` | ✅ Created | Empty (marks folder as Python module) |
| `tools/tool_registry.py` | ✅ Done | Defines `search_jobs` and `evaluate_fit` in Anthropic API format |
| `tools/tool_executor.py` | ✅ Done | Executes tools locally against jobs.json |
| `anthropic_provider.py` | ✅ Done | Full loop: POST → tool_use → tool_result → end_turn |
| `main.py` | ✅ Done | Minimal terminal entry point |
| `venv/` | ✅ Created | pandas, openpyxl, httpx, python-dotenv installed |

### Files — pending
| File | Status | Purpose |
|---|---|---|
| `prompt_builder.py` | 🔲 Phase 3 | System prompt with Raphael's profile + XML tags |
| `service.py` | 🔲 Phase 4 | Orchestrates full flow with conversation history |
| `main.py` | 🔲 Phase 4 | Upgrade to multi-turn chat |

---

## Phases

### Phase 1 — Local tools ✅ Done
- [x] `tool_registry.py` — tool definitions
- [x] `tool_executor.py` — tool execution

### Phase 2 — Full function calling cycle ✅ Done
`anthropic_provider.py` with two functions:
- `run(user_message)` — manages the loop: POST → check stop_reason → execute tools → append → repeat
- `_post(messages)` — sends the POST to the API and returns the JSON response

Also added `debug_log.json` output to inspect raw API requests and responses per iteration.

Fixed `tool_registry.py` descriptions — the model was asking the user for the `job_id` instead of calling `search_jobs` first. Lesson: vague descriptions cause wrong model behavior.

---

### Phase 3 — Structured prompt ⬅ next
`prompt_builder.py`: include Raphael's professional profile in the system prompt so the model can evaluate fit without asking the user for their background every time.

Concepts to apply: XML tags for structure, few-shot of the full cycle, chain-of-thought in `evaluate_fit`.

---

### Phase 4 — FastAPI + hardening
`POST /chat` endpoint, multi-turn conversation history in `service.py`, error handling, README.

---

## Dependencies installed in venv
```bash
pip install httpx python-dotenv
# still pending:
pip install pydantic fastapi uvicorn
```

---

## How to resume
1. `cd experiments/job_assistant`
2. `source venv/bin/activate`
3. `python main.py`
4. Next file to create: `prompt_builder.py`
