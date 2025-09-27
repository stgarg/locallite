"""
PDF Document Converter
Converts PDF files to structured text using pypdf
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from pypdf import PdfReader
from PIL import Image
import pytesseract
import polars as pl

logger = logging.getLogger(__name__)

class PDFConverter:
    """Converts PDF documents to structured text using multiple methods"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.ocr_enabled = self._check_tesseract()
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is available"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            logger.warning("Tesseract OCR not available - image-based PDFs won't be processed")
            return False
    
    def is_supported(self, file_path: Path) -> bool:
        """Check if file format is supported"""
        return file_path.suffix.lower() in self.supported_formats
    
    def extract_text(self, file_path: Path, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Extract text from PDF file using pypdf with Polars for data analysis
        
        Args:
            file_path: Path to PDF file
            include_metadata: Whether to include document metadata
            
        Returns:
            Dictionary containing extracted text, metadata, and structured data
        """
        try:
            reader = PdfReader(file_path)
            
            # Extract metadata if requested
            metadata = {}
            if include_metadata:
                metadata = self._extract_metadata(reader, file_path)
            
            # Extract text from each page
            pages_data = []
            total_chars = 0
            
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text().strip()
                    char_count = len(text)
                    total_chars += char_count
                    
                    page_data = {
                        'page_number': i + 1,
                        'text': text,
                        'char_count': char_count,
                        'has_text': char_count > 0
                    }
                    
                    # Try to extract additional page info
                    if hasattr(page, 'mediabox'):
                        page_data['dimensions'] = {
                            'width': float(page.mediabox.width),
                            'height': float(page.mediabox.height)
                        }
                    
                    pages_data.append(page_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {i + 1}: {e}")
                    pages_data.append({
                        'page_number': i + 1,
                        'text': '',
                        'char_count': 0,
                        'has_text': False,
                        'error': str(e)
                    })
            
            # Create structured output using Polars for data analysis
            try:
                pages_df = pl.DataFrame(pages_data)
            except Exception as e:
                logger.warning(f"Failed to create Polars DataFrame: {e}")
                pages_df = None
            
            # Calculate statistics
            statistics = {
                'total_pages': len(pages_data),
                'total_characters': total_chars,
                'non_empty_pages': len([p for p in pages_data if p['has_text']]),
                'empty_pages': len([p for p in pages_data if not p['has_text']]),
                'average_chars_per_page': total_chars / len(pages_data) if pages_data else 0,
                'extraction_method': 'pypdf_with_polars'
            }
            
            return {
                'metadata': metadata,
                'pages': pages_data,
                'pages_dataframe': pages_df,
                'statistics': statistics,
                'full_text': self._combine_page_text(pages_data),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Failed to process PDF {file_path}: {e}")
            return {
                'metadata': {'filename': file_path.name},
                'pages': [],
                'pages_dataframe': pl.DataFrame(),
                'statistics': {'total_pages': 0, 'total_characters': 0, 'extraction_method': 'failed'},
                'full_text': '',
                'error': str(e),
                'status': 'error'
            }
    
    def _extract_metadata(self, reader: PdfReader, file_path: Path) -> Dict[str, Any]:
        """Extract PDF metadata"""
        metadata = {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'pages': len(reader.pages),
        }
        
        if reader.metadata:
            metadata.update({
                'title': reader.metadata.get('/Title', '').strip(),
                'author': reader.metadata.get('/Author', '').strip(),
                'subject': reader.metadata.get('/Subject', '').strip(),
                'creator': reader.metadata.get('/Creator', '').strip(),
                'producer': reader.metadata.get('/Producer', '').strip(),
                'creation_date': str(reader.metadata.get('/CreationDate', '')),
                'modification_date': str(reader.metadata.get('/ModDate', '')),
            })
        
        return metadata
    
    def _combine_page_text(self, pages_data: List[Dict]) -> str:
        """Combine text from all pages into a single string"""
        texts = []
        for page in pages_data:
            if page.get('text'):
                texts.append(f"--- Page {page['page_number']} ---\n{page['text']}\n")
        return '\n'.join(texts)
    
    def analyze_structure(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze document structure and return insights using Polars
        """
        result = self.extract_text(file_path)
        if result['status'] != 'success' or result['pages_dataframe'] is None:
            return result
        
        df = result['pages_dataframe']
        
        # Analyze page content patterns
        analysis = {
            'content_distribution': {
                'pages_with_content': df.filter(pl.col('has_text')).height,
                'pages_without_content': df.filter(~pl.col('has_text')).height,
                'content_percentage': (df.filter(pl.col('has_text')).height / df.height * 100) if df.height > 0 else 0
            },
            'text_statistics': {
                'total_characters': df.select(pl.col('char_count').sum()).item(),
                'average_chars_per_page': df.select(pl.col('char_count').mean()).item(),
                'max_chars_per_page': df.select(pl.col('char_count').max()).item(),
                'min_chars_per_page': df.select(pl.col('char_count').min()).item(),
            }
        }
        
        # Detect potential issues
        issues = []
        if analysis['content_distribution']['content_percentage'] < 50:
            issues.append("More than 50% of pages appear to be empty - possibly image-based PDF")
        
        if analysis['text_statistics']['average_chars_per_page'] < 100:
            issues.append("Very low text density - may need OCR processing")
        
        return {
            **result,
            'structure_analysis': analysis,
            'potential_issues': issues
        }
    
    def extract_with_ocr(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from PDF using OCR for image-based PDFs
        Note: Requires additional setup for image extraction from PDF
        """
        if not self.ocr_enabled:
            return {
                'error': 'Tesseract OCR not available',
                'status': 'ocr_unavailable'
            }
        
        logger.warning("OCR extraction from PDF not yet fully implemented")
        return {
            'error': 'OCR extraction not yet fully implemented',
            'status': 'not_implemented'
        }