"""
Test script for document processing with Polars
Tests the multimodal document processing system without pandas dependency
"""

import sys
from pathlib import Path

# Add the ai-gateway src to Python path
ai_gateway_src = Path(__file__).parent / "ai-gateway" / "src"
sys.path.insert(0, str(ai_gateway_src))

try:
    from processors.document_processor import DocumentProcessor
    from converters.pdf_converter import PDFConverter
    from converters.docx_converter import DOCXConverter  
    from converters.image_converter import ImageConverter
    import polars as pl
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_OK = False

def test_polars_integration():
    """Test that Polars is working correctly"""
    print("🔍 Testing Polars Integration...")
    
    # Test basic Polars functionality
    try:
        df = pl.DataFrame({
            'test_column': [1, 2, 3],
            'text_column': ['hello', 'world', 'polars']
        })
        
        print(f"✅ Polars DataFrame created successfully: {df.shape}")
        print(f"   - Columns: {df.columns}")
        print(f"   - Data types: {df.dtypes}")
        return True
    except Exception as e:
        print(f"❌ Polars integration failed: {e}")
        return False

def test_converters_initialization():
    """Test that all converters can be initialized"""
    print("\n🔧 Testing Converter Initialization...")
    
    if not IMPORTS_OK:
        print("❌ Cannot test converters - imports failed")
        return False
    
    tests = []
    
    # Test PDF Converter
    try:
        pdf_conv = PDFConverter()
        print(f"✅ PDFConverter initialized - OCR enabled: {pdf_conv.ocr_enabled}")
        print(f"   - Supported formats: {pdf_conv.supported_formats}")
        tests.append(True)
    except Exception as e:
        print(f"❌ PDFConverter failed: {e}")
        tests.append(False)
    
    # Test DOCX Converter  
    try:
        docx_conv = DOCXConverter()
        print(f"✅ DOCXConverter initialized")
        print(f"   - Supported formats: {docx_conv.supported_formats}")
        tests.append(True)
    except Exception as e:
        print(f"❌ DOCXConverter failed: {e}")
        tests.append(False)
    
    # Test Image Converter
    try:
        img_conv = ImageConverter()
        print(f"✅ ImageConverter initialized - OCR enabled: {img_conv.ocr_enabled}")
        print(f"   - Supported formats: {img_conv.supported_formats}")
        tests.append(True)
    except Exception as e:
        print(f"❌ ImageConverter failed: {e}")
        tests.append(False)
    
    return all(tests)

def test_document_processor():
    """Test the unified document processor"""
    print("\n🏗️ Testing Document Processor...")
    
    if not IMPORTS_OK:
        print("❌ Cannot test processor - imports failed")
        return False
    
    try:
        processor = DocumentProcessor()
        
        print(f"✅ DocumentProcessor initialized")
        print(f"   - Available converters: {list(processor.converters.keys())}")
        
        supported_formats = processor.get_supported_formats()
        print(f"   - All supported formats: {supported_formats}")
        
        # Test format detection
        test_files = [
            "test.pdf",
            "document.docx", 
            "image.png",
            "unknown.xyz"
        ]
        
        print("   - Format detection tests:")
        for test_file in test_files:
            format_type = processor.detect_format(Path(test_file))
            print(f"     {test_file} -> {format_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ DocumentProcessor failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n📦 Testing Dependencies...")
    
    dependencies = {
        'polars': 'pl',
        'pypdf': 'PdfReader',
        'python-docx': 'Document', 
        'PIL': 'Image',
        'pytesseract': 'pytesseract'
    }
    
    results = []
    
    for dep_name, import_test in dependencies.items():
        try:
            if dep_name == 'polars':
                import polars as pl
                print(f"✅ {dep_name}: {pl.__version__}")
            elif dep_name == 'pypdf':
                from pypdf import PdfReader
                print(f"✅ {dep_name}: Available")
            elif dep_name == 'python-docx':
                from docx import Document
                print(f"✅ {dep_name}: Available")
            elif dep_name == 'PIL':
                from PIL import Image
                print(f"✅ {dep_name}: Available")
            elif dep_name == 'pytesseract':
                import pytesseract
                try:
                    version = pytesseract.get_tesseract_version()
                    print(f"✅ {dep_name}: Tesseract {version}")
                except:
                    print(f"⚠️ {dep_name}: Installed but Tesseract binary not found")
            
            results.append(True)
        except ImportError as e:
            print(f"❌ {dep_name}: Not available ({e})")
            results.append(False)
        except Exception as e:
            print(f"⚠️ {dep_name}: Available but issue detected ({e})")
            results.append(True)
    
    return all(results)

def main():
    """Run all tests"""
    print("🚀 Document Processing System Test (Polars Edition)")
    print("=" * 60)
    
    tests = [
        ("Polars Integration", test_polars_integration),
        ("Dependencies", test_dependencies),
        ("Converter Initialization", test_converters_initialization),
        ("Document Processor", test_document_processor),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status} {test_name}")
    
    overall_success = all(results)
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Your multimodal document processing system is ready!")
        print("   • Polars is working instead of pandas")
        print("   • All converters are properly initialized") 
        print("   • Document processor is functional")
        print("\n📝 Next Steps:")
        print("   1. Create sample documents for testing")
        print("   2. Add document processing endpoints to FastAPI")
        print("   3. Test with real document files")
    else:
        print("\n🔧 Issues found - please check the failing tests above")

if __name__ == "__main__":
    main()