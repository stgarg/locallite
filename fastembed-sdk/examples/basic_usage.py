#!/usr/bin/env python3
"""
FastEmbed SDK - Basic Usage Examples
Demonstrates core functionality and OpenAI compatibility
"""

import fastembed
import numpy as np
import time
from typing import List


def basic_embedding_example():
    """Basic embedding example - single text"""
    print("🚀 Basic Embedding Example")
    print("=" * 40)
    
    # Initialize client
    client = fastembed.FastEmbedClient()
    
    # Check server health
    try:
        health = client.health()
        print(f"✅ Server connected - NPU available: {health.npu_available}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Single text embedding
    text = "FastEmbed provides NPU-accelerated embeddings"
    
    start_time = time.time()
    response = client.embeddings.create(input=text)
    latency = (time.time() - start_time) * 1000
    
    embedding = response.data[0].embedding
    
    print(f"📝 Input: {text}")
    print(f"📊 Embedding shape: {len(embedding)} dimensions")
    print(f"⚡ Latency: {latency:.1f}ms")
    print(f"🔢 First 5 values: {embedding[:5]}")
    print(f"💰 Cost: $0.00 (vs OpenAI: ~$0.02)")
    
    client.close()


def batch_embedding_example():
    """Batch embedding with automatic NPU optimization"""
    print("\n🎯 Batch Embedding Example")
    print("=" * 40)
    
    client = fastembed.FastEmbedClient()
    
    # Different batch sizes to show NPU optimization
    test_cases = [
        ("Single text (NPU optimal)", ["Hello world"]),
        ("Small batch (NPU good)", ["Hello", "World", "FastEmbed"]),
        ("Medium batch (Auto CPU)", ["Text " + str(i) for i in range(8)]),
        ("Large batch (CPU optimal)", ["Document " + str(i) for i in range(20)]),
    ]
    
    for test_name, texts in test_cases:
        start_time = time.time()
        response = client.embeddings.create(input=texts)
        latency = (time.time() - start_time) * 1000
        
        print(f"📋 {test_name}:")
        print(f"   Texts: {len(texts)}, Latency: {latency:.1f}ms")
        print(f"   Embeddings: {len(response.data)} x {len(response.data[0].embedding)}")
        print(f"   Tokens/sec: ~{len(texts) * 10 / (latency / 1000):.0f}")
        print()
    
    client.close()


def openai_compatibility_example():
    """Demonstrate OpenAI API compatibility"""
    print("🔄 OpenAI Compatibility Example")
    print("=" * 40)
    
    # This is the EXACT same API as OpenAI!
    client = fastembed.FastEmbedClient()
    
    # OpenAI-style call
    response = client.embeddings.create(
        input="This is a test document for embeddings",
        model="bge-small-en-v1.5",  # High-quality model
        encoding_format="float",    # Standard format
    )
    
    print("✅ OpenAI-compatible response structure:")
    print(f"   Object: {response.object}")
    print(f"   Model: {response.model}")
    print(f"   Data length: {len(response.data)}")
    print(f"   Usage: {response.usage.total_tokens} tokens")
    print(f"   Embedding dimensions: {len(response.data[0].embedding)}")
    
    # Access data exactly like OpenAI
    embedding_vector = response.data[0].embedding
    token_usage = response.usage.total_tokens
    
    print(f"📊 First embedding value: {embedding_vector[0]:.6f}")
    print(f"💳 Token usage: {token_usage}")
    
    client.close()


def similarity_search_example():
    """Semantic similarity search example"""
    print("🔍 Similarity Search Example")
    print("=" * 40)
    
    client = fastembed.FastEmbedClient()
    
    # Sample documents
    documents = [
        "FastEmbed provides high-performance embeddings with NPU acceleration",
        "OpenAI offers cloud-based embedding APIs with good quality",
        "Local inference ensures complete data privacy and security", 
        "Cost savings of 90% compared to cloud embedding services",
        "Snapdragon processors include specialized NPU hardware",
        "Python is a popular programming language for AI development",
    ]
    
    # Search query
    query = "NPU hardware acceleration benefits"
    
    print(f"🔍 Query: {query}")
    print(f"📚 Searching {len(documents)} documents...")
    
    # Embed all texts at once for efficiency
    all_texts = [query] + documents
    response = client.embeddings.create(input=all_texts)
    
    query_embedding = response.data[0].embedding
    doc_embeddings = [item.embedding for item in response.data[1:]]
    
    # Calculate cosine similarities
    similarities = []
    for i, doc_embedding in enumerate(doc_embeddings):
        # Cosine similarity
        dot_product = np.dot(query_embedding, doc_embedding)
        norm_query = np.linalg.norm(query_embedding)
        norm_doc = np.linalg.norm(doc_embedding)
        similarity = dot_product / (norm_query * norm_doc)
        
        similarities.append((similarity, documents[i]))
    
    # Sort by similarity
    similarities.sort(reverse=True)
    
    print("\n🎯 Top Results:")
    for i, (score, doc) in enumerate(similarities[:3]):
        print(f"{i+1}. Score: {score:.3f}")
        print(f"   {doc}")
        print()
    
    client.close()


def error_handling_example():
    """Demonstrate proper error handling"""
    print("🛡️ Error Handling Example")
    print("=" * 40)
    
    from fastembed import (
        FastEmbedConnectionError,
        FastEmbedTimeoutError,
        FastEmbedError,
    )
    
    # Test with potentially problematic scenarios
    try:
        # Normal case
        client = fastembed.FastEmbedClient()
        response = client.embeddings.create(input="Valid input")
        print("✅ Normal case succeeded")
        
        # Test with empty input (should fail validation)
        try:
            response = client.embeddings.create(input=[])
            print("❌ Empty input should have failed!")
        except FastEmbedError as e:
            print(f"✅ Validation error caught: {e}")
        
        # Test with invalid input type
        try:
            response = client.embeddings.create(input=123)
            print("❌ Invalid input type should have failed!")
        except FastEmbedError as e:
            print(f"✅ Validation error caught: {e}")
        
        client.close()
        
    except FastEmbedConnectionError:
        print("❌ Could not connect to FastEmbed server")
        print("💡 Make sure the server is running on http://127.0.0.1:8000")
    except FastEmbedTimeoutError:
        print("❌ Request timed out")
        print("💡 Try increasing timeout or check server performance")
    except FastEmbedError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def performance_monitoring_example():
    """Monitor system performance and health"""
    print("📊 Performance Monitoring Example")
    print("=" * 40)
    
    client = fastembed.FastEmbedClient()
    
    try:
        # Get initial health status
        health = client.health()
        
        print("🏥 System Health:")
        print(f"   Status: {health.status}")
        print(f"   NPU Available: {health.npu_available}")
        
        if hasattr(health, 'memory_usage'):
            mem = health.memory_usage
            print(f"   Memory: {mem.get('used_gb', 0):.1f}GB / {mem.get('total_gb', 0):.1f}GB")
        
        if hasattr(health, 'performance_stats'):
            stats = health.performance_stats
            print(f"   Total Requests: {stats.get('total_requests', 0)}")
            print(f"   NPU Requests: {stats.get('npu_requests', 0)}")
            print(f"   CPU Requests: {stats.get('cpu_requests', 0)}")
        
        # Perform some operations
        print("\n🧪 Running test operations...")
        for i in range(3):
            response = client.embeddings.create(input=f"Test embedding {i}")
            print(f"   Operation {i+1}: ✅ {len(response.data[0].embedding)} dims")
        
        # Check health again
        health_after = client.health()
        if hasattr(health_after, 'performance_stats'):
            new_stats = health_after.performance_stats
            new_total = new_stats.get('total_requests', 0)
            old_total = health.performance_stats.get('total_requests', 0)
            print(f"\n📈 New requests processed: {new_total - old_total}")
        
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
    finally:
        client.close()


def main():
    """Run all examples"""
    print("🎯 FastEmbed SDK Examples")
    print("=" * 60)
    
    try:
        basic_embedding_example()
        batch_embedding_example()
        openai_compatibility_example()
        similarity_search_example()
        error_handling_example()
        performance_monitoring_example()
        
        print("\n" + "=" * 60)
        print("🎉 All examples completed successfully!")
        print("💡 Next steps:")
        print("   • Run benchmarks: fastembed-benchmark --quick")
        print("   • Try demos: fastembed-demo similarity")
        print("   • Check documentation: https://fastembed.dev/docs")
        
    except KeyboardInterrupt:
        print("\n❌ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")


if __name__ == "__main__":
    main()