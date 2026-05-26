import httpx
import json
import os
from dotenv import load_dotenv
from tools.tool_registry import get_tools
from tools.tool_executor import execute_tool

load_dotenv()

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.getenv("MODEL_NAME", "claude-haiku-4-5-20251001")
API_KEY = os.getenv("ANTHROPIC_API_KEY")
MAX_ITERATIONS = 10

_debug_log = []


def _save_debug_log():
    with open("debug_log.json", "w") as f:
        json.dump(_debug_log, f, indent=2, ensure_ascii=False)


def run(user_message: str) -> str:
    _debug_log.clear()
    messages = [{"role": "user", "content": user_message}]

    for _ in range(MAX_ITERATIONS):
        response = _post(messages)
        stop_reason = response["stop_reason"]

        if stop_reason == "end_turn":
            _save_debug_log()
            for block in response["content"]:
                if block["type"] == "text":
                    return block["text"]

        if stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response["content"]})

            tool_results = []
            for block in response["content"]:
                if block["type"] == "tool_use":
                    try:
                        result = execute_tool(block["name"], block["input"])
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block["id"],
                            "content": result,
                        })
                    except Exception as e:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block["id"],
                            "content": str(e),
                            "is_error": True,
                        })

            messages.append({"role": "user", "content": tool_results})

    return "Limite de iterações atingido."


def _post(messages: list) -> dict:
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": 1024,
        "tools": get_tools(),
        "messages": messages,
    }
    response = httpx.post(API_URL, headers=headers, json=body, timeout=30)
    response.raise_for_status()
    result = response.json()

    _debug_log.append({
        "request": body,
        "response": result,
    })

    return result
