# ai_chat_v1 — Rules & Learnings

## Project Rules

### 1. Import verification rule
Before writing any file that imports from another project file, Claude must use the `view` tool to read that file first. No exceptions.
This rule exists because writing imports from memory leads to name mismatches and broken code. The `view` tool makes this verifiable — if Claude writes an import without reading the source file first, the rule is broken.

---

## Learnings from Phase 1

### How `uvicorn backend.main:app` works
- `backend.main` is a Python module path — "go into the `backend` folder, find `main.py`"
- `:app` means "grab the variable called `app` inside that file"
- When running from inside `backend/`, the command simplifies to `uvicorn main:app`

### What a decorator is
- The `@` syntax wraps a function to add behavior without modifying it
- `@app.get("/health")` registers the function in FastAPI's routing table
- It's shorthand — `@decorator` on a function is equivalent to `function = decorator(function)`

### How FastAPI works
- Maps URLs to Python functions using decorators
- Automatically parses JSON bodies and validates them against type hints
- Handles HTTP plumbing (status codes, headers, content-type) so you write only the logic
- Uses `APIRouter` to keep routes in separate files from the main app entry point

### How your computer acts as an HTTP server
- An HTTP server is just a program listening on a network port
- `localhost` means "this machine" — requests don't leave your computer
- The only difference between your laptop and a production server is network exposure
- Any computer can be a server — uvicorn just tells the OS "give me port 8000"

### Why frameworks exist
- They don't enable anything new — raw Python can do everything FastAPI does
- They eliminate repetitive, error-prone plumbing (headers, parsing, validation, routing)
- Same concept across all languages: FastAPI (Python), Express (JS), ASP.NET (C#), Spring (Java)

### Why tools like Supabase exist if APIs are simple
- The API is the easy part — what's hard is everything around it
- Database, authentication, real-time sync, row-level security, file storage
- Supabase bundles infrastructure you'd spend months building
- A PM who has built things manually knows when to use Supabase and when not to

### How to read Python errors
- Read the last line first — it contains the actual error
- `ModuleNotFoundError` means Python can't find the file or name you're importing
- You don't need to understand all of Python to read error messages

### Virtual environments
- `python3 -m venv venv` creates an isolated Python environment
- `source venv/bin/activate` activates it — you'll see `(venv)` in your terminal
- Without it, all projects share packages and versions, which causes conflicts

### .env hygiene
- `.env` holds secrets — never committed to git
- `.env.example` documents what variables are needed — always committed
- `.gitignore` is the safety net — must exist before `.env` is created
- `config.py` is the single source of truth for configuration — no other file reads env vars

### dataclasses
- Python's simplest way to define structured data with named fields and types
- Catches typos at development time that dictionaries would miss at runtime
- `Optional` fields have default values and aren't required

---

## Learnings from Phase 2

### JSON files as persistence
- No database needed for a single-user local project — JSON files are human-readable and debuggable directly on disk
- One file per conversation means each conversation is independent and inspectable without any tooling
- The tradeoff: no querying, no indexing. Fine for v1; a real database becomes necessary the moment you need to search or serve multiple users

### Why UTC for all timestamps
- `datetime.now(timezone.utc).isoformat()` writes timestamps in a universal format
- If you save local time (e.g. BRT), timestamps break when you run the app from a different timezone or deploy it
- UTC everywhere, convert to local time only in the UI

### Context windowing
- LLMs have a finite context window — you can't send unlimited history
- `history[-MAX_CONTEXT_MESSAGES:]` slices the last N messages before sending to the API
- Oldest messages are dropped first; the most recent context is always preserved
- `MAX_CONTEXT_MESSAGES = 20` is a named constant, not a magic number — it documents intent and is tunable via `.env`

### Separation of concerns in practice
- `prompt_builder.py` knows how to shape a list of messages — it knows nothing about HTTP or disk
- `storage.py` knows how to read and write JSON — it knows nothing about the AI
- `chat_service.py` orchestrates: it calls each module in sequence but owns none of their logic
- This means you can swap any one module (e.g. replace JSON with SQLite) without touching the others

---

## Learnings from Phase 3

### The Anthropic API is stateless
- The API has no memory. Every single request must include the full conversation history
- This is why `prompt_builder.py` exists — to rebuild the `messages` array on every call
- The model doesn't "remember" you between requests; your app does

### Why `content[0]["text"]`
- The Anthropic response wraps the text in an array: `"content": [{"type": "text", "text": "..."}]`
- This is because the API supports multiple content blocks in a single response: text, tool results, images
- Even though we only use text in Phase 3, the response format is already designed for future capabilities (tool use in Phase 3+)

### The `anthropic-version` header
- Required on every request: `"anthropic-version": "2023-06-01"`
- This pins the API contract — Anthropic can ship breaking changes to newer versions without affecting clients using an older version header
- Same pattern used by Stripe, GitHub, and most production APIs

### `.env` values always win over code defaults
- `os.getenv("MODEL_NAME", "claude-haiku-4-5-20251001")` reads the `.env` file first
- If `MODEL_NAME` exists in `.env`, the default in the code is ignored entirely
- This means changing a default in `config.py` has no effect if the same key is already set in `.env`
- Always check your `.env` when a config change doesn't seem to take effect

### Model IDs are versioned and deprecate
- `claude-sonnet-4-5-20250514` no longer exists — Anthropic returns a 404 for unknown model IDs
- A 404 on `/v1/messages` means the model name is invalid, not that the URL is wrong
- Always verify model IDs against current documentation before hardcoding them

### Better error handling: include the response body
- `response.raise_for_status()` raises an exception but gives you only the HTTP status code
- `if not response.ok: raise RuntimeError(f"... {response.text}")` includes Anthropic's actual error message
- This turns a cryptic `404 Not Found` into `model: claude-sonnet-4-5-20250514` — immediately actionable

### `requests.post()` with `json=body`
- Passing `json=body` automatically serializes the dict to JSON and sets `Content-Type: application/json`
- You don't need to call `json.dumps()` manually or set the header yourself
- Contrast with `data=body`, which sends form-encoded data — wrong for API calls

---

## Learnings from Phase 4

### What SSE (Server-Sent Events) actually is
- SSE is a plain HTTP response that never closes — the server keeps writing to it
- Each event is a line starting with `data: ` followed by a newline, separated from the next event by a blank line
- The browser has a built-in `EventSource` API that reads these events natively — no library needed
- SSE is one-directional (server → client). For two-way communication you'd use WebSockets, but for chat responses SSE is simpler and sufficient

### How the Anthropic streaming response is structured
- Adding `"stream": True` to the request body switches the API to SSE mode
- Anthropic sends a sequence of typed events: `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`
- Only two events matter for basic streaming:
  - `content_block_delta` → contains `delta.text` with the next token
  - `message_start` → contains `input_tokens` (usage at the start)
  - `message_delta` → contains `output_tokens` (usage at the end)
- All other events (`ping`, `content_block_start`, etc.) can be safely ignored

### `requests.post(..., stream=True)` and `iter_lines()`
- `stream=True` tells `requests` not to download the full response body at once — keeps the connection open
- `response.iter_lines()` yields each line as it arrives, blocking until the next one appears
- Using `with requests.post(... stream=True) as response:` ensures the connection is properly closed even if an error occurs mid-stream
- `iter_lines()` returns bytes by default — must decode: `line.decode("utf-8")`

### Python generators and `yield`
- A function with `yield` is a generator — it doesn't run until iterated
- Each `yield` pauses the function and hands a value to the caller; execution resumes from that point on the next iteration
- This is exactly what makes streaming possible: `stream_anthropic()` yields tokens one at a time, `stream_chat()` re-yields them as SSE strings, and FastAPI's `StreamingResponse` sends each one to the client immediately
- The code after the last `yield` in `stream_chat()` (saving the conversation) runs only after the stream is fully consumed — this is why storage always has the complete message

### Why save only after the stream completes
- If the stream fails halfway, you'd save a partial message to disk — corrupted history
- Accumulating `full_content` as tokens arrive and saving at the end is the safe pattern
- The tradeoff: if the server crashes after streaming but before saving, the message is lost. For v1 this is acceptable; production systems use a write-ahead log or transactional approach

### FastAPI `StreamingResponse`
- Wraps any Python generator (or iterator) and sends each yielded value to the client as it arrives
- `media_type="text/event-stream"` sets the correct Content-Type header, which tells the browser this is an SSE stream
- The route function returns the `StreamingResponse` object immediately — FastAPI then pulls from the generator in the background

### `curl -N` for testing streams
- By default, curl buffers output until the connection closes — you'd see all tokens arrive at once at the end
- `-N` (or `--no-buffer`) disables buffering, making each token visible as it arrives
- This is only a curl behavior — browsers and `EventSource` don't buffer; they process events as they arrive

---

## Learnings from Phase 5

### Why `fetch()` + `ReadableStream` instead of `EventSource`
- The browser has a built-in `EventSource` API for SSE — but it only works with GET requests
- Our `/chat/stream` endpoint is POST (it receives a JSON body), so `EventSource` can't be used
- Instead: `fetch()` returns a `Response` whose `.body` is a `ReadableStream`; calling `.getReader()` gives a cursor that yields raw bytes as they arrive
- This pattern works for any SSE endpoint regardless of HTTP method

### The text buffer pattern for SSE in JavaScript
- `fetch()` + `ReadableStream` yields raw byte chunks — not clean lines
- A chunk can contain multiple SSE lines, or a line can be split across two chunks
- Fix: accumulate into a string buffer, split on `\n`, keep the last (possibly incomplete) piece in the buffer, process only complete lines
- Without this pattern, `JSON.parse()` will crash on half-delivered lines

### FastAPI `StaticFiles` — same-origin frontend serving
- `app.mount("/", StaticFiles(directory=..., html=True), name="frontend")` tells FastAPI to serve the frontend at `"/"` after all API routes
- `html=True` makes `index.html` the default response for `/` — no need to navigate to `/index.html`
- Because the frontend is served from the same origin as the API, there's no CORS issue — all `fetch()` calls go to the same host and port
- The mount must come after `include_router()` — FastAPI matches routes in order, and `StaticFiles` is a catch-all

### `Path(__file__)` for path resolution
- `Path(__file__).parent.parent / "frontend"` constructs the frontend path relative to `main.py` itself
- This means the server works regardless of where `uvicorn` is launched from (`/backend`, `/`, or anywhere else)
- Hardcoding `"../frontend"` would only work if you always run from `backend/` — fragile in practice

### Passing `conversation_id` through the SSE done event
- The frontend needs to know the `conversation_id` to maintain multi-turn context — but the ID is generated server-side
- The pattern: include `conversation_id` in the final SSE `done` event; the frontend reads it and stores it in a JS variable
- On every subsequent message, the frontend sends `conversation_id` back in the POST body — the server looks it up and appends to the existing history
- This is how stateless HTTP achieves stateful conversations: the client holds the session key

### CSS `::after` pseudo-element for the streaming cursor
- `.message.assistant.streaming::after { content: "▌"; animation: blink 0.8s step-end infinite; }` adds a blinking cursor with no JavaScript
- `::after` inserts virtual content after an element — it doesn't exist in the DOM, so it can't be accidentally overwritten by `textContent` assignments
- `step-end` makes the animation snap between states (visible/invisible) instead of fading — which is correct for a cursor blink
- The class is added when streaming starts and removed when the `done` event arrives

### Disabling input during streaming
- `input.disabled = !enabled` and `sendBtn.disabled = !enabled` prevent the user from sending a second message while the first is still streaming
- Without this, the user could create overlapping requests that each try to append to the same conversation concurrently — corrupted history
- This is a UX guardrail that also enforces a backend invariant: one active request per conversation at a time

---

## Learnings from Phase 6

### Pydantic is FastAPI's native validation layer
- Converting `ChatRequest` from a `dataclass` to a Pydantic `BaseModel` with `Field(..., min_length=1, max_length=2000)` gives automatic validation on every request
- When a request violates a constraint, FastAPI returns a `422 Unprocessable Entity` before your code runs — zero validation logic needed in the route handler
- This is the right place for input constraints: the data model, not the business logic

### Fail fast at startup
- Adding `if not ANTHROPIC_API_KEY: raise ValueError(...)` in `config.py` means a misconfigured environment crashes at startup, not on the first user request
- A crash at startup is visible immediately to the developer; a 500 at request time is invisible until someone uses the app
- Fail fast is a general principle: detect invalid state as early as possible, as close to the source as possible

### Global exception handlers — keep error contracts consistent
- Without a handler, FastAPI returns HTML tracebacks on unhandled exceptions — wrong content-type, leaks internals, frontend can't parse it
- `@app.exception_handler(Exception)` catches everything that falls through, returns `{"error": "Internal server error"}` — consistent JSON shape the frontend can always handle
- The real error goes to the server log (`logger.exception`), not to the client — the client gets enough to know something went wrong, nothing more

### `logging.getLogger(__name__)` and why it scales
- `__name__` resolves to the module name (e.g., `chat_service`) — each module gets its own namespaced logger
- `logging.basicConfig()` in `main.py` configures the root logger once; all module loggers inherit that config automatically
- This means you add logging to a new module with one line (`logger = logging.getLogger(__name__)`) and it Just Works — format, level, and output are centrally controlled

### Request timeouts are not optional
- `requests.post(..., timeout=30)` prevents a slow or hung Anthropic connection from blocking a uvicorn worker indefinitely
- Without a timeout, a single bad request can tie up a worker thread until the OS eventually closes the connection — which can take minutes
- 30 seconds is generous for a chat response; if the first token hasn't arrived by then, the request is effectively failed

### `conversations/` must be in `.gitignore` before the first commit
- Conversation files contain the full text of user messages — they are user data, not code
- Once committed to git, they persist in history even after deletion (`git filter-branch` is the only fix)
- The right time to add `backend/conversations/` to `.gitignore` is before the first `git add`, not after
