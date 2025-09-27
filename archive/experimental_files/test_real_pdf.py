"""
Real Document Processing Test with Actual PDF
Test with the user's actual PDF document
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add the ai-gateway src to Python path
ai_gateway_src = Path(__file__).parent / "ai-gateway" / "src"
sys.path.insert(0, str(ai_gateway_src))

def process_real_pdf():
    """Process the actual PDF document"""
    print("📄 PROCESSING REAL PDF DOCUMENT")
    print("=" * 60)
    
    pdf_path = Path(r"C:\Users\gargs\Downloads\4722_Math_model_paper.docx (10).pdf")
    
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return False
    
    print(f"✅ Found PDF: {pdf_path.name}")
    print(f"   Size: {pdf_path.stat().st_size / 1024:.1f} KB")
    
    try:
        # Import the document processor
        from processors.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        print(f"✅ DocumentProcessor loaded")
        print(f"   Supported formats: {len(processor.get_supported_formats())} formats")
        
        # Detect format
        detected_format = processor.detect_format(pdf_path)
        print(f"✅ Format detected: {detected_format}")
        
        if detected_format != 'pdf':
            print(f"❌ Expected PDF format, got: {detected_format}")
            return False
        
        # Process the document
        print("\n🔍 Processing document...")
        result = processor.process_document(pdf_path)
        
        if result['status'] == 'success':
            print("✅ Document processed successfully!")
            
            # Display results
            metadata = result.get('metadata', {})
            statistics = result.get('statistics', {})
            
            print(f"\n📊 Document Analysis:")
            print(f"   Filename: {metadata.get('filename', 'Unknown')}")
            print(f"   File size: {metadata.get('file_size', 0) / 1024:.1f} KB")
            print(f"   Total pages: {statistics.get('total_pages', 0)}")
            print(f"   Total characters: {statistics.get('total_characters', 0):,}")
            print(f"   Non-empty pages: {statistics.get('non_empty_pages', 0)}")
            print(f"   Empty pages: {statistics.get('empty_pages', 0)}")
            print(f"   Average chars/page: {statistics.get('average_chars_per_page', 0):.1f}")
            print(f"   Extraction method: {statistics.get('extraction_method', 'Unknown')}")
            
            # Show first few pages preview
            pages = result.get('pages', [])
            if pages:
                print(f"\n📝 Content Preview (first 3 pages):")
                for i, page in enumerate(pages[:3]):
                    text = page.get('text', '')
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"   Page {page.get('page_number', i+1)}: {len(text)} chars")
                    if text.strip():
                        print(f"      \"{preview}\"")
                    else:
                        print(f"      [Empty page]")
            
            # Test Polars DataFrame if available
            if result.get('pages_dataframe') is not None:
                df = result['pages_dataframe']
                print(f"\n📈 Polars Analysis:")
                print(f"   DataFrame shape: {df.shape}")
                print(f"   Columns: {df.columns}")
                
                # Simple analysis
                if df.height > 0:
                    total_chars = df.select('char_count').sum().item() if 'char_count' in df.columns else 0
                    pages_with_text = df.filter(df['has_text']).height if 'has_text' in df.columns else 0
                    print(f"   Pages with text: {pages_with_text}/{df.height}")
                    print(f"   Total characters: {total_chars:,}")
            
            return True
            
        else:
            print(f"❌ Document processing failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Processing failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_polars_fix():
    """Test the Polars group_by fix"""
    print("\n🔧 TESTING POLARS GROUP_BY FIX")
    print("=" * 60)
    
    try:
        import polars as pl
        
        # Create test data similar to what we'd get from document processing
        test_data = [
            {'file_name': 'doc1.pdf', 'format_type': 'pdf', 'success': False, 'converter': 'PDFConverter'},
            {'file_name': 'doc2.docx', 'format_type': 'docx', 'success': False, 'converter': 'DOCXConverter'},
            {'file_name': 'image.png', 'format_type': 'image', 'success': False, 'converter': 'ImageConverter'},
            {'file_name': 'real.pdf', 'format_type': 'pdf', 'success': True, 'converter': 'PDFConverter'},
        ]
        
        df = pl.DataFrame(test_data)
        print(f"✅ Test DataFrame created: {df.shape}")
        
        # Test the fixed group_by syntax
        format_dist = df.group_by('format_type').count().to_dict(as_series=False)
        converter_usage = df.group_by('converter').count().to_dict(as_series=False)
        
        print(f"✅ Format distribution: {format_dist}")
        print(f"✅ Converter usage: {converter_usage}")
        
        # Test summary generation
        from processors.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        # Create mock results
        mock_results = {
            'file1.pdf': {
                'status': 'error',
                'processing_metadata': {'detected_format': 'pdf', 'converter_used': 'PDFConverter'}
            },
            'file2.pdf': {
                'status': 'success',
                'processing_metadata': {'detected_format': 'pdf', 'converter_used': 'PDFConverter'},
                'statistics': {'total_characters': 1000, 'total_pages': 5}
            }
        }
        
        summary = processor.get_processing_summary(mock_results)
        print(f"✅ Summary generated: {summary['summary']['total_files']} files")
        print(f"   Success rate: {summary['summary']['success_rate']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Polars test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run real document processing test"""
    print("🚀 REAL DOCUMENT PROCESSING WITH ACTUAL PDF")
    print("=" * 70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    results = []
    
    # Test 1: Polars fix
    print(">>> Test 1: Polars Group By Fix")
    result1 = test_polars_fix()
    results.append(("Polars Fix", result1))
    
    # Test 2: Real PDF processing
    print("\n>>> Test 2: Real PDF Document Processing")
    result2 = process_real_pdf()
    results.append(("PDF Processing", result2))
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
    
    overall_success = all(result for _, result in results)
    success_rate = sum(result for _, result in results) / len(results) * 100
    
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({sum(result for _, result in results)}/{len(results)})")
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Document processing system working with real documents")
        print("✅ Polars integration fixed and operational")
        print("✅ Ready for production use")
    else:
        print("\n⚠️ Some tests failed - check the output above")
    
    return overall_success

if __name__ == "__main__":
    success = main()