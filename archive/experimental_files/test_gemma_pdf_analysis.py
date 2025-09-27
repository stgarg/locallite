"""
Test Gemma 3N on the learning PDF document
Compare with our pypdf extraction results
"""
import json
import requests
import base64
from pathlib import Path
import time

def test_gemma_on_pdf():
    print('🧠 TESTING GEMMA 3N ON LEARNING PDF')
    print('=' * 60)
    
    pdf_path = Path(r'C:\Users\gargs\Downloads\lecture14-types-of-learning.pdf')
    
    if not pdf_path.exists():
        print('❌ PDF file not found!')
        return
    
    print(f'📄 Document: {pdf_path.name}')
    print(f'Size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB')
    
    # Test 1: Check if AI Gateway is running
    print(f'\n🔍 Testing AI Gateway connection...')
    try:
        response = requests.get('http://localhost:8000/v1/models', timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f'✅ AI Gateway is running')
            print(f'Available models: {[m["id"] for m in models.get("data", [])]}')
            gateway_running = True
        else:
            print(f'⚠️ AI Gateway responded but with status {response.status_code}')
            gateway_running = False
    except requests.exceptions.RequestException as e:
        print(f'❌ AI Gateway not accessible: {e}')
        gateway_running = False
    
    if not gateway_running:
        print(f'\n💡 To start AI Gateway:')
        print(f'   cd ai-gateway/src')
        print(f'   python model_router.py')
        return
    
    # Test 2: Ask Gemma to analyze the PDF concept
    print(f'\n🧠 Testing Gemma 3N understanding...')
    
    # First, let's ask about machine learning concepts without the PDF
    chat_request = {
        "model": "gemma-3n-4b",
        "messages": [
            {
                "role": "user", 
                "content": """I have a PDF titled 'lecture14-types-of-learning.pdf' that seems to be about machine learning concepts. 
                
Can you explain the main types of machine learning approaches that would typically be covered in such a lecture? 
Please be comprehensive and explain:
1. Supervised Learning
2. Unsupervised Learning  
3. Reinforcement Learning
4. Any other important learning types

Focus on practical differences and use cases."""
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/v1/chat/completions',
            json=chat_request,
            timeout=30
        )
        gemma_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            usage = result.get('usage', {})
            
            print(f'✅ Gemma 3N Response ({gemma_time:.2f}s):')
            print(f'Input tokens: {usage.get("prompt_tokens", "unknown")}')
            print(f'Output tokens: {usage.get("completion_tokens", "unknown")}')
            print(f'Total tokens: {usage.get("total_tokens", "unknown")}')
            print(f'\n📖 Content (first 800 chars):')
            print('-' * 50)
            print(content[:800] + '...' if len(content) > 800 else content)
            print('-' * 50)
            
            return {
                'success': True,
                'content': content,
                'processing_time': gemma_time,
                'tokens': usage,
                'content_length': len(content)
            }
            
        else:
            print(f'❌ Gemma request failed: {response.status_code}')
            print(f'Response: {response.text}')
            return {'success': False, 'error': response.text}
            
    except requests.exceptions.RequestException as e:
        print(f'❌ Request failed: {e}')
        return {'success': False, 'error': str(e)}

def compare_extraction_methods():
    """Compare our pypdf results with Gemma's conceptual understanding"""
    print(f'\n📊 COMPARISON: PYPDF vs GEMMA 3N')
    print('=' * 60)
    
    # Our pypdf results (from previous test)
    pypdf_stats = {
        'characters': 6703,
        'processing_time': 2.23,
        'pages': 24,
        'learning_mentions': 51,
        'approach': 'Direct text extraction'
    }
    
    print(f'🔵 Our pypdf extraction:')
    print(f'   Characters extracted: {pypdf_stats["characters"]:,}')
    print(f'   Processing time: {pypdf_stats["processing_time"]}s')
    print(f'   Pages processed: {pypdf_stats["pages"]}')
    print(f'   "Learning" mentions: {pypdf_stats["learning_mentions"]}')
    print(f'   Approach: {pypdf_stats["approach"]}')
    
    # Test Gemma
    gemma_result = test_gemma_on_pdf()
    
    if gemma_result and gemma_result['success']:
        print(f'\n🧠 Gemma 3N analysis:')
        print(f'   Content generated: {gemma_result["content_length"]:,} characters')
        print(f'   Processing time: {gemma_result["processing_time"]:.2f}s')
        print(f'   Tokens used: {gemma_result["tokens"].get("total_tokens", "unknown")}')
        print(f'   Approach: Conceptual understanding + generation')
        
        print(f'\n🎯 Key Insights:')
        print(f'   • pypdf: Fast extraction but poor quality from image-heavy PDF')
        print(f'   • Gemma: Rich conceptual content but based on training, not document')
        print(f'   • Future: Gemma vision could process PDF pages as images')
        
        # Analyze Gemma's content for learning concepts
        content_lower = gemma_result['content'].lower()
        ml_concepts = ['supervised', 'unsupervised', 'reinforcement', 'deep learning', 'neural', 'classification', 'regression']
        
        print(f'\n🔍 Gemma concept coverage:')
        for concept in ml_concepts:
            if concept in content_lower:
                print(f'   ✅ {concept.title()}')
            else:
                print(f'   ❌ {concept.title()}')
    
    return gemma_result

if __name__ == "__main__":
    result = compare_extraction_methods()
    print(f'\n🚀 Analysis complete!')
    
    if result and result['success']:
        print(f'💡 Next step: Implement PDF page-to-image conversion for Gemma vision processing')
    else:
        print(f'💡 Start AI Gateway first: cd ai-gateway/src && python model_router.py')