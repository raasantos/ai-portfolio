from config import MAX_CONTEXT_MESSAGES


SYSTEM_PROMPT = """You are a helpful AI assistant. You are direct, clear, and concise.
You remember the conversation history and refer to it when relevant."""


def build_messages(history: list[dict]) -> list[dict]:
    windowed = history[-MAX_CONTEXT_MESSAGES:]
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in windowed
    ]


def get_system_prompt() -> str:
    return SYSTEM_PROMPT