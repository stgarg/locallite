"""Runtime package for model execution abstractions (embedding, chat, multimodal).

Initial focus: embedding backends + model registry.
"""

from .model_registry import MODEL_REGISTRY, ModelSpec  # noqa: F401
