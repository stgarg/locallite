"""Model registry skeleton.

Provides metadata for available models and a simple accessor.
Later: load policies, lazy initialization, health status, dynamic refresh.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, List


@dataclass
class ModelSpec:
    model_id: str
    task: str                 # 'embedding' | 'chat' | 'rerank' | 'vision'
    backend: str              # 'onnx-custom' | 'fastembed' | 'hf-transformers' | 'gguf'
    dimension: Optional[int] = None
    path: Optional[str] = None
    license: Optional[str] = None
    revision: Optional[str] = None
    capabilities: Dict[str, object] = field(default_factory=dict)
    notes: Optional[str] = None


# Minimal seed registry (to be expanded)
MODEL_REGISTRY: Dict[str, ModelSpec] = {
    "bge-small-en-v1.5": ModelSpec(
        model_id="bge-small-en-v1.5",
        task="embedding",
        backend="onnx-custom",
        dimension=384,
        path="models/bge-small-en-v1.5",
        license="Apache-2.0",
        capabilities={"batch_optimal": 4, "small_batch_provider": "CPU-ARM64"},
        notes="Initial ONNX export; heuristic provider routing",
    ),
    "phi-3-mini-4k": ModelSpec(
        model_id="phi-3-mini-4k",
        task="chat",
        backend="onnx-custom",
        path="models/phi-3-mini-4k",
        license="MIT? (verify)",
        capabilities={"context_length": 4000, "streaming": False},
        notes="Chat ONNX path; tokenizer alignment pending",
    ),
}


def list_models(task: Optional[str] = None) -> List[ModelSpec]:
    if task:
        return [m for m in MODEL_REGISTRY.values() if m.task == task]
    return list(MODEL_REGISTRY.values())


def get_model(model_id: str) -> Optional[ModelSpec]:
    return MODEL_REGISTRY.get(model_id)


__all__ = ["ModelSpec", "MODEL_REGISTRY", "list_models", "get_model"]
