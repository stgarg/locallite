"""
Document processors for multimodal AI gateway
Handles processing pipelines for extracted document content
"""

# Handle both relative and absolute imports
try:
    from .document_processor import DocumentProcessor
except ImportError:
    from document_processor import DocumentProcessor

__all__ = ["DocumentProcessor"]
