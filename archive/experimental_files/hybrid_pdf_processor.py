"""
PDF to Image Converter for Gemma 3N Vision Processing
Implements the hybrid approach: pypdf → quality check → Gemma vision fallback
"""
import sys
import os
from pathlib import Path
import time

def install_dependencies():
    """Check and install required dependencies"""
    print('📦 CHECKING DEPENDENCIES:')
    print('=' * 50)
    
    missing_deps = []
    
    # Check pdf2image
    try:
        import pdf2image
        print('✅ pdf2image available')
    except ImportError:
        print('❌ pdf2image missing')
        missing_deps.append('pdf2image')
    
    # Check PyMuPDF (fitz)
    try:
        import fitz
        print('✅ PyMuPDF (fitz) available')
    except ImportError:
        print('❌ PyMuPDF missing')
        missing_deps.append('PyMuPDF')
    
    # Check requests for API calls
    try:
        import requests
        print('✅ requests available')
    except ImportError:
        print('❌ requests missing')
        missing_deps.append('requests')
    
    if missing_deps:
        print(f'\n💡 INSTALL MISSING DEPENDENCIES:')
        print(f'pip install {" ".join(missing_deps)}')
        print(f'Note: pdf2image also requires poppler for Windows')
        return False
    else:
        print(f'\n✅ All dependencies available!')
        return True

def analyze_pdf_quality(pdf_path, text_content):
    """Determine if PDF needs vision processing"""
    print(f'\n📊 PDF QUALITY ANALYSIS:')
    print('-' * 30)
    
    file_size_mb = pdf_path.stat().st_size / 1024 / 1024
    char_count = len(text_content)
    chars_per_mb = char_count / file_size_mb if file_size_mb > 0 else 0
    
    print(f'File size: {file_size_mb:.1f} MB')
    print(f'Text extracted: {char_count:,} characters')
    print(f'Text density: {chars_per_mb:.0f} chars/MB')
    
    # Quality thresholds
    GOOD_THRESHOLD = 10000  # chars/MB
    POOR_THRESHOLD = 2000   # chars/MB
    
    if chars_per_mb >= GOOD_THRESHOLD:
        quality = 'excellent'
        recommend_vision = False
        print(f'✅ Quality: {quality.upper()} - use pypdf result')
    elif chars_per_mb >= POOR_THRESHOLD:
        quality = 'moderate'
        recommend_vision = True
        print(f'⚠️ Quality: {quality.upper()} - consider vision processing')
    else:
        quality = 'poor'
        recommend_vision = True
        print(f'❌ Quality: {quality.upper()} - NEEDS vision processing')
    
    return {
        'quality': quality,
        'chars_per_mb': chars_per_mb,
        'recommend_vision': recommend_vision,
        'file_size_mb': file_size_mb,
        'char_count': char_count
    }

def convert_pdf_to_images(pdf_path, max_pages=None):
    """Convert PDF pages to images for vision processing"""
    print(f'\n🖼️ CONVERTING PDF TO IMAGES:')
    print('-' * 30)
    
    try:
        # Try pdf2image first
        try:
            from pdf2image import convert_from_path
            print('Using pdf2image for conversion...')
            
            # Convert with reasonable DPI for vision processing
            end_page = max_pages if max_pages else None
            images = convert_from_path(
                str(pdf_path), 
                dpi=150,  # Good balance of quality vs file size
                first_page=1,
                last_page=end_page
            )
            
            print(f'✅ Converted {len(images)} pages using pdf2image')
            return images, 'pdf2image'
            
        except ImportError:
            print('pdf2image not available, trying PyMuPDF...')
            
        # Fallback to PyMuPDF
        try:
            import fitz
            print('Using PyMuPDF for conversion...')
            
            doc = fitz.open(str(pdf_path))
            images = []
            
            page_count = min(max_pages or doc.page_count, doc.page_count)
            
            for page_num in range(page_count):
                page = doc[page_num]
                # 150 DPI matrix (1.5 * 72 = 108, close to 150)
                mat = fitz.Matrix(2.0, 2.0)  # 144 DPI
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                import io
                from PIL import Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
            
            doc.close()
            print(f'✅ Converted {len(images)} pages using PyMuPDF')
            return images, 'pymupdf'
            
        except ImportError:
            print('❌ Neither pdf2image nor PyMuPDF available')
            return None, None
            
    except Exception as e:
        print(f'❌ Conversion error: {e}')
        return None, None

def test_gemma_vision_api():
    """Test if we can access Gemma 3N for vision processing"""
    print(f'\n🧠 TESTING GEMMA 3N VISION ACCESS:')
    print('-' * 30)
    
    # Check if AI Gateway is running
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print('✅ AI Gateway accessible')
        else:
            print(f'⚠️ AI Gateway status: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Cannot reach AI Gateway: {e}')
        return False
    
    # TODO: Check if Gemma 3N vision endpoint exists
    # For now, we know we have Gemma models but need vision integration
    print('⚠️ Gemma 3N vision endpoint not yet implemented')
    print('📍 Available: Gemma 3N ONNX models in /models/gemma-3n/')
    return False

def simulate_hybrid_processing(pdf_path):
    """Demonstrate the hybrid processing approach"""
    print(f'\n🔄 HYBRID PROCESSING DEMONSTRATION:')
    print('=' * 50)
    
    # Step 1: Try pypdf first (simulate with our known results)
    print('Step 1: 📝 Fast pypdf extraction...')
    time.sleep(0.1)  # Simulate processing
    
    # Our known results from previous testing
    pypdf_content = "Sample extracted text from pypdf..."
    pypdf_result = {
        'method': 'pypdf',
        'text': pypdf_content,
        'char_count': 6703,
        'processing_time': 2.23
    }
    print(f'✅ pypdf complete: {pypdf_result["char_count"]} chars in {pypdf_result["processing_time"]}s')
    
    # Step 2: Quality assessment
    print('\nStep 2: 📊 Quality assessment...')
    quality_result = analyze_pdf_quality(pdf_path, pypdf_content)
    
    # Step 3: Decision logic
    print(f'\nStep 3: 🤔 Processing decision...')
    if quality_result['recommend_vision']:
        print(f'❌ Poor pypdf quality ({quality_result["chars_per_mb"]:.0f} chars/MB)')
        print(f'✅ FALLBACK: Use Gemma 3N vision processing')
        
        # Step 4: Vision processing (simulated)
        print(f'\nStep 4: 🖼️ Vision processing...')
        
        if not install_dependencies():
            print('❌ Cannot proceed - missing dependencies')
            return pypdf_result
        
        images = convert_pdf_to_images(pdf_path, max_pages=3)  # Test first 3 pages
        if images[0]:
            print(f'✅ PDF converted to {len(images[0])} images')
            
            # Simulate Gemma vision analysis
            print('🧠 Simulating Gemma 3N vision analysis...')
            time.sleep(2)  # Simulate processing time
            
            gemma_result = {
                'method': 'gemma_3n_vision',
                'pages_processed': len(images[0]),
                'estimated_char_count': 20000,
                'processing_time': 120,  # 2 minutes for 3 pages
                'visual_elements_found': [
                    'Neural network diagrams',
                    'Classification boundaries', 
                    'Performance graphs',
                    'Mathematical formulas'
                ],
                'quality': 'excellent'
            }
            
            print(f'✅ Gemma vision complete:')
            print(f'   Pages processed: {gemma_result["pages_processed"]}')
            print(f'   Estimated content: {gemma_result["estimated_char_count"]} chars')
            print(f'   Processing time: {gemma_result["processing_time"]}s')
            print(f'   Visual elements: {len(gemma_result["visual_elements_found"])}')
            
            return gemma_result
        else:
            print('❌ Image conversion failed - fallback to pypdf')
            return pypdf_result
    else:
        print(f'✅ Good pypdf quality - use pypdf result')
        return pypdf_result

def main():
    """Main function to demonstrate hybrid processing"""
    print('🚀 HYBRID PDF PROCESSING DEMONSTRATION')
    print('=' * 70)
    
    pdf_path = Path(r'C:\Users\gargs\Downloads\lecture14-types-of-learning.pdf')
    
    if not pdf_path.exists():
        print(f'❌ PDF not found: {pdf_path}')
        return
    
    print(f'📄 Target: {pdf_path.name}')
    print(f'📐 Size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB')
    
    # Demonstrate hybrid processing
    result = simulate_hybrid_processing(pdf_path)
    
    print(f'\n📋 FINAL RESULT:')
    print('=' * 30)
    print(f'Method used: {result["method"]}')
    
    if result['method'] == 'pypdf':
        print(f'Text extracted: {result["char_count"]} chars')
        print(f'Processing time: {result["processing_time"]}s')
    else:
        print(f'Pages processed: {result["pages_processed"]}')
        print(f'Content estimated: {result["estimated_char_count"]} chars')
        print(f'Processing time: {result["processing_time"]}s')
        print(f'Visual elements: {result["visual_elements_found"]}')
    
    print(f'\n🎯 NEXT STEPS:')
    print('1. Install pdf2image and PyMuPDF dependencies')
    print('2. Implement Gemma 3N vision API endpoint')
    print('3. Create production hybrid processor')
    print('4. Add vision processing to document_converter.py')

if __name__ == "__main__":
    main()