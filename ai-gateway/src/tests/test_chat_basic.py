import os

import pytest

from services.chat_service import ChatService
from services.model_service import ModelService

MODEL_ID = "gemma-3n-4b"
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../../../models/gemma-3n")

pytestmark = pytest.mark.skipif(
    not os.path.isdir(MODEL_DIR), reason="Gemma model assets not present"
)


@pytest.mark.asyncio
async def test_chat_basic_response():
    model_service = ModelService()
    await model_service.initialize()
    loaded = await model_service.load_model(MODEL_ID, MODEL_DIR, model_type="chat")
    assert loaded, "Failed to load chat model"
    chat_service = ChatService()
    await chat_service.initialize(model_service)

    messages = [
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Say hello in one short sentence."},
    ]

    result = await chat_service.process_chat(messages, model=MODEL_ID, max_tokens=32)
    assert result.total_tokens >= result.output_tokens >= 0
    assert result.input_tokens > 0
    assert result.content.strip(), "Empty chat response"
    assert result.finish_reason in {"stop", "length"}
