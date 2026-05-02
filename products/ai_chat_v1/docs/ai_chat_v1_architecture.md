# ai_chat_v1 — Architecture & Implementation Plan

**Project:** ai_chat_v1
**Author:** Raphael Santos
**Started:** May 2026
**Purpose:** Learning project — build a full AI chat from scratch using Python + FastAPI + Anthropic API, with no SDK abstractions, no database, and no over-engineering.

---

## 1. Goals

- Understand what happens below the abstraction layer of tools like n8n and Flowise
- Build a working chat with real conversation history management
- Implement streaming (SSE) in a real interface
- Practice provider abstraction and separation of responsibilities
- Produce a clean, documented GitHub portfolio artifact

---

## 2. What this is NOT

- Not a production system
- Not a multi-user platform
- Not an SDK tutorial
- Not a framework showcase

---

## 3. Technology stack

| Layer | Choice | Reason |
|---|---|---|
| Backend | Python + FastAPI | Already studying Python; FastAPI has native SSE support |
| Frontend | HTML + CSS + JavaScript (no framework) | Focus on backend/AI learning; SSE is easier to control |
| AI Provider | Anthropic API (direct HTTP, no SDK) | Consistency with learning path — understand the wire |
| Persistence | JSON files on disk | No database needed in v1; history is readable and debuggable |
| Config | python-dotenv + .env | Standard practice; keeps secrets out of code |
| Streaming | Server-Sent Events (SSE) | Native to HTTP; works without WebSocket complexity |

---

## 4. Architecture overview

```
Browser (HTML + JS)
      |
      | HTTP POST /chat         (send message)
      | GET  /chat/stream       (receive streaming response via SSE)
      |
      v
FastAPI Backend
      |
      |-- chat_router.py        (routes only — thin, no business logic)
      |-- chat_service.py       (orchestrates the full chat flow)
      |-- prompt_builder.py     (builds the messages array for the API)
      |-- anthropic_provider.py (calls Anthropic API — streaming and non-streaming)
      |-- storage.py            (reads and writes conversation history to JSON)
      |-- config.py             (loads environment variables)
      |
      v
Local disk (conversations/*.json)
      |
      v
Anthropic API (api.anthropic.com)
```

---

## 5. Folder structure

```
ai_chat_v1/
├── .env                        # secrets — never commit
├── .env.example                # template — commit this
├── .gitignore
├── README.md
├── requirements.txt
│
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # loads .env, exposes settings
│   ├── chat_router.py          # HTTP routes
│   ├── chat_service.py         # business logic and flow orchestration
│   ├── prompt_builder.py       # builds messages array from history
│   ├── anthropic_provider.py   # HTTP calls to Anthropic (streaming + regular)
│   ├── storage.py              # save/load conversation JSON files
│   └── models.py               # data classes (ChatRequest, Message, etc.)
│
├── frontend/
│   ├── index.html              # chat interface
│   ├── style.css               # minimal styling
│   └── app.js                  # handles input, SSE connection, DOM updates
│
└── conversations/              # auto-created; stores conversation JSON files
    └── {conversation_id}.json
```

---

## 6. Data model (no database — plain JSON)

### Conversation file: `conversations/{id}.json`

```json
{
  "id": "conv_20260501_143022",
  "created_at": "2026-05-01T14:30:22Z",
  "updated_at": "2026-05-01T14:35:10Z",
  "messages": [
    {
      "role": "user",
      "content": "What is RAG?",
      "timestamp": "2026-05-01T14:30:22Z"
    },
    {
      "role": "assistant",
      "content": "RAG stands for Retrieval-Augmented Generation...",
      "timestamp": "2026-05-01T14:30:25Z",
      "model": "claude-sonnet-4-5",
      "input_tokens": 18,
      "output_tokens": 142
    }
  ]
}
```

Key decisions:
- One file per conversation
- Each message stores role, content, and timestamp
- Assistant messages also store model, input_tokens, output_tokens
- This gives you basic observability without a database

---

## 7. Core flow — what happens on each message

```
1. User types message and submits
2. Frontend sends POST /chat with { conversation_id, message }
3. chat_router receives request and calls chat_service
4. chat_service:
   a. loads conversation history from storage
   b. appends new user message
   c. calls prompt_builder to build messages array
   d. calls anthropic_provider (streaming)
   e. streams response back to frontend via SSE
   f. after stream ends, saves full assistant message to storage
5. Frontend receives SSE tokens and renders them in real time
```

---

## 8. Separation of responsibilities

| File | Owns | Does NOT own |
|---|---|---|
| `chat_router.py` | HTTP request/response, route definitions | Business logic, AI calls |
| `chat_service.py` | Chat flow orchestration, business rules | HTTP details, raw API calls |
| `prompt_builder.py` | Building messages array, system prompt, history windowing | Storage, API calls |
| `anthropic_provider.py` | Anthropic API communication, streaming | Business logic, history |
| `storage.py` | Reading/writing JSON files | Business rules, AI logic |
| `config.py` | Environment variables | Everything else |

---

## 9. Key business rules (live in chat_service.py)

- Maximum messages kept in context window: configurable constant (default: 20)
- Empty messages are rejected before reaching the AI
- System prompt is always injected by prompt_builder — never by the frontend
- conversation_id is generated by the backend if not provided
- Token usage is always saved per assistant message

---

## 10. Streaming implementation

The backend uses FastAPI's `StreamingResponse` with `text/event-stream` content type.

Flow:
```
anthropic_provider opens streaming connection to Anthropic
  -> yields each text_delta token
    -> chat_service yields each token through FastAPI StreamingResponse
      -> frontend EventSource receives each token
        -> app.js appends token to the chat bubble in real time
```

The SSE format sent to the frontend:
```
data: {"token": "RAG", "done": false}

data: {"token": " stands", "done": false}

data: {"token": "", "done": true, "input_tokens": 18, "output_tokens": 142}
```

The final event includes token usage so the frontend can optionally display it.

---

## 11. Provider abstraction

`anthropic_provider.py` is intentionally isolated. It is the only file that knows:
- The Anthropic API URL
- The request payload format
- How to parse SSE events from Anthropic
- What `text_delta` and `input_json_delta` mean

If you want to add OpenAI later, you create `openai_provider.py` with the same interface. `chat_service.py` does not change.

Provider interface (informal, in Python):
```python
# Both providers must implement this signature
async def stream_message(messages: list, system: str, model: str) -> AsyncGenerator[str, None]:
    ...
```

---

## 12. What is explicitly OUT of v1 scope

- Authentication / user accounts
- Rate limiting
- Multiple users
- Database (SQLite, Postgres, etc.)
- Prompt versioning
- Eval system
- Docker / deployment
- React / Next.js frontend
- WebSockets

These are Phase 2+ concerns. Document them as known limitations in the README.

---

## 13. Implementation plan — phased

### Phase 1 — Backend foundation (Day 1)

Goal: server running, routes defined, environment working.

```
1. Create project structure and .gitignore
2. Create .env and .env.example
3. Install dependencies: fastapi, uvicorn, requests, python-dotenv
4. Write config.py — load API key and settings
5. Write main.py — bare FastAPI app
6. Write models.py — ChatRequest, Message data classes
7. Write chat_router.py — POST /chat stub that returns a fixed string
8. Confirm server starts and route responds
```

Deliverable: `curl -X POST /chat` returns a hardcoded response.

---

### Phase 2 — Storage and history (Day 1-2)

Goal: conversations are saved and loaded from disk.

```
1. Write storage.py — save_conversation(), load_conversation(), generate_id()
2. Write prompt_builder.py — takes history list, returns messages array
3. Update chat_service.py — load history, append user message, save
4. Confirm conversation JSON is created and grows correctly on each call
```

Deliverable: conversation history persists across requests. Readable JSON on disk.

---

### Phase 3 — Anthropic integration without streaming (Day 2)

Goal: real AI responses, no streaming yet.

```
1. Write anthropic_provider.py — POST to Anthropic, return text response
2. Update chat_service.py — call provider, save assistant message with token counts
3. Confirm end-to-end: user message in, AI message out, history updated
```

Deliverable: full chat flow working via curl or Postman. No frontend yet.

---

### Phase 4 — Streaming (Day 2-3)

Goal: streaming SSE response from backend to client.

```
1. Update anthropic_provider.py — streaming version using iter_lines()
2. Add GET /chat/stream route in chat_router.py — StreamingResponse
3. Update chat_service.py — yield tokens as they arrive, save full message at end
4. Test streaming with curl:
   curl -N http://localhost:8000/chat/stream?conversation_id=xxx&message=hello
```

Deliverable: tokens appear progressively in terminal. History still correct after stream ends.

---

### Phase 5 — Frontend (Day 3-4)

Goal: working chat interface in the browser.

```
1. Create index.html — input box, send button, message container
2. Create style.css — minimal, readable chat layout
3. Create app.js:
   a. On submit: POST /chat to create user message entry
   b. Open EventSource to /chat/stream
   c. On each SSE event: append token to current assistant bubble
   d. On done event: finalize bubble, show token count if desired
4. Handle loading state and basic error state
5. New conversation button — generates new conversation_id
```

Deliverable: working chat in browser with real-time streaming.

---

### Phase 6 — Hardening (Day 4-5)

Goal: clean, documented, publishable.

```
1. Add input validation — empty message, max length
2. Add basic error handling — Anthropic failures, file read errors
3. Add structured logging — each request, each AI call, token counts
4. Write README.md:
   - What this is
   - How to run it locally
   - Architecture diagram (text-based)
   - Known limitations
   - What comes next
5. Final review of .gitignore — confirm .env is excluded
6. First GitHub commit
```

Deliverable: clean repository, documented, ready to show.

---

## 14. Architectural risks and mitigations

| Risk | Mitigation |
|---|---|
| History grows too large for context window | prompt_builder caps messages at MAX_CONTEXT_MESSAGES constant |
| Streaming partially fails | Save assistant message only after stream ends successfully |
| API key exposed in code | config.py + .env + .gitignore — checked before every commit |
| Business logic in router | chat_router.py contains zero business logic — delegates to service |
| Anthropic format changes | anthropic_provider.py is isolated — only one file to update |

---

## 15. Known limitations (document in README)

- Single user only — no authentication
- No database — history is lost if files are deleted
- No rate limiting — costs are not controlled
- No eval system — response quality is not measured
- No prompt versioning — prompt changes are not tracked
- Local only — not deployed

---

## 16. Definition of done for v1

- [ ] POST /chat accepts message and returns AI response
- [ ] GET /chat/stream streams response token by token via SSE
- [ ] Conversation history persists across requests in JSON files
- [ ] Frontend displays streaming response in real time
- [ ] System prompt is injected by backend, not configurable from frontend
- [ ] Token usage is logged per message
- [ ] .env is gitignored and .env.example exists
- [ ] README explains how to run the project locally
- [ ] Code is clean, named consistently, and responsibilities are separated

---

*Next step: open a dedicated project chat with the software_architect_agent.md system prompt and start Phase 1.*
