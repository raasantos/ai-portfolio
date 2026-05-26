# Learnings — job_assistant

## Session 1 — Python Basics + Architecture

---

### Virtual environment (venv)
- `python3 -m venv venv` creates the virtual environment inside the project
- `source venv/bin/activate` activates it — the prompt shows `(venv)` when active
- Must reactivate every time a new terminal is opened
- Dependencies installed in the venv are isolated from the global Python

---

### Pandas: reading Excel and converting to JSON

**`pd.read_excel(path)`**
Reads the `.xlsx` file and creates a DataFrame — an in-memory table.

**`df.rename(columns={...})`**
Renames columns. Required because names with accents/spaces (`"Data aplicação"`) are unsafe as Python identifiers. Convention: snake_case.

**`df.where(pd.notna(df), None)`**
Empty cells in Excel become `NaN` (a special pandas float). `json.dump` can't serialize `NaN` — this command replaces them with `None`, which becomes `null` in JSON.

**`df.to_dict(orient="records")`**
Converts the entire DataFrame to a list of dicts in one operation — much more efficient than `iterrows()`. Each row becomes a dict.

**Why not use `for` with `iterrows()`?**
`iterrows()` iterates row by row in pure Python. `to_dict` uses C internals — much faster for large datasets.

---

### List comprehension

```python
jobs = [Job(id=f"job_{i+1:03d}", **row) for i, row in enumerate(raw)]
```

Equivalent to a `for` loop with `append`. `enumerate(list)` yields `(index, value)` on each iteration.

---

### `**kwargs` — dictionary unpacking

```python
Job(id="job_001", **row)
```

`**` unpacks the dict as named arguments. Works because the column names match exactly the parameters of the `Job` class.

---

### `with` — context manager

Guarantees the file is closed when exiting the block, even if an error occurs.

---

### `dataclasses.asdict()`

`json.dump` can't serialize custom objects. `dataclasses.asdict()` converts a dataclass to a plain Python dict.

---

### Separation of concerns

Each file has a single responsibility. `models.py` defines what a `Job` is. `jobs_populator.py` knows how to read Excel. Neither needs to know how the other works internally.

**When to create a class vs leave as a dict:**
> Create a class when the data has behavior or will be manipulated by code. Leave as a dict when it's just static configuration being sent somewhere else.

---

## Session 1 — Phase 1: Function Calling

### The `tools` format in the Anthropic API

Each tool is a dict with three fields: `name`, `description`, `input_schema`.

- **`description`** — most important field. The model reads this to decide *when* to call the tool. Vague description = wrong calls.
- **`input_schema`** — follows JSON Schema. `required` lists mandatory fields.

**`tool_registry.py`** — only defines the tool catalog. Executes nothing.
**`tool_executor.py`** — executes the tool. Knows nothing about the Anthropic API.
The two files are independent — you are responsible for keeping them in sync.

### Design: why does `evaluate_fit` only receive `job_id`?
Pass only the identifier, let the executor fetch the rest. Passing redundant fields would risk inconsistency.

---

## Session 2 — Phase 2: The Function Calling Loop

### The model does not execute tools — it pauses and asks your code to do it

This is the most important concept of function calling. When the model decides to call a tool, it does not have access to your code or `jobs.json`. It stops generating text and returns:

```json
{"stop_reason": "tool_use", "content": [{"type": "tool_use", "name": "search_jobs", "input": {"query": "spotify"}}]}
```

Your code reads this, calls `execute_tool`, gets the result, and sends it back. The model never touched `jobs.json`.

### `stop_reason` — why the model stopped

- `"tool_use"` — model is handing control back to your code to execute a tool
- `"end_turn"` — model is satisfied and returning the final text response

### The `messages` array grows — the API is stateless

The API remembers nothing between calls. Your code accumulates the full conversation history in the `messages` array and sends everything from scratch on every POST.

```
Iteration 1: [user]
Iteration 2: [user, assistant (tool_use), user (tool_result)]
Iteration 3: [user, assistant, user, assistant (tool_use), user (tool_result)]
```

### `role: user` vs `role: assistant`

- `role: assistant` — always written by the Anthropic API
- `role: user` — always written by your code (including `tool_result` entries)

The API doesn't know it's your code sending the tool results — it just sees a `user` message.

### `MAX_ITERATIONS` — the emergency brake

Without a limit, a bug or bad tool description could cause the model to call tools in an infinite loop, burning API credits. The limit stops the loop after N iterations regardless.

### Tool descriptions determine model behavior

In practice: the model was asking the user for the `job_id` instead of calling `search_jobs` first, because the description didn't make the dependency clear. Fixing the description fixed the behavior — no code change needed.

Rule: when the model does something unexpected, check the descriptions before changing the code.

### `is_error: True` in `tool_result`

When a tool fails, don't crash the loop. Return the error as a `tool_result` with `"is_error": True`. The model reads it and decides what to do — it may try a different approach or explain the failure to the user.

### `_post` vs `run` — separation of concerns

- `_post` handles only HTTP communication. If you swap `httpx` for the Anthropic SDK tomorrow, only `_post` changes.
- `run` handles only loop logic. It doesn't know how the POST is made.

### The `tools` array is sent on every POST, outside of `messages`

```json
{
  "model": "...",
  "tools": [...],    ← sent every iteration, outside messages
  "messages": [...]  ← grows with each iteration
}
```

The model receives the full tool catalog fresh on every call and reasons from the accumulated history.
