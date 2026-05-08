# ai_chat_v1

A minimal AI chat app built to learn how foundation model APIs actually work — below the abstraction layer of official SDKs.

## What this is

A working chat interface backed by a Python/FastAPI server that talks directly to the Anthropic API over HTTP (no SDK). Responses stream token-by-token to the browser via Server-Sent Events. Conversation history is stored as JSON files on disk and sent back on every request, since the API is stateless.

Built as a learning project. Every design choice was made to expose how things work, not to hide complexity.

## Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

```bash
# Clone and enter the project
git clone <repo-url>
cd ai_chat_v1

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and set ANTHROPIC_API_KEY=your-key-here
```

## Run

```bash
cd backend
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## API reference

Both endpoints accept `Content-Type: application/json`.

### POST /chat

Blocking — returns the full response once complete.

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?"}' | python3 -m json.tool
```

Response:
```json
{
  "conversation_id": "conv_20250508_...",
  "role": "assistant",
  "content": "...",
  "input_tokens": 42,
  "output_tokens": 128
}
```

### POST /chat/stream

Streaming — returns an SSE stream of tokens as they arrive.

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain embeddings in one sentence."}'
```

Each event: `data: {"token": "...", "done": false}`  
Final event: `data: {"token": "", "done": true, "conversation_id": "...", "input_tokens": 42, "output_tokens": 95, "model": "..."}`

To continue a conversation, pass `conversation_id` from the previous response:

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Can you elaborate?", "conversation_id": "conv_20250508_..."}'
```

## Project structure

```
ai_chat_v1/
├── .env.example              # Required environment variables (template)
├── .gitignore
├── requirements.txt
│
├── backend/
│   ├── main.py               # FastAPI app, logging config, error handlers
│   ├── chat_router.py        # Route definitions (/chat, /chat/stream)
│   ├── chat_service.py       # Business logic orchestration
│   ├── anthropic_provider.py # Direct HTTP calls to Anthropic API
│   ├── prompt_builder.py     # Shapes message history for the API
│   ├── storage.py            # Read/write conversation JSON files
│   ├── models.py             # Pydantic request model with validation
│   ├── config.py             # Environment variable loading
│   └── conversations/        # Auto-created, gitignored
│
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js                # fetch() + ReadableStream SSE consumer
```

## Intentional design choices

**No Anthropic SDK** — The SDK wraps the same HTTP calls made here. Building without it makes the API contract visible: what headers are required, how streaming events are structured, what `content[0]["text"]` means and why it's an array.

**JSON files instead of a database** — One file per conversation, human-readable on disk, no setup required. The tradeoff is no querying and no multi-user support — both acceptable for a local learning project.

**SSE instead of WebSockets** — The chat response is one-directional (server → client). SSE is a plain HTTP response that never closes; it requires no protocol upgrade and works with a standard `fetch()` call. WebSockets add bidirectional complexity that isn't needed here.

**`fetch()` instead of `EventSource`** — The browser's built-in `EventSource` API only supports GET requests. Since the chat endpoint is POST (it carries a JSON body), `fetch()` with `ReadableStream` is the correct tool.
