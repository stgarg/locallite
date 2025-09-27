#!/usr/bin/env python3
"""
FastEmbed Azure OpenAI Integration Demo

This demo shows how to:
1. Use FastEmbed for local NPU-accelerated embeddings
2. Benchmark against Azure OpenAI embeddings
3. Compare performance, cost, and privacy

Prerequisites:
- Copy .env.example to .env
- Fill in your Azure OpenAI credentials
- Ensure FastEmbed server is running (http://127.0.0.1:8000)
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
import fastembed
from secure_benchmark import SecureBenchmarkRunner

def main():
    print("🚀 FastEmbed vs Azure OpenAI Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Sample documents for testing
    documents = [
        "FastEmbed provides high-performance embeddings with NPU acceleration for cost-effective AI.",
        "Azure OpenAI offers cloud-based embedding services with enterprise-grade security.",
        "Local embedding generation reduces costs and improves data privacy for sensitive applications.",
        "Machine learning models can be optimized for different hardware architectures.",
        "Neural Processing Units (NPUs) excel at inference workloads for transformer models."
    ]
    
    print(f"📄 Testing with {len(documents)} sample documents")
    print()
    
    # 1. Test FastEmbed directly
    print("⚡ Testing FastEmbed (Local NPU):")
    try:
        client = fastembed.FastEmbedClient()
        embeddings = client.embeddings.create(input=documents[:2])  # Test with 2 documents
        print(f"   ✅ Generated {len(embeddings.data)} embeddings")
        print(f"   📏 Dimension: {len(embeddings.data[0].embedding)}")
        print(f"   🏷️  Model: {embeddings.model}")
        print()
    except Exception as e:
        print(f"   ❌ FastEmbed error: {e}")
        print(f"   💡 Make sure FastEmbed server is running on http://127.0.0.1:8000")
        print()
    
    # 2. Run comprehensive benchmark
    print("🏁 Running Comprehensive Benchmark:")
    print("-" * 40)
    
    benchmark = SecureBenchmarkRunner(iterations=3)  # Quick demo
    results = benchmark.run_comprehensive_benchmark()
    
    # 3. Show key insights
    print("\n💡 Key Insights:")
    print("-" * 20)
    
    # Analyze results
    if "results" in results:
        fastembed_results = [r for r in results["results"] if "FastEmbed" in r.get("provider", "")]
        azure_results = [r for r in results["results"] if "Azure" in r.get("provider", "")]
        
        if fastembed_results and azure_results:
            fe_latency = fastembed_results[0]["avg_latency_ms"]
            az_latency = azure_results[0]["avg_latency_ms"]
            fe_dim = 384  # BGE-small-en-v1.5
            az_dim = 1536  # text-embedding-3-small
            
            print(f"⚡ Latency: FastEmbed {fe_latency}ms vs Azure {az_latency}ms")
            print(f"📏 Dimensions: FastEmbed {fe_dim}D vs Azure {az_dim}D")
            print(f"🎯 Model: FastEmbed (BGE-small-en-v1.5) vs Azure (text-embedding-3-small)")
            print(f"💰 Cost: FastEmbed FREE vs Azure ${azure_results[0]['cost_per_1k_tokens']}/1k tokens")
            print(f"🔒 Privacy: FastEmbed (local) vs Azure (cloud)")
            print()
            print(f"⚠️  **Note**: Different model capabilities - Azure model is larger/higher quality")
            
            if fe_latency < az_latency:
                speedup = az_latency / fe_latency
                print(f"🚀 FastEmbed is {speedup:.1f}x faster (but different model architecture)")
        
        elif fastembed_results:
            print(f"⚡ FastEmbed latency: {fastembed_results[0]['avg_latency_ms']}ms")
            print(f"💰 FastEmbed cost: FREE (no API calls)")
            print(f"🔒 FastEmbed privacy: 100% local processing")
            print(f"📊 Configure Azure OpenAI credentials to see comparison")
        
        else:
            print("📊 No benchmark results available")
    
    print(f"\n🎯 Use Case Recommendations:")
    print(f"• 🏠 High-volume/cost-sensitive → FastEmbed (good quality, fast, free)")
    print(f"• ☁️  Maximum quality needed → Azure OpenAI (premium model)")
    print(f"• 💰 Budget constraints → FastEmbed")
    print(f"• 🔒 Data privacy critical → FastEmbed (local processing)")
    print(f"• 📊 Proof-of-concept/prototyping → FastEmbed (quick setup)")
    print(f"• 🏢 Enterprise/production → Consider both based on quality needs")
    
    print(f"\n✅ Demo complete!")
    print(f"💡 To test Azure OpenAI: Configure credentials in .env file")

if __name__ == "__main__":
    main()