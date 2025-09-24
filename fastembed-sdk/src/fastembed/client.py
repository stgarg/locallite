"""
FastEmbed SDK Client
OpenAI-compatible client with automatic NPU optimization
"""

import asyncio
import time
from typing import List, Optional, Union, Dict, Any
import httpx
from pydantic import ValidationError

from .models import (
    EmbeddingResponse, EmbeddingRequest, SystemInfo, EmbeddingData, Usage,
    ChatResponse, ChatRequest, ChatMessage, ChatChoice
)
from .exceptions import (
    FastEmbedError,
    FastEmbedConnectionError, 
    FastEmbedTimeoutError,
    FastEmbedAPIError,
    FastEmbedValidationError,
)


class FastEmbedClient:
    """
    FastEmbed SDK Client - OpenAI-compatible embedding client with NPU acceleration
    
    Drop-in replacement for OpenAI embeddings with 2-10x faster inference
    and 90% cost savings on local Snapdragon hardware.
    
    Example:
        ```python
        import fastembed
        
        client = fastembed.FastEmbedClient()
        
        # Single text embedding
        response = client.embeddings.create(
            input="Hello world",
            model="bge-small-en-v1.5"
        )
        
        # Batch embedding with automatic NPU optimization
        response = client.embeddings.create(
            input=["Hello world", "How are you?", "FastEmbed is fast!"],
            model="bge-small-en-v1.5"
        )
        ```
    """
    
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 30.0,
        max_retries: int = 3,
        api_key: Optional[str] = None,  # For OpenAI compatibility
    ):
        """
        Initialize FastEmbed client
        
        Args:
            base_url: Base URL of FastEmbed server
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            api_key: API key (unused but kept for OpenAI compatibility)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(timeout=timeout)
        
        # OpenAI-style API structure
        self.embeddings = EmbeddingsAPI(self)
        self.chat = ChatAPI(self)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def close(self):
        """Close the HTTP client"""
        self._client.close()
        
    async def aclose(self):
        """Close the async HTTP client"""
        if hasattr(self, '_async_client'):
            await self._async_client.aclose()
    
    def health(self) -> SystemInfo:
        """
        Get system health and performance information
        
        Returns:
            SystemInfo: Current system status including NPU availability
        """
        try:
            response = self._client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return SystemInfo(**response.json())
        except httpx.ConnectError as e:
            raise FastEmbedConnectionError(f"Failed to connect to FastEmbed server: {e}")
        except httpx.TimeoutException as e:
            raise FastEmbedTimeoutError(f"Request timed out: {e}")
        except httpx.HTTPStatusError as e:
            raise FastEmbedAPIError(f"API error: {e.response.text}", e.response.status_code)
        except ValidationError as e:
            raise FastEmbedValidationError(f"Invalid response format: {e}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.ConnectError as e:
                if attempt == self.max_retries:
                    raise FastEmbedConnectionError(f"Failed to connect after {self.max_retries + 1} attempts: {e}")
                time.sleep(0.5 * (2 ** attempt))  # Exponential backoff
            except httpx.TimeoutException as e:
                if attempt == self.max_retries:
                    raise FastEmbedTimeoutError(f"Request timed out after {self.max_retries + 1} attempts: {e}")
                time.sleep(0.5 * (2 ** attempt))
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                raise FastEmbedAPIError(f"API error: {error_detail}", e.response.status_code)


class EmbeddingsAPI:
    """OpenAI-compatible embeddings API"""
    
    def __init__(self, client: FastEmbedClient):
        self._client = client
        
    def create(
        self,
        input: Union[str, List[str]],
        model: str = "bge-small-en-v1.5",
        encoding_format: str = "float",
        dimensions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> EmbeddingResponse:
        """
        Create embeddings for input text(s)
        
        Args:
            input: Text string or list of strings to embed
            model: Model to use for embeddings
            encoding_format: Format for embeddings (only 'float' supported)
            dimensions: Number of dimensions (optional)
            user: User identifier (optional)
            
        Returns:
            EmbeddingResponse: Response containing embeddings and usage info
            
        Example:
            ```python
            # Single text
            response = client.embeddings.create(input="Hello world")
            embedding = response.data[0].embedding
            
            # Multiple texts with automatic NPU optimization
            response = client.embeddings.create(
                input=["Hello", "World", "FastEmbed"]
            )
            embeddings = [item.embedding for item in response.data]
            ```
        """
        start_time = time.time()
        
        # Validate input
        if isinstance(input, str):
            texts = [input]
        elif isinstance(input, list):
            if not input:
                raise FastEmbedValidationError("Input list cannot be empty")
            if not all(isinstance(text, str) for text in input):
                raise FastEmbedValidationError("All inputs must be strings")
            texts = input
        else:
            raise FastEmbedValidationError("Input must be string or list of strings")
        
        # Create request
        request_data = EmbeddingRequest(
            input=texts,
            model=model,
            encoding_format=encoding_format,
            dimensions=dimensions,
            user=user,
        ).model_dump(exclude_none=True)
        
        # Make API request
        try:
            response = self._client._make_request(
                "POST",
                "/v1/embeddings",
                json=request_data,
            )
            
            response_data = response.json()
            
            # Convert to our models
            embedding_data = []
            for i, embedding in enumerate(response_data["data"]):
                embedding_data.append(EmbeddingData(
                    index=i,
                    embedding=embedding["embedding"]
                ))
            
            # Calculate usage (approximate for compatibility)
            total_tokens = sum(len(text.split()) for text in texts)
            usage = Usage(
                prompt_tokens=total_tokens,
                total_tokens=total_tokens
            )
            
            return EmbeddingResponse(
                data=embedding_data,
                model=model,
                usage=usage
            )
            
        except ValidationError as e:
            raise FastEmbedValidationError(f"Invalid response format: {e}")


class ChatAPI:
    """OpenAI-compatible chat completions API"""
    
    def __init__(self, client: 'FastEmbedClient'):
        self._client = client
        
    def create(
        self,
        model: str = "gemma-3n-4b",
        messages: List[Dict[str, str]] = None,
        temperature: Optional[float] = 1.0,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = 1.0,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
        stop: Optional[Union[str, List[str]]] = None,
        stream: Optional[bool] = False,
        user: Optional[str] = None,
    ) -> ChatResponse:
        """
        Create chat completion
        
        Args:
            model: Model to use for chat completion
            messages: List of messages (dicts with 'role' and 'content' keys)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            stop: Stop sequences
            stream: Whether to stream responses
            user: User identifier
            
        Returns:
            ChatResponse: Response containing chat completion
            
        Example:
            ```python
            response = client.chat.create(
                model="gemma-3n-4b",
                messages=[
                    {"role": "user", "content": "Hello!"}
                ]
            )
            message = response.choices[0].message.content
            ```
        """
        if messages is None:
            messages = []
            
        start_time = time.time()
        
        # Validate messages
        if not messages:
            raise FastEmbedValidationError("Messages list cannot be empty")
        
        # Convert dict messages to ChatMessage objects if needed
        chat_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                chat_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                    "name": msg.get("name")
                })
            else:
                chat_messages.append(msg)
        
        # Build request
        request_data = {
            "model": model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stop": stop,
            "stream": stream,
            "user": user
        }
        
        try:
            # Make request to chat completions endpoint
            response = self._client._make_request(
                "POST",
                "/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            response_data = response.json()
            
            # Build response model
            choices = []
            for choice_data in response_data.get("choices", []):
                message_data = choice_data.get("message", {})
                choice = ChatChoice(
                    index=choice_data.get("index", 0),
                    message=ChatMessage(
                        role=message_data.get("role", "assistant"),
                        content=message_data.get("content", ""),
                        name=message_data.get("name")
                    ),
                    finish_reason=choice_data.get("finish_reason")
                )
                choices.append(choice)
            
            usage_data = response_data.get("usage", {})
            usage = Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )
            
            return ChatResponse(
                id=response_data.get("id", ""),
                object=response_data.get("object", "chat.completion"),
                created=response_data.get("created", int(time.time())),
                model=response_data.get("model", model),
                choices=choices,
                usage=usage
            )
            
        except ValidationError as e:
            raise FastEmbedValidationError(f"Invalid response format: {e}")


class AsyncFastEmbedClient:
    """
    Async version of FastEmbed client for high-throughput applications
    """
    
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 30.0,
        max_retries: int = 3,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(timeout=timeout)
        self.embeddings = AsyncEmbeddingsAPI(self)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
        
    async def aclose(self):
        """Close the async HTTP client"""
        await self._client.aclose()
    
    async def health(self) -> SystemInfo:
        """Async version of health check"""
        try:
            response = await self._client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return SystemInfo(**response.json())
        except httpx.ConnectError as e:
            raise FastEmbedConnectionError(f"Failed to connect to FastEmbed server: {e}")
        except httpx.TimeoutException as e:
            raise FastEmbedTimeoutError(f"Request timed out: {e}")
        except httpx.HTTPStatusError as e:
            raise FastEmbedAPIError(f"API error: {e.response.text}", e.response.status_code)
        except ValidationError as e:
            raise FastEmbedValidationError(f"Invalid response format: {e}")
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make async HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.ConnectError as e:
                if attempt == self.max_retries:
                    raise FastEmbedConnectionError(f"Failed to connect after {self.max_retries + 1} attempts: {e}")
                await asyncio.sleep(0.5 * (2 ** attempt))
            except httpx.TimeoutException as e:
                if attempt == self.max_retries:
                    raise FastEmbedTimeoutError(f"Request timed out after {self.max_retries + 1} attempts: {e}")
                await asyncio.sleep(0.5 * (2 ** attempt))
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                raise FastEmbedAPIError(f"API error: {error_detail}", e.response.status_code)


class AsyncEmbeddingsAPI:
    """Async OpenAI-compatible embeddings API"""
    
    def __init__(self, client: AsyncFastEmbedClient):
        self._client = client
        
    async def create(
        self,
        input: Union[str, List[str]],
        model: str = "bge-small-en-v1.5",
        encoding_format: str = "float",
        dimensions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> EmbeddingResponse:
        """Async version of embeddings creation"""
        start_time = time.time()
        
        # Validate input (same as sync version)
        if isinstance(input, str):
            texts = [input]
        elif isinstance(input, list):
            if not input:
                raise FastEmbedValidationError("Input list cannot be empty")
            if not all(isinstance(text, str) for text in input):
                raise FastEmbedValidationError("All inputs must be strings")
            texts = input
        else:
            raise FastEmbedValidationError("Input must be string or list of strings")
        
        # Create request
        request_data = EmbeddingRequest(
            input=texts,
            model=model,
            encoding_format=encoding_format,
            dimensions=dimensions,
            user=user,
        ).model_dump(exclude_none=True)
        
        # Make API request
        try:
            response = await self._client._make_request(
                "POST",
                "/v1/embeddings",
                json=request_data,
            )
            
            response_data = response.json()
            
            # Convert to our models
            embedding_data = []
            for i, embedding in enumerate(response_data["data"]):
                embedding_data.append(EmbeddingData(
                    index=i,
                    embedding=embedding["embedding"]
                ))
            
            # Calculate usage
            total_tokens = sum(len(text.split()) for text in texts)
            usage = Usage(
                prompt_tokens=total_tokens,
                total_tokens=total_tokens
            )
            
            return EmbeddingResponse(
                data=embedding_data,
                model=model,
                usage=usage
            )
            
        except ValidationError as e:
            raise FastEmbedValidationError(f"Invalid response format: {e}")