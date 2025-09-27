"""Test enhanced table detection capabilities"""
import sys
sys.path.insert(0, r'C:\Learn\Code\fastembed\ai-gateway\src')

from converters.image_converter import ImageConverter
from pathlib import Path

def test_enhanced_table_detection():
    print('🚀 ENHANCED OCR WITH TABLE DETECTION')
    print('=' * 60)
    
    converter = ImageConverter()
    img_path = r'C:\Users\gargs\Downloads\Screenshot 2025-09-10 175920.png'
    
    # Extract with table detection
    result = converter.extract_text(img_path)
    
    if result.get('error'):
        print(f'❌ Error: {result["error"]}')
        return
    
    # Show basic stats
    print(f'📊 EXTRACTION STATS:')
    stats = result.get('statistics', {})
    print(f'   Total characters: {stats.get("total_characters", 0)}')
    print(f'   Word count: {stats.get("word_count", 0)}')
    print(f'   Confidence: {stats.get("confidence_score", 0):.1f}%')
    
    # Show table analysis results
    table_analysis = result.get('table_analysis', {})
    print(f'\n📋 TABLE DETECTION RESULTS:')
    print(f'   Tables detected: {table_analysis.get("table_count", 0)}')
    
    processing_stats = table_analysis.get('processing_stats', {})
    print(f'   Total words processed: {processing_stats.get("total_words", 0)}')
    print(f'   Confident words: {processing_stats.get("confident_words", 0)}')
    print(f'   Structured rows: {processing_stats.get("rows_detected", 0)}')
    
    # Show detected tables
    tables = table_analysis.get('tables', [])
    if tables:
        print(f'\n📊 DETECTED TABLES ({len(tables)} found):')
        print('=' * 60)
        
        for i, table in enumerate(tables):
            print(f'\nTable {i+1}:')
            print(f'  Rows: {len(table["rows"])}')
            print(f'  Columns: {len(table["columns"])}')
            print(f'  Y-range: {table.get("start_y", 0)} - {table.get("end_y", 0)}px')
            
            print(f'  Content:')
            for j, row in enumerate(table['rows'][:5]):  # Show first 5 rows
                conf = row.get('confidence', 0)
                print(f'    Row {j+1} (conf: {conf:.1f}%): {row["formatted"]}')
            
            if len(table['rows']) > 5:
                print(f'    ... and {len(table["rows"]) - 5} more rows')
    
    # Show structured text output
    structured_text = result.get('structured_text', '')
    if structured_text:
        print(f'\n📝 STRUCTURED TEXT OUTPUT:')
        print('=' * 60)
        lines = structured_text.split('\n')
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            if line.strip():
                marker = '║' if line.startswith('║') else ' '
                print(f'{marker} {line}')
        
        if len(lines) > 20:
            print(f'... and {len(lines) - 20} more lines')
    
    # Compare with raw text
    raw_text = result.get('ocr_text', '')
    print(f'\n🔄 RAW vs STRUCTURED COMPARISON:')
    print(f'   Raw text length: {len(raw_text)} chars')
    print(f'   Structured length: {len(structured_text)} chars')
    print(f'   Enhancement ratio: {len(structured_text) / len(raw_text):.2f}x' if raw_text else 'N/A')
    
    print(f'\n🎯 SUCCESS! Enhanced table detection completed!')
    return result

if __name__ == "__main__":
    result = test_enhanced_table_detection()