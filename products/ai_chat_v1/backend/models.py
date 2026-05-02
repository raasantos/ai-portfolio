from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    role: str
    content: str
    timestamp: Optional[str] = None
    model: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


@dataclass
class ChatRequest:
    message: str
    conversation_id: Optional[str] = None