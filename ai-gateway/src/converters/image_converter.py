"""
Image Document Converter
Converts images to text using OCR (pytesseract) with Polars analysis
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from PIL import Image
import pytesseract
import polars as pl

logger = logging.getLogger(__name__)

class ImageConverter:
    """Converts images to text using OCR with advanced analysis"""
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp']
        self.ocr_enabled = self._check_tesseract()
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is available"""
        try:
            # Set Tesseract path for Windows
            import os
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
            pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Tesseract OCR not available: {e}")
            return False
    
    def is_supported(self, file_path: Path) -> bool:
        """Check if file format is supported"""
        return file_path.suffix.lower() in self.supported_formats
    
    def extract_text(self, file_path, include_metadata: bool = True, ocr_config: str = '') -> Dict[str, Any]:
        """
        Extract text from image using OCR
        
        Args:
            file_path: Path to image file (str or Path object)
            include_metadata: Whether to include image metadata
            ocr_config: Custom OCR configuration string for tesseract
            
        Returns:
            Dictionary containing extracted text, metadata, and analysis
        """
        if not self.ocr_enabled:
            return {
                'error': 'Tesseract OCR not available',
                'status': 'ocr_unavailable'
            }
        
        try:
            # Ensure file_path is a Path object
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            # Open and analyze image
            image = Image.open(file_path)
            
            # Extract metadata if requested
            metadata = {}
            if include_metadata:
                metadata = self._extract_metadata(image, file_path)
            
            # Perform OCR
            ocr_data = self._perform_ocr(image, ocr_config)
            
            # Create structured output using Polars if we have detailed OCR data
            ocr_df = None
            if ocr_data.get('detailed_data'):
                try:
                    ocr_df = pl.DataFrame(ocr_data['detailed_data'])
                except Exception as e:
                    logger.warning(f"Failed to create Polars DataFrame for OCR data: {e}")
            
            # Calculate statistics
            statistics = {
                'total_characters': len(ocr_data['text']),
                'confidence_score': ocr_data.get('confidence', 0),
                'word_count': len(ocr_data['text'].split()) if ocr_data['text'] else 0,
                'line_count': len(ocr_data['text'].split('\\n')) if ocr_data['text'] else 0,
                'extraction_method': 'tesseract_ocr',
                'ocr_config': ocr_config or 'default'
            }
            
            # Detect and format tables using coordinate data
            table_analysis = self.detect_and_format_tables(ocr_data.get('detailed_data', []))
            
            return {
                'metadata': metadata,
                'ocr_text': ocr_data['text'],
                'ocr_confidence': ocr_data.get('confidence', 0),
                'ocr_detailed': ocr_data.get('detailed_data', []),
                'ocr_dataframe': ocr_df,
                'statistics': statistics,
                'table_analysis': table_analysis,
                'structured_text': table_analysis.get('structured_text', ocr_data['text']),
                'full_text': ocr_data['text'],
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Failed to process image {file_path}: {e}")
            
            # Handle both string and Path objects in error case
            filename = file_path.name if hasattr(file_path, 'name') else str(file_path).split('\\')[-1]
            
            return {
                'metadata': {'filename': filename},
                'ocr_text': '',
                'ocr_detailed': [],
                'ocr_dataframe': pl.DataFrame(),
                'statistics': {'total_characters': 0, 'extraction_method': 'failed'},
                'full_text': '',
                'error': str(e),
                'status': 'error'
            }
    
    def _extract_metadata(self, image: Image.Image, file_path: Path) -> Dict[str, Any]:
        """Extract image metadata"""
        metadata = {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'image_format': image.format,
            'image_mode': image.mode,
            'image_size': image.size,
            'width': image.width,
            'height': image.height,
        }
        
        # Try to extract EXIF data
        try:
            exif = image._getexif()
            if exif:
                metadata['exif_data'] = dict(exif)
        except Exception:
            metadata['exif_data'] = {}
        
        return metadata
    
    def _perform_ocr(self, image: Image.Image, config: str) -> Dict[str, Any]:
        """Perform OCR on image and return detailed results"""
        try:
            # Extract plain text
            text = pytesseract.image_to_string(image, config=config).strip()
            
            # Try to get detailed OCR data with bounding boxes and confidence
            detailed_data = []
            try:
                ocr_data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                
                # Process detailed OCR results
                for i in range(len(ocr_data['text'])):
                    if int(ocr_data['conf'][i]) > 0:  # Only include confident detections
                        detailed_data.append({
                            'text': ocr_data['text'][i],
                            'confidence': int(ocr_data['conf'][i]),
                            'left': ocr_data['left'][i],
                            'top': ocr_data['top'][i], 
                            'width': ocr_data['width'][i],
                            'height': ocr_data['height'][i],
                            'level': ocr_data['level'][i],
                            'page_num': ocr_data['page_num'][i],
                            'block_num': ocr_data['block_num'][i],
                            'par_num': ocr_data['par_num'][i],
                            'line_num': ocr_data['line_num'][i],
                            'word_num': ocr_data['word_num'][i]
                        })
                
                # Calculate average confidence
                confidences = [d['confidence'] for d in detailed_data if d['confidence'] > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
            except Exception as e:
                logger.warning(f"Failed to get detailed OCR data: {e}")
                avg_confidence = 0
            
            return {
                'text': text,
                'confidence': avg_confidence,
                'detailed_data': detailed_data
            }
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return {
                'text': '',
                'confidence': 0,
                'detailed_data': []
            }
    
    def detect_and_format_tables(self, detailed_data: List[Dict], confidence_threshold: int = 50) -> Dict[str, Any]:
        """
        Detect table structures using coordinate data and format them properly
        
        Args:
            detailed_data: List of OCR elements with coordinates
            confidence_threshold: Minimum confidence to include words
            
        Returns:
            Dictionary with detected tables and formatted structures
        """
        if not detailed_data:
            return {'tables': [], 'structured_text': '', 'table_count': 0}
        
        try:
            # Create DataFrame for spatial analysis
            df = pl.DataFrame(detailed_data)
            
            # Filter high-confidence words
            confident_df = df.filter(pl.col('confidence') > confidence_threshold)
            
            if len(confident_df) == 0:
                return {'tables': [], 'structured_text': '', 'table_count': 0}
            
            # Group by approximate rows (Y-coordinate clustering)
            row_tolerance = 15  # pixels
            confident_df = confident_df.with_columns([
                (pl.col('top') / row_tolerance).round().cast(pl.Int64).alias('row_group')
            ])
            
            # Create structured rows
            rows_data = confident_df.group_by('row_group').agg([
                pl.col('text').sort_by('left'),
                pl.col('left').sort(),
                pl.col('confidence').sort_by('left'),
                pl.col('top').min().alias('row_y')
            ]).sort('row_y')
            
            structured_rows = []
            tables = []
            current_table = None
            
            for row_data in rows_data.iter_rows(named=True):
                texts = row_data['text']
                positions = row_data['left']
                confidences = row_data['confidence']
                row_y = row_data['row_y']
                
                # Create formatted row with proper spacing
                row_cells = []
                formatted_row = ""
                last_pos = 0
                
                for i, (text, pos, conf) in enumerate(zip(texts, positions, confidences)):
                    # Calculate spacing based on position
                    if i > 0:
                        gap = pos - last_pos
                        if gap > 100:  # Large gap suggests new column
                            formatted_row += " | "
                            row_cells.append(text)
                        elif gap > 30:  # Medium gap
                            formatted_row += "  "
                        else:  # Small gap
                            formatted_row += " "
                    
                    formatted_row += text
                    if i == 0:  # First cell
                        row_cells.append(text)
                    
                    last_pos = pos + len(text) * 8
                
                # Detect table patterns
                is_table_row = self._is_table_row(texts, positions)
                
                if is_table_row:
                    if current_table is None:
                        current_table = {
                            'start_y': row_y,
                            'rows': [],
                            'columns': self._detect_columns(positions),
                            'type': 'data_table'
                        }
                    
                    current_table['rows'].append({
                        'cells': row_cells,
                        'formatted': formatted_row.strip(),
                        'y_position': row_y,
                        'confidence': sum(confidences) / len(confidences) if confidences else 0
                    })
                else:
                    # End current table if we have one
                    if current_table and len(current_table['rows']) >= 2:
                        current_table['end_y'] = current_table['rows'][-1]['y_position']
                        tables.append(current_table)
                    current_table = None
                
                structured_rows.append({
                    'text': formatted_row.strip(),
                    'y_position': row_y,
                    'is_table': is_table_row,
                    'cell_count': len(row_cells)
                })
            
            # Add final table if exists
            if current_table and len(current_table['rows']) >= 2:
                current_table['end_y'] = current_table['rows'][-1]['y_position']
                tables.append(current_table)
            
            # Generate structured text output
            structured_text = self._format_structured_output(structured_rows, tables)
            
            return {
                'tables': tables,
                'structured_text': structured_text,
                'structured_rows': structured_rows,
                'table_count': len(tables),
                'processing_stats': {
                    'total_words': len(detailed_data),
                    'confident_words': len(confident_df),
                    'rows_detected': len(structured_rows),
                    'confidence_threshold': confidence_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"Table detection failed: {e}")
            return {'tables': [], 'structured_text': '', 'table_count': 0, 'error': str(e)}
    
    def _is_table_row(self, texts: List[str], positions: List[int]) -> bool:
        """Detect if a row likely belongs to a table structure"""
        if len(texts) < 2:
            return False
        
        # Check for table indicators
        table_keywords = ['units', 'inventory', 'backlog', 'level', 'amount', 'total', 'sum']
        numeric_pattern = any(any(c.isdigit() for c in text) for text in texts)
        
        # Check for consistent spacing (columnar layout)
        if len(positions) >= 3:
            gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            consistent_spacing = len(set(gap//20 for gap in gaps)) <= 3  # Allow some variation
        else:
            consistent_spacing = False
        
        # Table row if: has numbers OR table keywords OR consistent spacing
        return numeric_pattern or any(kw in ' '.join(texts).lower() for kw in table_keywords) or consistent_spacing
    
    def _detect_columns(self, positions: List[int]) -> List[Dict]:
        """Detect column boundaries from X positions"""
        if not positions:
            return []
        
        # Group similar positions into columns
        column_tolerance = 30  # pixels
        columns = []
        
        for pos in sorted(set(positions)):
            # Find if this position belongs to existing column
            found_column = False
            for col in columns:
                if abs(pos - col['center']) <= column_tolerance:
                    col['positions'].append(pos)
                    col['center'] = sum(col['positions']) // len(col['positions'])
                    found_column = True
                    break
            
            if not found_column:
                columns.append({
                    'center': pos,
                    'positions': [pos],
                    'width': 0
                })
        
        # Calculate column widths
        for i, col in enumerate(columns):
            if i < len(columns) - 1:
                col['width'] = columns[i+1]['center'] - col['center']
            else:
                col['width'] = 100  # Default for last column
        
        return columns
    
    def _format_structured_output(self, structured_rows: List[Dict], tables: List[Dict]) -> str:
        """Format the structured output with tables properly aligned"""
        output_lines = []
        
        for row in structured_rows:
            if row['is_table'] and row['cell_count'] > 1:
                # Format as table row with proper alignment
                output_lines.append(f"║ {row['text']} ║")
            else:
                # Regular text
                output_lines.append(row['text'])
        
        # Add table summaries
        if tables:
            output_lines.append("")
            output_lines.append("📊 DETECTED TABLES:")
            output_lines.append("=" * 50)
            
            for i, table in enumerate(tables):
                output_lines.append(f"Table {i+1}: {len(table['rows'])} rows, {len(table['columns'])} columns")
                
                # Show formatted table
                for row in table['rows']:
                    output_lines.append(f"  {row['formatted']}")
                
                output_lines.append("")
        
        return '\n'.join(output_lines)

    def analyze_ocr_quality(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze OCR quality and provide insights
        """
        result = self.extract_text(file_path)
        if result['status'] != 'success' or result['ocr_dataframe'] is None:
            return result
        
        df = result['ocr_dataframe']
        
        if df.height == 0:
            return {
                **result,
                'quality_analysis': {'status': 'no_text_detected'},
                'recommendations': ['Image may not contain readable text', 'Try image preprocessing or different OCR settings']
            }
        
        # Analyze OCR quality
        analysis = {
            'confidence_statistics': {
                'average_confidence': df.select(pl.col('confidence').mean()).item(),
                'min_confidence': df.select(pl.col('confidence').min()).item(),
                'max_confidence': df.select(pl.col('confidence').max()).item(),
                'low_confidence_words': df.filter(pl.col('confidence') < 50).height,
                'high_confidence_words': df.filter(pl.col('confidence') >= 80).height,
            },
            'text_distribution': {
                'total_words': df.height,
                'unique_words': df.select(pl.col('text').n_unique()).item(),
                'empty_detections': df.filter(pl.col('text') == '').height,
            }
        }
        
        # Generate recommendations
        recommendations = []
        if analysis['confidence_statistics']['average_confidence'] < 60:
            recommendations.append("Low average confidence - consider image preprocessing")
        if analysis['confidence_statistics']['low_confidence_words'] > analysis['text_distribution']['total_words'] * 0.3:
            recommendations.append("Many low-confidence words detected - image quality may be poor")
        if analysis['text_distribution']['empty_detections'] > 10:
            recommendations.append("Many empty detections - OCR may be detecting noise")
        
        if not recommendations:
            recommendations.append("OCR quality appears good")
        
        return {
            **result,
            'quality_analysis': analysis,
            'recommendations': recommendations
        }
    
    def export_tables(self, table_analysis: Dict, format_type: str = 'markdown') -> str:
        """
        Export detected tables in various formats
        
        Args:
            table_analysis: Result from detect_and_format_tables
            format_type: 'markdown', 'csv', 'json', 'html'
            
        Returns:
            Formatted table string
        """
        tables = table_analysis.get('tables', [])
        if not tables:
            return f"No tables detected for {format_type} export"
        
        output = []
        
        for i, table in enumerate(tables):
            rows = table['rows']
            
            if format_type.lower() == 'markdown':
                output.append(f"## Table {i+1}")
                output.append("")
                
                # Create markdown table
                if rows:
                    # Header (use first row or create generic headers)
                    max_cells = max(len(row.get('cells', [])) for row in rows) or 2
                    headers = [f"Col {j+1}" for j in range(max_cells)]
                    
                    # Table header
                    output.append("| " + " | ".join(headers) + " |")
                    output.append("|" + "|".join([" --- "] * max_cells) + "|")
                    
                    # Table data
                    for row in rows:
                        cells = row.get('cells', [])
                        # Pad with empty cells if needed
                        while len(cells) < max_cells:
                            cells.append("")
                        output.append("| " + " | ".join(cells) + " |")
                
                output.append("")
                
            elif format_type.lower() == 'csv':
                output.append(f"# Table {i+1}")
                for row in rows:
                    cells = row.get('cells', [])
                    # Clean cells for CSV
                    clean_cells = [cell.replace(',', ';').replace('"', '') for cell in cells]
                    output.append(','.join(f'"{cell}"' for cell in clean_cells))
                output.append("")
                
            elif format_type.lower() == 'html':
                output.append(f"<h3>Table {i+1}</h3>")
                output.append("<table border='1'>")
                
                for row in rows:
                    output.append("  <tr>")
                    cells = row.get('cells', [])
                    for cell in cells:
                        clean_cell = cell.replace('<', '&lt;').replace('>', '&gt;')
                        output.append(f"    <td>{clean_cell}</td>")
                    output.append("  </tr>")
                
                output.append("</table>")
                output.append("")
                
            elif format_type.lower() == 'json':
                import json
                table_data = {
                    'table_id': i+1,
                    'rows': len(rows),
                    'columns': len(table['columns']),
                    'position': {
                        'start_y': table.get('start_y'),
                        'end_y': table.get('end_y')
                    },
                    'data': [
                        {
                            'row_number': j+1,
                            'cells': row.get('cells', []),
                            'confidence': row.get('confidence', 0),
                            'y_position': row.get('y_position', 0)
                        }
                        for j, row in enumerate(rows)
                    ]
                }
                output.append(json.dumps(table_data, indent=2))
                output.append("")
        
        return '\n'.join(output)