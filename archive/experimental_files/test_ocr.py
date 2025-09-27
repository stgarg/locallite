"""
Test OCR functionality with Tesseract
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Add our source to path
sys.path.insert(0, r'C:\Learn\Code\fastembed\ai-gateway\src')

def create_test_image():
    """Create a simple test image with text"""
    # Create a white background image
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some text
    text_lines = [
        "Tesseract OCR Test Document",
        "This is a sample image with text for OCR testing.",
        "The text should be extracted successfully.",
        "Date: September 24, 2025",
        "Status: Testing ARM64 Windows compatibility"
    ]
    
    y_position = 50
    for line in text_lines:
        draw.text((50, y_position), line, fill='black')
        y_position += 60
    
    # Save test image
    test_path = Path(__file__).parent / 'test_ocr_image.png'
    img.save(test_path)
    print(f"✅ Created test image: {test_path}")
    return test_path

def test_image_converter():
    """Test our ImageConverter with the test image"""
    from converters.image_converter import ImageConverter
    
    print("\n=== Testing ImageConverter ===")
    converter = ImageConverter()
    
    # Create test image
    test_image_path = create_test_image()
    
    if converter.ocr_enabled:
        print("✅ OCR is enabled")
        
        try:
            # Extract text from image 
            result = converter.extract_text(test_image_path)
            
            print(f"\n📄 Extracted Text:")
            print("-" * 50)
            print(result.get('text', 'No text found'))
            print("-" * 50)
            
            print(f"\n📊 Analysis Results:")
            analysis = result.get('analysis', {})
            for key, value in analysis.items():
                print(f"   {key}: {value}")
                
            print(f"\n🎯 Success! OCR extracted {len(result.get('text', ''))} characters")
            
        except Exception as e:
            print(f"❌ Error during OCR: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ OCR is not enabled")
    
    # Cleanup
    if test_image_path.exists():
        test_image_path.unlink()
        print(f"🧹 Cleaned up test image")

if __name__ == "__main__":
    test_image_converter()