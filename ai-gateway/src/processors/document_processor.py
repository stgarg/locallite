"""
Document Processor
Unified processor for handling multiple document formats using Polars for analysis
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import polars as pl

# Import converters - handle both relative and absolute imports
try:
    from ..converters import DOCXConverter, ImageConverter, PDFConverter
except ImportError:
    # If relative import fails, try absolute import
    try:
        from converters import DOCXConverter, ImageConverter, PDFConverter
    except ImportError:
        from converters.docx_converter import DOCXConverter
        from converters.image_converter import ImageConverter
        from converters.pdf_converter import PDFConverter

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Unified document processor supporting multiple formats with advanced analysis"""

    def __init__(self):
        self.pdf_converter = PDFConverter()
        self.docx_converter = DOCXConverter()
        self.image_converter = ImageConverter()

        self.converters = {
            "pdf": self.pdf_converter,
            "docx": self.docx_converter,
            "image": self.image_converter,
        }

    def get_supported_formats(self) -> List[str]:
        """Get list of all supported file formats"""
        formats = []
        for converter in self.converters.values():
            formats.extend(converter.supported_formats)
        return sorted(list(set(formats)))

    def detect_format(self, file_path: Path) -> Optional[str]:
        """Detect document format and return converter type"""
        suffix = file_path.suffix.lower()

        if suffix in self.pdf_converter.supported_formats:
            return "pdf"
        elif suffix in self.docx_converter.supported_formats:
            return "docx"
        elif suffix in self.image_converter.supported_formats:
            return "image"

        return None

    def process_document(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Process a document and extract structured content

        Args:
            file_path: Path to document file
            **kwargs: Additional arguments passed to specific converters

        Returns:
            Dictionary containing processed document data
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return {"error": f"File not found: {file_path}", "status": "file_not_found"}

        # Detect format
        format_type = self.detect_format(file_path)
        if not format_type:
            return {
                "error": f"Unsupported file format: {file_path.suffix}",
                "supported_formats": self.get_supported_formats(),
                "status": "unsupported_format",
            }

        # Get appropriate converter
        converter = self.converters[format_type]

        try:
            # Process document
            result = converter.extract_text(file_path, **kwargs)

            # Add processing metadata
            result["processing_metadata"] = {
                "file_path": str(file_path),
                "detected_format": format_type,
                "converter_used": converter.__class__.__name__,
                "processing_status": result.get("status", "unknown"),
            }

            return result

        except Exception as e:
            logger.error(f"Failed to process document {file_path}: {e}")
            return {
                "error": str(e),
                "status": "processing_error",
                "processing_metadata": {
                    "file_path": str(file_path),
                    "detected_format": format_type,
                    "converter_used": converter.__class__.__name__,
                },
            }

    def analyze_document_structure(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Perform advanced structural analysis of a document

        Args:
            file_path: Path to document file

        Returns:
            Dictionary containing structural analysis results
        """
        file_path = Path(file_path)
        format_type = self.detect_format(file_path)

        if not format_type:
            return {
                "error": f"Unsupported file format: {file_path.suffix}",
                "status": "unsupported_format",
            }

        converter = self.converters[format_type]

        # Use converter's analyze method if available
        if hasattr(converter, "analyze_structure"):
            return converter.analyze_structure(file_path)
        elif hasattr(converter, "analyze_ocr_quality"):  # For images
            return converter.analyze_ocr_quality(file_path)
        else:
            # Fall back to basic processing
            return self.process_document(file_path)

    def batch_process(
        self, file_paths: List[Union[str, Path]], **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Process multiple documents in batch

        Args:
            file_paths: List of file paths to process
            **kwargs: Additional arguments passed to converters

        Returns:
            Dictionary mapping file paths to processing results
        """
        results = {}

        for file_path in file_paths:
            try:
                result = self.process_document(file_path, **kwargs)
                results[str(file_path)] = result
            except Exception as e:
                logger.error(f"Failed to process {file_path} in batch: {e}")
                results[str(file_path)] = {
                    "error": str(e),
                    "status": "batch_processing_error",
                }

        return results

    def get_processing_summary(
        self, results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics from batch processing results using Polars

        Args:
            results: Results from batch_process()

        Returns:
            Summary statistics
        """
        try:
            # Prepare data for Polars analysis
            summary_data = []

            for file_path, result in results.items():
                file_name = Path(file_path).name
                status = result.get("status", "unknown")

                row = {
                    "file_name": file_name,
                    "file_path": file_path,
                    "status": status,
                    "success": status == "success",
                    "format_type": result.get("processing_metadata", {}).get(
                        "detected_format", "unknown"
                    ),
                    "converter": result.get("processing_metadata", {}).get(
                        "converter_used", "unknown"
                    ),
                }

                # Add statistics if available
                stats = result.get("statistics", {})
                if stats:
                    row.update(
                        {
                            "total_characters": stats.get("total_characters", 0),
                            "total_pages": stats.get(
                                "total_pages",
                                stats.get(
                                    "total_elements", stats.get("total_words", 0)
                                ),
                            ),
                            "extraction_method": stats.get(
                                "extraction_method", "unknown"
                            ),
                        }
                    )

                summary_data.append(row)

            # Create Polars DataFrame for analysis
            df = pl.DataFrame(summary_data)

            # Generate summary statistics
            summary = {
                "total_files": len(results),
                "successful_files": df.filter(pl.col("success")).height,
                "failed_files": df.filter(~pl.col("success")).height,
                "success_rate": (
                    (df.filter(pl.col("success")).height / len(results) * 100)
                    if results
                    else 0
                ),
                "format_distribution": (
                    df.group_by("format_type").len().to_dict(as_series=False)
                    if df.height > 0
                    else {}
                ),
                "converter_usage": (
                    df.group_by("converter").len().to_dict(as_series=False)
                    if df.height > 0
                    else {}
                ),
            }

            # Add character statistics if available
            if "total_characters" in df.columns:
                char_stats = df.filter(pl.col("success")).select(
                    pl.col("total_characters")
                )
                if char_stats.height > 0:
                    summary["character_statistics"] = {
                        "total_characters": char_stats.sum().item(),
                        "average_characters": char_stats.mean().item(),
                        "max_characters": char_stats.max().item(),
                        "min_characters": char_stats.min().item(),
                    }

            return {
                "summary": summary,
                "detailed_results": summary_data,
                "dataframe": df,
            }

        except Exception as e:
            logger.error(f"Failed to generate processing summary: {e}")
            return {
                "summary": {"total_files": len(results), "error": str(e)},
                "detailed_results": [],
                "dataframe": pl.DataFrame(),
            }
