import json
import logging
from datetime import datetime, timezone

from models import ChatRequest

logger = logging.getLogger(__name__)
from storage import load_conversation, save_conversation, generate_conversation_id
from prompt_builder import build_messages, get_system_prompt
from anthropic_provider import call_anthropic, stream_anthropic


def handle_chat(request: ChatRequest) -> dict:
    conversation_id = request.conversation_id or generate_conversation_id()

    conversation = load_conversation(conversation_id) or {
        "id": conversation_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": []
    }

    user_message = {
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    conversation["messages"].append(user_message)

    messages = build_messages(conversation["messages"])
    system = get_system_prompt()

    provider_response = call_anthropic(messages, system)
    assistant_content = provider_response["content"]

    assistant_message = {
        "role": "assistant",
        "content": assistant_content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": provider_response["model"],
        "input_tokens": provider_response["input_tokens"],
        "output_tokens": provider_response["output_tokens"],
    }
    conversation["messages"].append(assistant_message)

    save_conversation(conversation)

    logger.info(
        "conversation=%s input_tokens=%d output_tokens=%d",
        conversation_id,
        provider_response["input_tokens"],
        provider_response["output_tokens"],
    )

    return {
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": assistant_content,
        "input_tokens": provider_response["input_tokens"],
        "output_tokens": provider_response["output_tokens"],
    }


def stream_chat(request: ChatRequest):
    conversation_id = request.conversation_id or generate_conversation_id()

    conversation = load_conversation(conversation_id) or {
        "id": conversation_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": []
    }

    user_message = {
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    conversation["messages"].append(user_message)

    messages = build_messages(conversation["messages"])
    system = get_system_prompt()

    full_content = []
    final_event = {}

    for event in stream_anthropic(messages, system):
        if event["done"]:
            event["conversation_id"] = conversation_id
        yield f"data: {json.dumps(event)}\n\n"
        if not event["done"]:
            full_content.append(event["token"])
        else:
            final_event = event

    assistant_message = {
        "role": "assistant",
        "content": "".join(full_content),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": final_event.get("model"),
        "input_tokens": final_event.get("input_tokens", 0),
        "output_tokens": final_event.get("output_tokens", 0),
    }
    conversation["messages"].append(assistant_message)
    conversation["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_conversation(conversation)

    logger.info(
        "conversation=%s stream complete: input_tokens=%d output_tokens=%d",
        conversation_id,
        final_event.get("input_tokens", 0),
        final_event.get("output_tokens", 0),
    )