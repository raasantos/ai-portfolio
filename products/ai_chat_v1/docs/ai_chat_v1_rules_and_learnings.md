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
