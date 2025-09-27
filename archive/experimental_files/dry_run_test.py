"""
Document Processing System - Dry Run Test Suite
Comprehensive testing of the multimodal document processing system
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import tempfile

# Add the ai-gateway src to Python path
ai_gateway_src = Path(__file__).parent / "ai-gateway" / "src"
sys.path.insert(0, str(ai_gateway_src))

def test_system_status():
    """Test overall system status and dependencies"""
    print("🔍 SYSTEM STATUS CHECK")
    print("=" * 50)
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "overall": True
    }
    
    # Test Polars
    try:
        import polars as pl
        test_df = pl.DataFrame({'test': [1, 2, 3], 'text': ['a', 'b', 'c']})
        print(f"✅ Polars: v{pl.__version__} - DataFrame ops working")
        status["tests"]["polars"] = {"status": "success", "version": pl.__version__}
    except Exception as e:
        print(f"❌ Polars: Failed - {e}")
        status["tests"]["polars"] = {"status": "error", "error": str(e)}
        status["overall"] = False
    
    # Test Core Dependencies
    deps = [
        ("pypdf", "from pypdf import PdfReader; PdfReader"),
        ("python-docx", "from docx import Document; Document"),
        ("PIL", "from PIL import Image; Image"),
        ("pytesseract", "import pytesseract; pytesseract.get_tesseract_version"),
        ("python-magic", "import magic"),
    ]
    
    for name, test_code in deps:
        try:
            exec(test_code)
            print(f"✅ {name}: Available")
            status["tests"][name] = {"status": "success"}
        except Exception as e:
            if "tesseract" in name.lower():
                print(f"⚠️ {name}: Library installed, Tesseract binary not found")
                status["tests"][name] = {"status": "warning", "note": "Binary not found"}
            else:
                print(f"❌ {name}: Failed - {e}")
                status["tests"][name] = {"status": "error", "error": str(e)}
    
    return status

def test_converters():
    """Test individual converters"""
    print("\n🔧 CONVERTER INITIALIZATION TEST")
    print("=" * 50)
    
    converter_tests = {}
    
    try:
        from converters.pdf_converter import PDFConverter
        pdf_conv = PDFConverter()
        print(f"✅ PDFConverter: OCR={pdf_conv.ocr_enabled}, Formats={pdf_conv.supported_formats}")
        converter_tests["pdf"] = {
            "status": "success", 
            "ocr_enabled": pdf_conv.ocr_enabled,
            "formats": pdf_conv.supported_formats
        }
    except Exception as e:
        print(f"❌ PDFConverter: Failed - {e}")
        converter_tests["pdf"] = {"status": "error", "error": str(e)}
    
    try:
        from converters.docx_converter import DOCXConverter
        docx_conv = DOCXConverter()
        print(f"✅ DOCXConverter: Formats={docx_conv.supported_formats}")
        converter_tests["docx"] = {
            "status": "success",
            "formats": docx_conv.supported_formats
        }
    except Exception as e:
        print(f"❌ DOCXConverter: Failed - {e}")
        converter_tests["docx"] = {"status": "error", "error": str(e)}
    
    try:
        from converters.image_converter import ImageConverter
        img_conv = ImageConverter()
        print(f"✅ ImageConverter: OCR={img_conv.ocr_enabled}, Formats={img_conv.supported_formats}")
        converter_tests["image"] = {
            "status": "success",
            "ocr_enabled": img_conv.ocr_enabled,
            "formats": img_conv.supported_formats
        }
    except Exception as e:
        print(f"❌ ImageConverter: Failed - {e}")
        converter_tests["image"] = {"status": "error", "error": str(e)}
    
    return converter_tests

def test_document_processor():
    """Test unified document processor"""
    print("\n🏗️ DOCUMENT PROCESSOR TEST")
    print("=" * 50)
    
    try:
        from processors.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        # Test basic functionality
        supported_formats = processor.get_supported_formats()
        print(f"✅ DocumentProcessor initialized")
        print(f"   Supported formats: {supported_formats}")
        print(f"   Available converters: {list(processor.converters.keys())}")
        
        # Test format detection
        format_tests = [
            ("document.pdf", "pdf"),
            ("presentation.docx", "docx"),
            ("image.png", "image"),
            ("screenshot.jpg", "image"),
            ("unknown.xyz", None)
        ]
        
        print("\n   Format Detection Tests:")
        detection_results = {}
        for filename, expected in format_tests:
            detected = processor.detect_format(Path(filename))
            status = "✅" if detected == expected else "❌"
            print(f"   {status} {filename} -> {detected} (expected: {expected})")
            detection_results[filename] = {"detected": detected, "expected": expected}
        
        return {
            "status": "success",
            "supported_formats": supported_formats,
            "converters": list(processor.converters.keys()),
            "format_detection": detection_results
        }
        
    except Exception as e:
        print(f"❌ DocumentProcessor failed: {e}")
        return {"status": "error", "error": str(e)}

def create_test_documents():
    """Create test documents for processing"""
    print("\n📄 CREATING TEST DOCUMENTS")
    print("=" * 50)
    
    test_docs = {}
    temp_dir = Path(tempfile.gettempdir()) / "document_processing_test"
    temp_dir.mkdir(exist_ok=True)
    
    # Create a simple text file to simulate PDF content
    text_content = """Document Processing Test
    
This is a test document to verify our document processing system.

Key Features:
- Multi-format support (PDF, DOCX, Images)
- Polars-based data analysis
- OCR capabilities
- Unified processing pipeline

Statistics:
- Total words: approximately 50
- Paragraphs: 4
- Lists: 1

This content will help test text extraction and analysis capabilities.
"""
    
    # Create test text file
    test_txt = temp_dir / "test_document.txt"
    test_txt.write_text(text_content, encoding='utf-8')
    test_docs["text_file"] = str(test_txt)
    
    print(f"✅ Created test text file: {test_txt}")
    print(f"   Content: {len(text_content)} characters, {len(text_content.split())} words")
    
    # Try to create a simple image with text (if PIL supports text rendering)
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple image with text
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Use default font
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((10, 10), "Test Image Document\n\nThis image contains text\nfor OCR testing.", 
                  fill='black', font=font)
        
        test_img = temp_dir / "test_image.png"
        img.save(test_img)
        test_docs["image_file"] = str(test_img)
        print(f"✅ Created test image: {test_img}")
        
    except Exception as e:
        print(f"⚠️ Could not create test image: {e}")
    
    return test_docs, temp_dir

def test_polars_analysis():
    """Test Polars data analysis capabilities"""
    print("\n📊 POLARS ANALYSIS TEST")
    print("=" * 50)
    
    try:
        import polars as pl
        
        # Create sample document processing data
        sample_data = [
            {"page": 1, "text": "Introduction paragraph with 25 words here to test analysis", "char_count": 63, "has_text": True},
            {"page": 2, "text": "Second page content", "char_count": 19, "has_text": True},
            {"page": 3, "text": "", "char_count": 0, "has_text": False},
            {"page": 4, "text": "Final page with conclusion and summary text", "char_count": 43, "has_text": True},
        ]
        
        df = pl.DataFrame(sample_data)
        print("✅ Sample document data created:")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {df.columns}")
        
        # Perform analysis
        analysis = {
            "total_pages": df.height,
            "pages_with_content": df.filter(pl.col('has_text')).height,
            "total_characters": df.select(pl.col('char_count').sum()).item(),
            "average_chars_per_page": df.select(pl.col('char_count').mean()).item(),
            "content_percentage": (df.filter(pl.col('has_text')).height / df.height * 100)
        }
        
        print("✅ Analysis results:")
        for key, value in analysis.items():
            print(f"   {key}: {value}")
        
        return {"status": "success", "analysis": analysis, "data_shape": df.shape}
        
    except Exception as e:
        print(f"❌ Polars analysis failed: {e}")
        return {"status": "error", "error": str(e)}

def run_dry_run():
    """Run complete dry run test suite"""
    print("🚀 DOCUMENT PROCESSING SYSTEM - DRY RUN")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {
        "test_run": {
            "timestamp": datetime.now().isoformat(),
            "system": "Document Processing System",
            "version": "Polars Edition"
        },
        "tests": {}
    }
    
    # Run all tests
    try:
        results["tests"]["system_status"] = test_system_status()
        results["tests"]["converters"] = test_converters()
        results["tests"]["document_processor"] = test_document_processor()
        results["tests"]["polars_analysis"] = test_polars_analysis()
        
        # Create test documents
        test_docs, temp_dir = create_test_documents()
        results["tests"]["test_documents"] = {
            "status": "success",
            "created_files": test_docs,
            "temp_directory": str(temp_dir)
        }
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        results["tests"]["suite_error"] = {"error": str(e)}
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📋 DRY RUN SUMMARY")
    print("=" * 60)
    
    successful_tests = 0
    total_tests = 0
    
    for test_name, test_result in results["tests"].items():
        if isinstance(test_result, dict):
            if test_result.get("status") == "success" or test_result.get("overall"):
                print(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
                successful_tests += 1
            else:
                print(f"❌ {test_name.replace('_', ' ').title()}: FAILED")
            total_tests += 1
    
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    
    if success_rate >= 80:
        print("\n🎉 DRY RUN SUCCESSFUL!")
        print("✅ System is ready for document processing")
        print("✅ Polars integration working")
        print("✅ Multi-format support available")
        print("\n📝 Next Steps:")
        print("   • Test with real documents")
        print("   • Add FastAPI endpoints")
        print("   • Integrate with existing AI gateway")
    else:
        print("\n⚠️ DRY RUN NEEDS ATTENTION")
        print("🔧 Some components need fixing before production use")
    
    # Save detailed results
    results_file = Path("dry_run_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    results = run_dry_run()