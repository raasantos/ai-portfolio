from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models import ChatRequest
from chat_service import handle_chat, stream_chat

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest):
    return handle_chat(request)


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    return StreamingResponse(stream_chat(request), media_type="text/event-stream")