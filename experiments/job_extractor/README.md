# job_extractor

A learning experiment in **structured outputs** using the Anthropic API — without the official SDK.

## What it is

`job_extractor` is a FastAPI service that takes a raw job posting (plain text) and returns a structured JSON object with fields like company name, job title, salary, required skills, and ATS keywords.

The main learning goal was to understand how **tool use** works at the HTTP level: instead of using the `anthropic` Python SDK, this project calls the Anthropic API directly with `requests`, making the request and response structure explicit.

## Architecture

```
POST /extract_job
      │
      ▼
  router.py        ← receives the request, handles HTTP errors
      │
      ▼
  service.py       ← orchestrates the call, validates the response
      │
      ▼
  anthropic_provider.py  ← makes the HTTP call to Anthropic API
```

## How it works

The service uses **tool use** (also called function calling) to force the model to return structured JSON:

1. A tool schema (`extract_job_fields`) defines the exact fields and types we want.
2. `tool_choice: { type: "tool", name: "extract_job_fields" }` forces the model to always call that tool.
3. The model fills in the tool's input — which is already a validated JSON object.
4. We extract `content[].input` from the response and map it to a Pydantic model.

This is more reliable than asking the model to "return JSON" in free text, because the API enforces the schema on the model's output.

## Extracted fields

| Field | Type | Description |
|---|---|---|
| `empresa` | string | Company name |
| `vaga` | string | Job title |
| `remoto` | boolean | Whether the job is remote |
| `salario_divulgado` | boolean | Whether salary is disclosed |
| `salario` | string (optional) | Salary range, if disclosed |
| `requisitos` | string[] | List of requirements |
| `beneficios` | string[] | List of benefits |
| `skills` | string[] | Required skills |
| `palavras_ats` | string[] | ATS keywords |
| `status_sugerido` | string | Suggested action: `aplicar`, `pesquisar mais`, or `descartar` |

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Running

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

## Testing

```bash
curl -X POST http://localhost:8000/extract_job \
  -H "Content-Type: application/json" \
  -d @test_body.json
```

Or with inline text:

```bash
curl -X POST http://localhost:8000/extract_job \
  -H "Content-Type: application/json" \
  -d '{"text": "Vaga: Engenheiro de Software Sênior. Remoto. Salário: R$15.000. Requisitos: Python, AWS."}'
```

## Key concepts learned

- **Tool use / function calling**: How to define a schema as a tool and force the model to use it, instead of generating free text.
- **HTTP-level API calls**: What the Anthropic API actually looks like under the hood — headers (`x-api-key`, `anthropic-version`), the messages array, and the `content` blocks in the response.
- **Structured outputs without SDK**: The SDK is a convenience layer; the underlying protocol is plain HTTP + JSON.
- **Pydantic for validation**: Using `BaseModel` both to validate the incoming request and to validate the model's output before returning it.
- **Error layering**: Separating network errors, API errors, and schema errors into different HTTP status codes (503, 502, 422).
