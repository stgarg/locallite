"""
REAL Gemma 3N Testing - Actually test capabilities instead of theorizing
"""
import requests
import json
import time
from pathlib import Path

def test_ai_gateway_endpoints():
    """Actually check what endpoints exist and work"""
    print('🔍 REAL AI GATEWAY TESTING')
    print('=' * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Is it actually running?
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f'✅ Health check: {response.status_code}')
        if response.status_code == 200:
            print(f'   Response: {response.json()}')
        else:
            print(f'   Error: {response.text}')
    except Exception as e:
        print(f'❌ Cannot connect to AI Gateway: {e}')
        return False
    
    # Test 2: What models are available?
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        print(f'\n📋 Models endpoint: {response.status_code}')
        if response.status_code == 200:
            models = response.json()
            print(f'   Available models: {models}')
        else:
            print(f'   Error: {response.text}')
    except Exception as e:
        print(f'❌ Models endpoint error: {e}')
    
    # Test 3: Can we generate embeddings? (existing functionality)
    try:
        payload = {
            "input": ["Test text for embedding"],
            "model": "bge-small-en-v1.5"
        }
        response = requests.post(f"{base_url}/v1/embeddings", json=payload, timeout=30)
        print(f'\n🔢 Embeddings endpoint: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print(f'   ✅ Embeddings work: {len(result.get("data", []))} vectors')
        else:
            print(f'   ❌ Error: {response.text}')
    except Exception as e:
        print(f'❌ Embeddings error: {e}')
    
    return True

def test_gemma_model_files():
    """Actually check what Gemma files we have"""
    print(f'\n📁 REAL GEMMA 3N FILE ANALYSIS')
    print('=' * 50)
    
    gemma_path = Path('C:/Learn/Code/fastembed/models/gemma-3n')
    
    if not gemma_path.exists():
        print('❌ No Gemma 3N directory found')
        return False
    
    print(f'📂 Gemma directory exists: {gemma_path}')
    
    # Check what files actually exist
    all_files = list(gemma_path.rglob('*'))
    print(f'📄 Total files: {len(all_files)}')
    
    # Categorize files
    onnx_files = [f for f in all_files if f.suffix == '.onnx']
    json_files = [f for f in all_files if f.suffix == '.json']
    data_files = [f for f in all_files if 'data' in f.name]
    
    print(f'\n📊 File breakdown:')
    print(f'   ONNX models: {len(onnx_files)}')
    for onnx in onnx_files:
        size_mb = onnx.stat().st_size / 1024 / 1024
        print(f'     • {onnx.name} ({size_mb:.1f} MB)')
    
    print(f'   JSON configs: {len(json_files)}')
    for json_file in json_files:
        print(f'     • {json_file.name}')
    
    print(f'   Data files: {len(data_files)}')
    for data_file in data_files:
        size_mb = data_file.stat().st_size / 1024 / 1024
        print(f'     • {data_file.name} ({size_mb:.1f} MB)')
    
    return True

def attempt_real_pdf_test():
    """Try to actually test PDF processing (will likely fail, but let's see)"""
    print(f'\n📄 ACTUAL PDF PROCESSING ATTEMPT')
    print('=' * 50)
    
    pdf_path = Path(r'C:\Users\gargs\Downloads\lecture14-types-of-learning.pdf')
    
    if not pdf_path.exists():
        print(f'❌ PDF not found: {pdf_path}')
        return False
    
    print(f'📄 PDF found: {pdf_path.name}')
    print(f'📐 Size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB')
    
    # Try to read PDF as binary data
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        print(f'📊 Read {len(pdf_bytes):,} bytes from PDF')
        
        # Can we somehow send this to Gemma? (Probably not directly)
        # Let's see if there's any PDF endpoint
        try:
            # This will probably fail, but let's try
            files = {'file': ('lecture14.pdf', pdf_bytes, 'application/pdf')}
            response = requests.post("http://127.0.0.1:8000/v1/analyze-pdf", files=files, timeout=60)
            
            print(f'📤 PDF upload attempt: {response.status_code}')
            if response.status_code == 200:
                print(f'🎉 PDF processing worked!')
                print(f'Response: {response.json()}')
            else:
                print(f'❌ PDF endpoint error: {response.text}')
                
        except requests.exceptions.ConnectionError:
            print(f'❌ No PDF endpoint exists (expected)')
        except Exception as e:
            print(f'❌ PDF upload error: {e}')
    
    except Exception as e:
        print(f'❌ Cannot read PDF: {e}')
        return False
    
    return True

def test_what_we_actually_have():
    """Test what we can actually do right now"""
    print(f'\n🧪 TESTING ACTUAL CURRENT CAPABILITIES')
    print('=' * 50)
    
    # Can we load the Gemma models directly?
    try:
        import onnxruntime as ort
        
        gemma_decoder = Path('C:/Learn/Code/fastembed/models/gemma-3n/onnx/decoder_model_merged_q4.onnx')
        if gemma_decoder.exists():
            print(f'📄 Found decoder model: {gemma_decoder.name}')
            
            # Try to load it
            try:
                print(f'🔄 Attempting to load ONNX model...')
                session = ort.InferenceSession(str(gemma_decoder))
                
                print(f'✅ Model loaded successfully!')
                
                # Check inputs/outputs
                inputs = session.get_inputs()
                outputs = session.get_outputs()
                
                print(f'📊 Model info:')
                print(f'   Inputs: {len(inputs)}')
                for inp in inputs:
                    print(f'     • {inp.name}: {inp.shape} ({inp.type})')
                
                print(f'   Outputs: {len(outputs)}')
                for out in outputs:
                    print(f'     • {out.name}: {out.shape} ({out.type})')
                
            except Exception as e:
                print(f'❌ Cannot load model: {e}')
        else:
            print(f'❌ Decoder model not found')
    
    except ImportError:
        print(f'❌ onnxruntime not available')
    except Exception as e:
        print(f'❌ Model testing error: {e}')

def main():
    """Actually test things instead of theorizing"""
    print('🎯 REAL TESTING - NO MORE ASSUMPTIONS!')
    print('Let\'s see what actually works\n')
    
    # Test what we have
    gateway_works = test_ai_gateway_endpoints()
    
    if gateway_works:
        test_gemma_model_files()
        attempt_real_pdf_test()
        test_what_we_actually_have()
    
    print(f'\n🎯 REAL CONCLUSIONS:')
    print(f'Based on actual testing (not assumptions):')
    print(f'1. What endpoints actually exist and work')
    print(f'2. What Gemma 3N files we actually have')
    print(f'3. Whether PDF processing is currently possible')
    print(f'4. What we need to implement next')

if __name__ == "__main__":
    main()