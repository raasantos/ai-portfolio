# job_assistant

A terminal assistant that runs a full Anthropic tool-use loop over a local job list. The model decides when to call `search_jobs` and `evaluate_fit`, the tools run locally, and results go back as `tool_result` blocks until the model ends its turn (capped at 10 iterations).

| File | What it does |
|---|---|
| `anthropic_provider.py` | Tool-use loop over plain HTTP (httpx, no SDK). Writes each request and response to `debug_log.json`. |
| `tools/tool_registry.py` | Tool definitions in Anthropic API format. |
| `tools/tool_executor.py` | Runs the tools against the local job list. |
| `jobs_populator.py` | Converts a job-tracking spreadsheet into `data/jobs.json`. |
| `models.py` | `Job` dataclass. |

## Data

`data/jobs.example.json` holds two fictional job postings, so the assistant runs out of the box. If `data/jobs.json` exists, it is used instead. That file, the source spreadsheet and `debug_log.json` contain personal data and are gitignored.

## Run

```bash
pip install httpx python-dotenv pandas openpyxl
cp .env.example .env   # add your ANTHROPIC_API_KEY
python main.py
```
