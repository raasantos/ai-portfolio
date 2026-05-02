# ai_chat_v1 — Project Progress

## Current status: Phase 1 complete ✅ — Ready to start Phase 2

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

## Phase 2 — Storage and History (next)

**Goal:** Conversations persist across requests as JSON files on disk.

| Step | File | Status |
|---|---|---|
| Save/load conversations | `backend/storage.py` | ⬜ Not started |
| Build messages array | `backend/prompt_builder.py` | ⬜ Not started |
| Chat flow orchestration | `backend/chat_service.py` | ⬜ Not started |

**Done when:** JSON file grows correctly on each request. Readable on disk.

---

## Phase 3 — Anthropic Integration (no streaming)

**Goal:** Real AI responses end-to-end.

| Step | File | Status |
|---|---|---|
| HTTP calls to Anthropic | `backend/anthropic_provider.py` | ⬜ Not started |
| Connect provider to service | `backend/chat_service.py` (update) | ⬜ Not started |

**Done when:** Full chat flow works via curl. History correct after each call.

---

## Phase 4 — Streaming

**Goal:** SSE streaming from backend to client.

| Step | File | Status |
|---|---|---|
| Streaming provider | `backend/anthropic_provider.py` (update) | ⬜ Not started |
| StreamingResponse route | `backend/chat_router.py` (update) | ⬜ Not started |
| Yield tokens in service | `backend/chat_service.py` (update) | ⬜ Not started |

**Done when:** Tokens appear progressively in terminal via `curl -N`.

---

## Phase 5 — Frontend

**Goal:** Working chat in the browser.

| Step | File | Status |
|---|---|---|
| Chat interface | `frontend/index.html` | ⬜ Not started |
| Styling | `frontend/style.css` | ⬜ Not started |
| SSE + DOM logic | `frontend/app.js` | ⬜ Not started |

**Done when:** Full chat works in browser with streaming visible.

---

## Phase 6 — Hardening

**Goal:** Clean, documented, publishable.

| Step | Status |
|---|---|
| Input validation | ⬜ Not started |
| Error handling | ⬜ Not started |
| Structured logging | ⬜ Not started |
| README.md | ⬜ Not started |
| Final .gitignore check | ⬜ Not started |
| First GitHub commit | ⬜ Not started |

**Done when:** Clean repository, documented, ready to show.

---

## Files created so far

```
ai_chat_v1/
├── .env                  ✅
├── .env.example          ✅
├── .gitignore            ✅
├── requirements.txt      ✅
│
├── backend/
│   ├── config.py         ✅
│   ├── main.py           ✅
│   ├── models.py         ✅
│   └── chat_router.py    ✅
│
├── frontend/             (empty — Phase 5)
│
└── conversations/        (empty — Phase 2)
```
