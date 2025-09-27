"""
Document converters for multimodal AI gateway
Handles conversion of various document formats to structured text
"""

# Handle both relative and absolute imports
try:
    from .docx_converter import DOCXConverter
    from .image_converter import ImageConverter
    from .pdf_converter import PDFConverter
except ImportError:
    from docx_converter import DOCXConverter
    from image_converter import ImageConverter
    from pdf_converter import PDFConverter

__all__ = ["PDFConverter", "DOCXConverter", "ImageConverter"]
