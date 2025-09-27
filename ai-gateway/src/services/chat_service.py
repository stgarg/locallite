"""
Shared Chat Service
Core chat/completion processing logic shared by both human and agent endpoints
"""

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.router_types import RequestType, UnifiedRequest

from .model_service import ModelService

logger = logging.getLogger(__name__)


@dataclass
class ChatResult:
    """Result from chat processing"""

    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model_used: str
    provider_used: str
    processing_time_ms: float
    finish_reason: str
    request_id: str
    metadata: Dict[str, Any]


class ChatService:
    """
    Core chat service shared by both human and agent endpoints

    Handles:
    - Real ONNX inference (replacing placeholders)
    - Streaming support
    - Token counting
    - Model routing between different chat models
    """

    def __init__(self):
        self.chat_model = None
        self._is_initialized = False
        self.model_router: Optional[ModelService] = None

    async def initialize(self, model_router: ModelService) -> bool:
        """Initialize with model router reference"""
        try:
            self.model_router = model_router
            self._is_initialized = True
            logger.info("✅ ChatService initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChatService: {e}")
            return False

    async def process_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemma-3n-4b",
        stream: bool = False,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
    ) -> ChatResult:
        """
        Core chat logic - shared by both human and agent endpoints

        Args:
            messages: Chat messages in OpenAI format
            model: Model identifier
            stream: Whether to stream the response
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            stop: Stop sequences

        Returns:
            ChatResult with generated content and metadata
        """
        if not self._is_initialized or not self.model_router:
            raise RuntimeError("ChatService not initialized")

        start_time = time.time()
        request_id = f"chatcmpl-{str(uuid.uuid4())[:8]}"

        try:
            target_model_id = model or self.model_router.get_default_model_id("chat")
            if not target_model_id:
                available = self.model_router.list_models_by_type("chat")
                if not available:
                    raise RuntimeError("No chat models loaded")
                target_model_id = available[0]

            chat_model = self.model_router.get_model(target_model_id)
            if not chat_model:
                raise RuntimeError(f"Chat model '{target_model_id}' not loaded")

            unified_request = UnifiedRequest(
                id=request_id,
                request_type=RequestType.CHAT_COMPLETION,
                model_id=target_model_id,
                content={
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                    "stop": stop,
                },
                options={"stream": stream},
                timestamp=time.time(),
            )

            # Process with the chat model
            unified_response = await chat_model.process(unified_request)

            processing_time_ms = (time.time() - start_time) * 1000

            # Extract response content
            choices = unified_response.content.get("choices", [])
            if not choices:
                raise RuntimeError("No response generated from chat model")

            choice = choices[0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "stop")

            # Extract token usage
            usage = unified_response.usage
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

            logger.info(
                "Chat completion: model=%s, tokens=%s, time=%.1fms",
                unified_response.model_id,
                total_tokens,
                processing_time_ms,
            )

            return ChatResult(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                model_used=unified_response.model_id,
                provider_used=unified_response.provider_used,
                processing_time_ms=processing_time_ms,
                finish_reason=finish_reason,
                request_id=request_id,
                metadata={
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                    "stop": stop,
                },
            )

        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Error in chat processing: {e}")

            # Return error result
            return ChatResult(
                content=f"Error: {str(e)}",
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                model_used=model,
                provider_used="error",
                processing_time_ms=processing_time_ms,
                finish_reason="error",
                request_id=request_id,
                metadata={"error": str(e)},
            )

    def health_check(self) -> Dict[str, Any]:
        """Health check for the chat service"""
        if not self._is_initialized or not self.model_router:
            return {"status": "unhealthy", "error": "Service not initialized"}

        try:
            router_status = self.model_router.get_status()
            chat_models = self.model_router.list_models_by_type("chat")
            chat_available = len(chat_models) > 0

            return {
                "status": "healthy" if chat_available else "degraded",
                "chat_model_available": chat_available,
                "router_status": router_status,
                "available_models": chat_models,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
