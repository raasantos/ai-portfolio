from fastapi import APIRouter
from models import ChatRequest

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest):
    return {
        "conversation_id": "conv_stub",
        "role": "assistant",
        "content": "This is a hardcoded response. AI integration comes in Phase 3.",
        "input_tokens": 0,
        "output_tokens": 0
    }