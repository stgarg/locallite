"""
Document converters for multimodal AI gateway
Handles conversion of various document formats to structured text
"""

# Handle both relative and absolute imports
try:
    from .pdf_converter import PDFConverter
    from .docx_converter import DOCXConverter
    from .image_converter import ImageConverter
except ImportError:
    from pdf_converter import PDFConverter
    from docx_converter import DOCXConverter
    from image_converter import ImageConverter

__all__ = ["PDFConverter", "DOCXConverter", "ImageConverter"]
