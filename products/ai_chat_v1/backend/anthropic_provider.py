import json
import requests

from config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"


def call_anthropic(messages: list[dict], system: str) -> dict:
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "content-type": "application/json",
    }

    body = {
        "model": MODEL_NAME,
        "max_tokens": MAX_TOKENS,
        "system": system,
        "messages": messages,
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=body, timeout=30)
    if not response.ok:
        raise RuntimeError(f"Anthropic API error {response.status_code}: {response.text}")

    data = response.json()

    return {
        "content": data["content"][0]["text"],
        "input_tokens": data["usage"]["input_tokens"],
        "output_tokens": data["usage"]["output_tokens"],
        "model": data["model"],
    }


def stream_anthropic(messages: list[dict], system: str):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "content-type": "application/json",
    }

    body = {
        "model": MODEL_NAME,
        "max_tokens": MAX_TOKENS,
        "system": system,
        "messages": messages,
        "stream": True,
    }

    input_tokens = 0
    output_tokens = 0
    model = MODEL_NAME

    with requests.post(ANTHROPIC_API_URL, headers=headers, json=body, stream=True, timeout=30) as response:
        if not response.ok:
            raise RuntimeError(f"Anthropic API error {response.status_code}: {response.text}")

        for raw_line in response.iter_lines():
            if not raw_line:
                continue

            line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line

            if not line.startswith("data: "):
                continue

            data_str = line[6:]

            try:
                event = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            event_type = event.get("type")

            if event_type == "message_start":
                input_tokens = event["message"]["usage"]["input_tokens"]
                model = event["message"]["model"]

            elif event_type == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    yield {"token": delta["text"], "done": False}

            elif event_type == "message_delta":
                output_tokens = event["usage"]["output_tokens"]

    yield {"token": "", "done": True, "input_tokens": input_tokens, "output_tokens": output_tokens, "model": model}
