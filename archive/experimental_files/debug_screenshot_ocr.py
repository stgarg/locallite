"""Debug OCR on screenshot with different configurations"""
import pytesseract
from PIL import Image

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the screenshot
img_path = r'C:\Users\gargs\Downloads\Screenshot 2025-09-10 175920.png'
img = Image.open(img_path)

print(f'=== Screenshot OCR Debug ===')
print(f'Image size: {img.size}')
print(f'Image mode: {img.mode}')

# Try OCR with different configurations
configs = [
    ('--psm 3', 'Fully automatic page segmentation'),
    ('--psm 6', 'Uniform block of text'),
    ('--psm 7', 'Single text line'),
    ('--psm 8', 'Single word'),
    ('--psm 11', 'Sparse text detection'),
    ('', 'Default configuration')
]

for config, description in configs:
    try:
        text = pytesseract.image_to_string(img, config=config).strip()
        print(f'\n📝 {description} ({config or "default"}):')
        print(f'   Length: {len(text)} characters')
        if text:
            preview = text.replace('\n', '\\n')[:150]
            print(f'   Preview: {preview}{"..." if len(text) > 150 else ""}')
        else:
            print('   No text detected')
    except Exception as e:
        print(f'   ❌ Failed: {e}')

# Also try to get detailed data to see what Tesseract is seeing
print(f'\n🔍 Detailed OCR Analysis:')
try:
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    confident_words = [word for i, word in enumerate(data['text']) 
                      if int(data['conf'][i]) > 30 and word.strip()]
    print(f'   Confident words found: {len(confident_words)}')
    if confident_words:
        print(f'   Words: {confident_words[:10]}{"..." if len(confident_words) > 10 else ""}')
except Exception as e:
    print(f'   ❌ Detailed analysis failed: {e}')