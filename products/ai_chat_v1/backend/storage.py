import json
import os
from datetime import datetime, timezone


CONVERSATIONS_DIR = "conversations"


def generate_conversation_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"conv_{timestamp}"


def _conversation_path(conversation_id: str) -> str:
    return os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")


def load_conversation(conversation_id: str) -> dict | None:
    path = _conversation_path(conversation_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_conversation(conversation: dict) -> None:
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
    conversation["updated_at"] = datetime.now(timezone.utc).isoformat()
    path = _conversation_path(conversation["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(conversation, f, indent=2, ensure_ascii=False)