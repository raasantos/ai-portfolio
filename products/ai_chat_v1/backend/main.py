from fastapi import FastAPI
from chat_router import router

app = FastAPI(
    title="ai_chat_v1",
    description="Learning Project - AI chat with streaming and conversation history"
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

