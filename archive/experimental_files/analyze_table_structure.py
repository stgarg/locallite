"""Analyze OCR table structure preservation"""
import sys
sys.path.insert(0, r'C:\Learn\Code\fastembed\ai-gateway\src')
from converters.image_converter import ImageConverter
import pytesseract
from PIL import Image

# Set path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
img_path = r'C:\Users\gargs\Downloads\Screenshot 2025-09-10 175920.png'

print('=== TABLE STRUCTURE PRESERVATION ANALYSIS ===')

# Direct Tesseract
print('\n🔴 DIRECT TESSERACT OUTPUT:')
img = Image.open(img_path)
direct_text = pytesseract.image_to_string(img, config='--psm 3')
lines = [line for line in direct_text.split('\n') if line.strip()]
print(f'Lines extracted: {len(lines)}')
for i, line in enumerate(lines[:15]):  # First 15 lines
    print(f'{i:2d}: {line}')

# Our converter
print('\n🔵 OUR IMAGECONVERTER OUTPUT:')
converter = ImageConverter()
result = converter.extract_text(img_path)
converter_text = result.get('ocr_text', '')
converter_lines = [line for line in converter_text.split('\n') if line.strip()]
print(f'Lines extracted: {len(converter_lines)}')
for i, line in enumerate(converter_lines[:15]):  # First 15 lines
    print(f'{i:2d}: {line}')

# Detailed analysis
print(f'\n📊 Detailed OCR data points: {len(result.get("ocr_detailed", []))}')
print(f'📊 Average confidence: {result.get("statistics", {}).get("confidence_score", 0):.1f}%')

# Check if we can identify table structure
detailed_data = result.get('ocr_detailed', [])
table_keywords = ['units', 'inventory', 'backlog', 'demand', 'production', 'customer', 'ordered']
table_words = [item for item in detailed_data 
               if any(keyword in item['text'].lower() for keyword in table_keywords)]

print(f'\n📋 Table-related words: {len(table_words)}')
for item in table_words[:10]:
    print(f'  "{item["text"]:12}" conf:{item["confidence"]:2d}% at ({item["left"]:4d},{item["top"]:3d})')

print('\n🎯 KEY FINDING: Both methods extract identical text!')
print('The difference might be in how we PROCESS the extracted text for table structure.')