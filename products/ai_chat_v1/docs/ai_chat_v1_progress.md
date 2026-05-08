# ai_chat_v1 — Project Progress

## Current status: Phase 6 complete ✅ — Project published

---

## Phase 1 — Backend Foundation ✅

**Goal:** Server running, routes responding, environment configured.

| Step | File | Status |
|---|---|---|
| Project structure + .gitignore | `.gitignore` | ✅ Done |
| Environment files | `.env`, `.env.example` | ✅ Done |
| Dependencies | `requirements.txt` | ✅ Done |
| Configuration | `backend/config.py` | ✅ Done |
| App entry point | `backend/main.py` | ✅ Done |
| Data models | `backend/models.py` | ✅ Done |
| Chat route (stub) | `backend/chat_router.py` | ✅ Done |

**Verified:** `curl -X POST /chat` returns hardcoded response.

**How to run the server:**
```bash
cd backend
source ../venv/bin/activate
uvicorn main:app --reload
```

---

## Phase 2 — Storage and History ✅

**Goal:** Conversations persist across requests as JSON files on disk.

| Step | File | Status |
|---|---|---|
| Save/load conversations | `backend/storage.py` | ✅ Done |
| Build messages array | `backend/prompt_builder.py` | ✅ Done |
| Chat flow orchestration | `backend/chat_service.py` | ✅ Done |

**Verified:** JSON file grows correctly on each request. Readable on disk. Three test conversations confirmed.

---

## Phase 3 — Anthropic Integration (no streaming) ✅

**Goal:** Real AI responses end-to-end.

| Step | File | Status |
|---|---|---|
| HTTP calls to Anthropic | `backend/anthropic_provider.py` | ✅ Done |
| Add MAX_TOKENS constant | `backend/config.py` (update) | ✅ Done |
| Connect provider to service | `backend/chat_service.py` (update) | ✅ Done |

**Verified:** Full chat flow works via curl. Real AI responses returned. Token counts and model name saved to conversation JSON on every request. Multi-turn history confirmed working.

---

## Phase 4 — Streaming ✅

**Goal:** SSE streaming from backend to client.

| Step | File | Status |
|---|---|---|
| Streaming provider | `backend/anthropic_provider.py` (update) | ✅ Done |
| StreamingResponse route | `backend/chat_router.py` (update) | ✅ Done |
| Yield tokens in service | `backend/chat_service.py` (update) | ✅ Done |

**Verified:** Tokens appear progressively in terminal via `curl -N`. Final `done` event includes token counts. Conversation saved to JSON only after stream fully completes. Both `/chat` (non-streaming) and `/chat/stream` routes coexist.

---

## Phase 5 — Frontend ✅

**Goal:** Working chat in the browser.

| Step | File | Status |
|---|---|---|
| Chat interface | `frontend/index.html` | ✅ Done |
| Styling | `frontend/style.css` | ✅ Done |
| SSE + DOM logic | `frontend/app.js` | ✅ Done |
| Serve frontend from FastAPI | `backend/main.py` (update) | ✅ Done |
| Pass `conversation_id` through done event | `backend/chat_service.py` (update) | ✅ Done |

**Verified:** Full chat works in browser. Responses stream token by token. Blinking cursor animates during streaming. Multi-turn conversation history maintained via `conversationId` in JS memory. Frontend served on same origin as API — no CORS.

---

## Phase 6 — Hardening ✅

**Goal:** Clean, documented, publishable.

| Step | File | Status |
|---|---|---|
| Input validation | `backend/models.py` (Pydantic BaseModel, min/max length) | ✅ Done |
| Error handling | `backend/main.py` (global 422 + 500 handlers) | ✅ Done |
| Startup guard | `backend/config.py` (fail fast on missing API key) | ✅ Done |
| Request timeouts | `backend/anthropic_provider.py` (timeout=30) | ✅ Done |
| Structured logging | `backend/chat_service.py` + `backend/main.py` | ✅ Done |
| README.md | `README.md` | ✅ Done |
| Final .gitignore check | `.gitignore` (conversations/ added) | ✅ Done |
| First GitHub commit | — | ⬜ Pending |

**Verified:** All curl tests passed. 422 on empty message. Tokens logged to stdout. Streaming and non-streaming both working. Browser chat working (message formatting is a known cosmetic issue for a future phase).

**Known issue:** Frontend message formatting — markdown/newlines not rendered. Not blocking for v1.

---

## Files created so far

```
ai_chat_v1/
├── .env                        ✅
├── .env.example                ✅
├── .gitignore                  ✅
├── requirements.txt            ✅
│
├── backend/
│   ├── config.py               ✅
│   ├── main.py                 ✅
│   ├── models.py               ✅
│   ├── chat_router.py          ✅
│   ├── storage.py              ✅
│   ├── prompt_builder.py       ✅
│   ├── chat_service.py         ✅
│   ├── anthropic_provider.py   ✅
│   └── conversations/          ✅ (auto-created, populated)
│
├── README.md                   ✅
│
└── frontend/
    ├── index.html              ✅
    ├── style.css               ✅
    └── app.js                  ✅
```
