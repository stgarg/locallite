"""
FastEmbed SDK Data Models
Pydantic models for request/response data
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class Usage(BaseModel):
    """Token usage statistics"""
    prompt_tokens: int
    total_tokens: int


class EmbeddingData(BaseModel):
    """Individual embedding data point"""
    object: str = "embedding"
    index: int
    embedding: List[float]


class EmbeddingResponse(BaseModel):
    """Response from embeddings endpoint"""
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: Usage


class EmbeddingRequest(BaseModel):
    """Request to embeddings endpoint"""
    input: Union[str, List[str]]
    model: str = "bge-small-en-v1.5"
    encoding_format: str = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None


class SystemInfo(BaseModel):
    """System information from health endpoint"""
    status: str
    npu_available: bool
    models_loaded: List[str]
    memory_usage: Dict[str, Any]
    performance_stats: Dict[str, Any]
    uptime_seconds: float


class BenchmarkResult(BaseModel):
    """Benchmark comparison result"""
    provider: str
    latency_ms: float
    cost_per_1k_tokens: float
    tokens_per_second: float
    quality_score: Optional[float] = None
    error_rate: float = 0.0
    
    
class BenchmarkSuite(BaseModel):
    """Complete benchmark suite results"""
    test_name: str
    timestamp: str
    hardware_info: Dict[str, Any]
    results: List[BenchmarkResult]
    summary: Dict[str, Any]


# === Chat API Models ===

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None


class ChatRequest(BaseModel):
    """Request to chat completions endpoint"""
    model: str = "gemma-3n-4b"
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    user: Optional[str] = None


class ChatChoice(BaseModel):
    """Individual chat completion choice"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from chat completions endpoint"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Usage