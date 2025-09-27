"""Test OCR with real screenshot"""
import sys
sys.path.insert(0, r'C:\Learn\Code\fastembed\ai-gateway\src')

from converters.image_converter import ImageConverter
from pathlib import Path

def test_screenshot_ocr():
    # Test with the real screenshot
    screenshot_path = Path(r'C:\Users\gargs\Downloads\Screenshot 2025-09-10 175920.png')
    
    print('=== OCR Test with Real Screenshot ===')
    print(f'File: {screenshot_path}')
    print(f'File exists: {screenshot_path.exists()}')
    
    if not screenshot_path.exists():
        print('❌ Screenshot file not found!')
        return
    
    converter = ImageConverter()
    print(f'OCR enabled: {converter.ocr_enabled}')
    
    try:
        result = converter.extract_text(screenshot_path)
        
        text = result.get('ocr_text', result.get('full_text', 'No text found'))
        print(f'\n📄 Extracted Text ({len(text)} characters):')
        print('=' * 60)
        print(text)
        print('=' * 60)
        
        # Show metadata
        metadata = result.get('metadata', {})
        if metadata:
            print(f'\n📊 Image Info:')
            print(f'   Size: {metadata.get("image_size", "Unknown")}')
            print(f'   Format: {metadata.get("image_format", "Unknown")}')
            print(f'   File size: {metadata.get("file_size", "Unknown")} bytes')
        
        # Show analysis
        analysis = result.get('analysis', {})
        if analysis:
            print(f'\n🔍 Analysis:')
            for key, value in analysis.items():
                print(f'   {key}: {value}')
        
        # Show any errors
        if result.get('error'):
            print(f'\n❌ Error: {result["error"]}')
        else:
            print(f'\n🎉 OCR completed successfully!')
            
    except Exception as e:
        print(f'❌ Exception: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_screenshot_ocr()