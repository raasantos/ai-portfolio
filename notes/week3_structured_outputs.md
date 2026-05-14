# Week 3 — Structured Outputs and Tool Use

**Date:** May 13, 2026
**Resources covered:** job_extractor (experiment) — FastAPI + Anthropic API with tool use · Session with AI Systems Mentor

---

## 10 observations I made

1. **Tool use is an output protocol, not an execution protocol.** The `tools` field instructs the Anthropic API on the format it should use to respond. It executes nothing, accesses no external resources. Your code executes any real action, if there is one. In job_extractor, the tool is just a mold — Anthropic fills it, you read it.

2. **`tool_choice` is the control between forced schema and agent behavior.** With `{"type": "tool", "name": "..."}` you always force a structured output. With `{"type": "auto"}` the model decides whether to use the tool or respond in plain text. This difference defines whether you are doing structured output or building a real agent.

3. **Anthropic returns an array of blocks, not plain text.** The `content` field in the response contains multiple blocks, each with a `type`. With tool use, the relevant block has `type: "tool_use"` and inside it an `input` field with the filled data. You need to find that block — that is what `next()` does.

4. **`system` goes at the root of the payload, not inside `messages`.** Unlike some other APIs that accept `{"role": "system"}` inside the messages array, Anthropic has a separate `system` field at the root level. Putting it in the wrong place either breaks silently or returns a 400 error.

5. **`next()` without a fallback is a silent time bomb.** If Anthropic does not return a `tool_use` block for any reason, `next(block for block in ...)` raises `StopIteration` which can surface somewhere else, far from the origin. `next(..., None)` with an explicit check is the correct pattern — fail fast, readable error.

6. **`requests.raise_for_status()` is explicit fail fast.** Without it, a 401 or 429 status from the API passes silently and the error appears later, hard to trace. With it, the code breaks exactly where the problem is.

7. **FastAPI `app` is an object, not a function.** `app = FastAPI()` instantiates an object of the FastAPI class that implements `__call__`. Uvicorn does not need a function — it needs anything ASGI-compliant. `main:app` tells uvicorn to import the `main` module and use the variable `app`.

8. **A decorator has two completely separate moments.** Registration happens once at server startup — the decorator notes the function in the route table. Execution happens on every request — FastAPI consults the table and calls the function. Conflating these two moments is the root of most misunderstandings about decorators.

9. **Separation of concerns answers the question "where is the bug?".** When something breaks: type error goes to `models.py`, wrong route goes to `router.py`, logic goes to `service.py`, API failure goes to `anthropic_provider.py`. This only works if each file has a single clear responsibility — and breaks down when everything is together.

10. **`**fields` eliminates manual field mapping.** `JobResponse(**fields)` unpacks the dictionary returned by the provider directly into the Pydantic model parameters. If the tool's `input_schema` is aligned with the Pydantic model, there is no field-by-field mapping. Keeping consistency between the tool schema and `JobResponse` is what makes this work.

---

## What I still don't understand

- How to refactor `anthropic_provider.py` to be reusable when the project has multiple tools — where the generic HTTP logic lives and where each tool's specific schema lives.
- When Anthropic decides to use a tool vs. respond in plain text with `tool_choice: auto` — what the internal decision criterion is.

---

## How this changes how I think about product

Tool use as a protocol shows up everywhere: n8n, Flowise, LangGraph, agents. What changes between them is the abstraction layer — but the underlying mechanism is the same. Understanding it in raw HTTP makes any abstraction transparent. When I see a "structured output" node in n8n now, I know exactly what it generates in the payload.

Separation of concerns is also a product principle, not just a code pattern. A system where each component answers one specific question is easier to debug, iterate on, and explain to someone else. This applies to agent architecture as much as to Python code.

---

## Open question

In a real agent flow with `tool_choice: auto` and multiple tools available, how does the model decide which tool to use — and what happens when it chooses wrong? What is the fallback strategy?