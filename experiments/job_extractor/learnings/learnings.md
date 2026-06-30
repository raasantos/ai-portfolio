# Learnings — Job Extractor

Session walkthrough covering architecture, Anthropic Tool Use via raw HTTP, Pydantic, and FastAPI routing patterns.

---

## 1. Project Architecture

**What it does:** A REST API that receives raw job posting text and returns structured data (company, role, salary, skills, etc.) using Claude as the extraction engine.

**Learning goal:** Practice Structured Outputs via raw HTTP (no SDK) and Tool Use with the Anthropic API.

**Layers:**

```
POST /extract_job
      ↓
  router.py       → validates input, maps errors to HTTP status codes
      ↓
  service.py      → orchestrates the logic
      ↓
anthropic_provider.py  → calls Anthropic API via raw HTTP
      ↓
  Anthropic API (Claude Haiku)
      ↓
  models.py       → validates and structures the response with Pydantic
      ↓
  Structured JSON back to the user
```

**File responsibilities:**

| File | Responsibility |
|---|---|
| `router.py` | HTTP endpoint, error-to-status-code mapping |
| `service.py` | Orchestration: calls provider, validates with Pydantic |
| `anthropic_provider.py` | Raw HTTP client for the Anthropic API (no SDK) |
| `models.py` | Input schema (`JobRequest`) and output schema (`JobResponse`) |

---

## 2. anthropic_provider.py — Key Concepts

### Environment variables and load_dotenv

```python
from dotenv import load_dotenv
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

`load_dotenv()` reads the `.env` file and injects its values into the process environment. `os.getenv()` only works after `load_dotenv()` has run. Order matters.

### Why TOOL is a constant, not a function

```python
TOOL = {
    "name": "extract_job_fields",
    "description": "...",
    "input_schema": { ... }
}
```

`TOOL` is a **static schema** — it describes which fields Claude must fill in. It has no logic, no parameters, nothing that changes at runtime. In Python, constants (uppercase by convention) are used for values that are defined once and never change. A function would only make sense if the schema varied at runtime (e.g., different fields per job type).

### Forced Tool Use

```python
"tool_choice": {"type": "tool", "name": "extract_job_fields"}
```

Instead of asking Claude to "return JSON", the code forces Claude to call a specific tool. This **guarantees structured output** — Claude cannot return free text, it can only fill in the fields defined in the tool schema.

### The tool_use block

The Anthropic API doesn't return a single `"result"` field. It returns a `content` array with blocks of different types. Example:

```json
{
  "content": [
    { "type": "text", "text": "Sure, I'll extract the fields..." },
    {
      "type": "tool_use",
      "name": "extract_job_fields",
      "input": {
        "empresa": "Neogrid",
        "vaga": "Data Analyst",
        ...
      }
    }
  ]
}
```

The code scans this array to find the `tool_use` block:

```python
tool_block = next(
    (block for block in data["content"] if block["type"] == "tool_use"),
    None
)
return tool_block["input"]
```

The `input` field contains exactly the fields defined in the TOOL schema.

### Multiple tools

If you had more than one tool, you'd use separate constants and pass them as a list:

```python
TOOL_EXTRACT = { "name": "extract_job_fields", ... }
TOOL_SCORE   = { "name": "score_candidate_fit", ... }

"tools": [TOOL_EXTRACT, TOOL_SCORE],
"tool_choice": {"type": "auto"}  # Claude decides which to use
```

### Why the payload is inside extract_with_tool

The current design is intentionally simple — one function, one tool, one use case. Separating the payload into a `_build_payload()` helper would be premature abstraction: more code with no real benefit for a single-tool project. If a second tool with different parameters were added, the separation would start to pay off.

---

## 3. input_schema — The Correct Perspective

`input_schema` is named from the **tool's perspective**, not the caller's.

Tool Use is modeled as a **function call**:
- You are the code that **defines** the function (name + expected parameters).
- Claude is the code that **calls** the function, filling in the parameters.
- `input_schema` is the schema for the parameters the function receives as input.

That's why the response block is also called `tool_use.input` — those are the arguments Claude "passed" when calling the function.

**Why it looks like output but is named input:**

The full Tool Use flow would be:
```
1. You define the tool (with input_schema)
2. Claude calls the tool, filling in the input
3. Your app executes the tool with that input
4. Your app returns the result to Claude to continue the conversation
```

In this project, steps 3 and 4 never happen. The `input` is intercepted and used directly as structured data. It's a shortcut: using Tool Use only for its side effect of forcing structured JSON, without actually executing any function.

---

## 4. models.py and Pydantic

### What Pydantic solves

Without Pydantic, you validate data manually:

```python
if "text" not in body:
    return error(400, "text field required")
if not isinstance(body["text"], str):
    return error(400, "text must be a string")
if len(body["text"]) > 20000:
    return error(400, "text too long")
```

With Pydantic, you declare the contract once:

```python
class JobRequest(BaseModel):
    text: str = Field(..., max_length=20000)
```

And it handles all validation automatically, raising `ValidationError` with a clear message if the data doesn't match.

### Three field types in models.py

```python
empresa: str                    # required, no default
salario: Optional[str] = None   # optional, defaults to None (null in JSON)
text: str = Field(..., max_length=20000)  # required with extra constraints
```

- **No default** → required
- **`Optional[str] = None`** → can be absent, becomes `null` in JSON
- **`Field(...)`** → `...` means required; add rules like `max_length`, `min_length`, `gt`, etc.

### JobRequest vs JobResponse

`JobRequest` — what the user sends (input boundary). `JobResponse` — what the system returns after extraction (output boundary). Both act as data guardians on opposite sides.

---

## 5. router.py — How Models Are Used

```python
@router.post("/extract_job", response_model=JobResponse)
def extract_job_route(request: JobRequest):
```

**`request: JobRequest`** → FastAPI reads the request body and validates it automatically. If `text` is missing or too long, it returns 422 before your function even runs.

**`response_model=JobResponse`** → FastAPI uses this model to serialize the response. Filters out extra fields Claude may have returned and guarantees the output JSON has exactly the fields in the model.

### The three error codes

```python
except ValueError as api_error:
    raise HTTPException(status_code=502, ...)   # Claude API returned an error

except RuntimeError as network_error:
    raise HTTPException(status_code=503, ...)   # Could not reach the API (network)

except ValidationError as schema_error:
    raise HTTPException(status_code=422, ...)   # Claude's output didn't match JobResponse
```

Each error type has a distinct status code for clear debugging: is it a network problem, an API problem, or a data shape problem?

### Complete request flow

```
Request body
    ↓
JobRequest validates (fail → 422 automatic from FastAPI)
    ↓
extract_job(request.text)
    ↓
service.py → anthropic_provider → Claude
    ↓
JobResponse validates Claude's data (fail → 422 manual in except)
    ↓
response_model=JobResponse serializes output JSON
    ↓
200 response to client
```

---

## 6. Flashcards

> Use these as spaced repetition cards. Cover the answer, read the question, then check.

---

**Q: What does `load_dotenv()` do and why must it run before `os.getenv()`?**

A: It reads the `.env` file and injects its key-value pairs into the process environment. `os.getenv()` reads from the environment — if `load_dotenv()` hasn't run yet, the variables aren't there yet.

---

**Q: Why is `TOOL` a module-level constant instead of a function?**

A: Because it's a static schema with no logic, no parameters, and nothing that changes at runtime. Constants (uppercase) represent configuration and structure, not behavior.

---

**Q: What does `"tool_choice": {"type": "tool", "name": "extract_job_fields"}` do?**

A: Forces Claude to call a specific tool instead of responding with free text. This guarantees structured output — Claude can only fill in the fields defined in the tool schema.

---

**Q: What is the `tool_use` block and where does it appear in the response?**

A: It's one of potentially many blocks inside `data["content"]`. It contains `type: "tool_use"`, the tool `name`, and an `input` field with the structured data Claude filled in.

---

**Q: From whose perspective is `input_schema` named?**

A: From the tool's perspective. It describes what the tool **receives as input** when called. Claude fills in those fields as if passing arguments to a function.

---

**Q: In this project, do we ever actually "execute" the tool after Claude calls it?**

A: No. We intercept `tool_use.input` and use it directly as structured data. The tool is never executed — we use Tool Use only to force structured JSON output.

---

**Q: What does `Optional[str] = None` mean in a Pydantic model?**

A: The field can be absent or explicitly `null`. It defaults to `None` and serializes as `null` in JSON. Without the `= None`, `Optional` alone would still require the field to be present.

---

**Q: What's the difference between `empresa: str` and `text: str = Field(..., max_length=20000)`?**

A: Both are required (`...` means required in Field). The second adds an extra constraint (max length). `Field()` is used when you need rules beyond just the type.

---

**Q: What are the two roles of Pydantic models in `router.py`?**

A: `request: JobRequest` → validates and parses the incoming request body. `response_model=JobResponse` → serializes and filters the outgoing response.

---

**Q: What does each HTTP error code mean in this project?**

A: 502 = Anthropic API returned an error (`ValueError`). 503 = Network failure, couldn't reach Anthropic (`RuntimeError`). 422 = Claude's output didn't match the `JobResponse` schema (`ValidationError`).

---

**Q: If you had two tools, how would you structure the code?**

A: Two separate constants (`TOOL_A`, `TOOL_B`) and pass them as a list: `"tools": [TOOL_A, TOOL_B]`. Use `"tool_choice": {"type": "auto"}` to let Claude decide which to call.

---

**Q: Why is the payload built inside `extract_with_tool` instead of a separate helper function?**

A: One tool, one use case — separating it would be premature abstraction. More code with no real benefit at this scale. If a second tool with different parameters were added, a helper would start to make sense.

---

**Q: What is the system prompt in this project and what language is it in?**

A: `"Você é um extrator de dados de vagas de emprego. Extraia os campos estruturados da vaga fornecida."` — Portuguese. It tells Claude to act as a job posting data extractor.

---

**Q: What HTTP headers are required to call the Anthropic API directly?**

A: `x-api-key` (your API key), `anthropic-version` (e.g., `2023-06-01`), `Content-Type: application/json`.

---

**Q: What is the key difference between the Anthropic SDK and what this project does?**

A: The SDK wraps all HTTP details (headers, URL, serialization, error handling) automatically. This project makes the raw `requests.post()` call manually — which is intentional, to understand the underlying protocol.

---

## 7. Quiz

> Multiple choice. Answer before reading the options if you can. Answers at the end.

---

**1. What happens if `load_dotenv()` is called AFTER `os.getenv("ANTHROPIC_API_KEY")`?**

- a) It works fine, Python resolves the order automatically
- b) `os.getenv()` returns `None` because the variable wasn't injected yet
- c) It raises an `ImportError`
- d) The `.env` file is ignored entirely

---

**2. Why does the project raise `RuntimeError` at module load time if `ANTHROPIC_API_KEY` is missing?**

- a) Because Pydantic requires it
- b) To fail fast — catching the problem at startup is better than failing on the first request
- c) FastAPI requires all providers to validate on import
- d) Because `os.getenv()` raises an exception when a variable is missing

---

**3. The `TOOL` constant's `input_schema` defines:**

- a) The format of the HTTP response from the Anthropic API
- b) The fields Claude must fill in when calling the tool — from the tool's perspective
- c) The Pydantic model used to validate the request body
- d) The system prompt structure

---

**4. What would happen if `tool_choice` was set to `{"type": "auto"}` instead of forcing a specific tool?**

- a) The API would return an error — `auto` is not a valid value
- b) Claude might respond with free text instead of calling the tool, breaking the structured output guarantee
- c) Claude would call all defined tools simultaneously
- d) Nothing changes — Claude always calls the tool anyway

---

**5. `tool_block` is found by:**

- a) Accessing `data["tool_use"]` directly on the response
- b) Scanning `data["content"]` for the block with `type == "tool_use"`
- c) Reading the first element of `data["content"]`
- d) Calling `response.tool_block()` from the requests library

---

**6. In `JobResponse`, `salario: Optional[str] = None` means:**

- a) The field is required but can be an empty string
- b) The field is required and must be a string or null
- c) The field is optional and defaults to `None` (null in JSON) if not provided
- d) The field accepts both `str` and `int` types

---

**7. When FastAPI sees `request: JobRequest` in a route function, it:**

- a) Passes the raw request object for manual parsing
- b) Automatically parses and validates the request body using the Pydantic model
- c) Reads the `JobRequest` fields from the URL query parameters
- d) Requires you to call `JobRequest.parse(request)` manually

---

**8. HTTP 503 in this project means:**

- a) The request body failed Pydantic validation
- b) Claude returned a response that didn't match `JobResponse`
- c) The network call to the Anthropic API failed (connection error, timeout)
- d) The Anthropic API returned a non-2xx status code

---

**9. What would you change in `anthropic_provider.py` to add a second tool?**

- a) Add a second function with a new TOOL constant inside it
- b) Define a second constant (e.g., `TOOL_B`) and add it to the `"tools": [TOOL, TOOL_B]` list
- c) Create a subclass of the existing `TOOL` constant
- d) Add a second key inside the existing `TOOL` dict

---

**10. The main reason for building `extract_with_tool` without a separate `_build_payload()` helper is:**

- a) Python doesn't support helper functions inside modules
- b) FastAPI requires all logic to be in a single function per endpoint
- c) There is one tool and one use case — separating it would be premature abstraction
- d) The payload changes every request, so it can't be extracted

---

### Answers

| # | Answer | Why |
|---|---|---|
| 1 | **b** | `os.getenv()` reads from the environment at call time — if `load_dotenv()` hasn't run yet, the variable isn't there |
| 2 | **b** | Fail fast at startup is better than a runtime error on the first user request |
| 3 | **b** | `input_schema` defines what the tool receives — named from the tool's perspective, not the caller's |
| 4 | **b** | `auto` lets Claude choose whether to call a tool at all — structured output is no longer guaranteed |
| 5 | **b** | The response `content` is an array of typed blocks; you scan for `type == "tool_use"` |
| 6 | **c** | `Optional[str] = None` means absent/null by default — the field doesn't need to be in the JSON |
| 7 | **b** | FastAPI reads the type hint and uses Pydantic to parse and validate the body automatically |
| 8 | **c** | `RuntimeError` is raised on `requests.exceptions.RequestException` — network-level failures |
| 9 | **b** | Separate constants, combined in the `tools` list |
| 10 | **c** | Premature abstraction — more code with no benefit for a single-tool project |
