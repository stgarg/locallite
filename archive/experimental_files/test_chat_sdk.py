#!/usr/bin/env python3
"""
Test script for the new FastEmbed SDK Chat API
"""
import sys
import os

# Add the SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fastembed-sdk', 'src'))

from fastembed import FastEmbedClient

def test_chat_api():
    """Test the new Chat API functionality"""
    print("🧪 Testing FastEmbed SDK Chat API...")
    
    # Initialize client
    client = FastEmbedClient(base_url="http://127.0.0.1:8000")
    
    # Test health first
    try:
        health = client.health()
        print(f"✅ Server health: {health.status}, NPU: {health.npu_available}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test chat completion
    try:
        print("\n💬 Testing chat completion...")
        response = client.chat.create(
            model="gemma-3n-4b",
            messages=[
                {"role": "user", "content": "Hello! Tell me about FastEmbed."}
            ]
        )
        
        print(f"✅ Chat Response ID: {response.id}")
        print(f"✅ Model: {response.model}")
        print(f"✅ Message: {response.choices[0].message.content}")
        print(f"✅ Usage: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chat API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        client.close()

if __name__ == "__main__":
    success = test_chat_api()
    print(f"\n🎯 SDK Chat API Test: {'PASSED' if success else 'FAILED'}")