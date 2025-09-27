"""Extract and analyze the learning PDF content"""
import sys
sys.path.insert(0, r'C:\Learn\Code\fastembed\ai-gateway\src')
from converters.pdf_converter import PDFConverter
from pathlib import Path

def analyze_learning_pdf():
    print('📖 LEARNING PDF CONTENT ANALYSIS')
    print('=' * 60)
    
    pdf_path = Path(r'C:\Users\gargs\Downloads\lecture14-types-of-learning.pdf')
    converter = PDFConverter()
    result = converter.extract_text(pdf_path)
    
    text = result.get('full_text', '')
    pages = result.get('pages', [])
    
    print(f'📊 Extraction Summary:')
    print(f'   Pages: {len(pages)}')
    print(f'   Total characters: {len(text):,}')
    print(f'   Word count: {len(text.split()):,}')
    
    if pages:
        print(f'\n📄 Page 1 Sample (first 400 chars):')
        page1 = pages[0].get('content', '')
        print(page1[:400] + '...' if len(page1) > 400 else page1)
        
        if len(pages) > 1:
            print(f'\n📄 Page 2 Sample (first 300 chars):')
            page2 = pages[1].get('content', '')
            print(page2[:300] + '...' if len(page2) > 300 else page2)
    
    # Content analysis
    print(f'\n🔍 Content Keywords Analysis:')
    keywords = [
        'learning', 'machine', 'supervised', 'unsupervised', 
        'reinforcement', 'algorithm', 'classification', 'regression',
        'neural', 'network', 'data', 'training'
    ]
    
    for keyword in keywords:
        count = text.lower().count(keyword)
        if count > 0:
            print(f'   "{keyword}": {count} occurrences')
    
    # Look for specific learning types
    print(f'\n🧠 Learning Types Mentioned:')
    learning_types = [
        'supervised learning', 'unsupervised learning', 
        'reinforcement learning', 'deep learning',
        'semi-supervised', 'active learning'
    ]
    
    for ltype in learning_types:
        count = text.lower().count(ltype.lower())
        if count > 0:
            print(f'   "{ltype}": {count} mentions')
    
    # Show document structure
    print(f'\n📋 Document Structure:')
    non_empty_pages = [i for i, page in enumerate(pages) if page.get('content', '').strip()]
    print(f'   Pages with content: {len(non_empty_pages)}/{len(pages)}')
    
    if non_empty_pages:
        print(f'   Content distribution:')
        for i in non_empty_pages[:5]:  # First 5 content pages
            content_len = len(pages[i].get('content', ''))
            print(f'     Page {i+1}: {content_len} characters')
    
    return {
        'total_pages': len(pages),
        'total_chars': len(text),
        'content_pages': len(non_empty_pages),
        'sample_content': page1[:200] if pages else '',
        'keywords_found': {kw: text.lower().count(kw) for kw in keywords if text.lower().count(kw) > 0}
    }

if __name__ == "__main__":
    results = analyze_learning_pdf()
    print(f'\n🎯 Analysis complete! Ready for documentation compilation.')