#!/usr/bin/env python3
"""
Model Comparison Guide

This guide helps you understand the trade-offs between different embedding models
and choose the right one for your use case.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_model_comparison():
    print("🤖 Embedding Model Comparison Guide")
    print("=" * 50)
    
    print("\n📊 **FastEmbed (BGE-small-en-v1.5)**")
    print("   • Dimensions: 384")
    print("   • Quality: Good (suitable for most applications)")
    print("   • Speed: Very Fast (local NPU acceleration)")
    print("   • Cost: FREE")
    print("   • Privacy: 100% local processing")
    print("   • Best for: High-volume, cost-sensitive, privacy-critical")
    
    print("\n☁️  **Azure OpenAI (text-embedding-3-small)**")
    print("   • Dimensions: 1536") 
    print("   • Quality: Premium (state-of-the-art)")
    print("   • Speed: Moderate (network latency + processing)")
    print("   • Cost: $0.02 per 1K tokens")
    print("   • Privacy: Cloud-based (Azure tenant)")
    print("   • Best for: Maximum quality, low-volume, enterprise")
    
    print("\n🎯 **Choosing the Right Model:**")
    print()
    print("**Use FastEmbed when:**")
    print("   ✅ Processing large volumes of text")
    print("   ✅ Cost is a primary concern")
    print("   ✅ Data privacy is critical")
    print("   ✅ Good quality is sufficient")
    print("   ✅ Low latency is required")
    print("   ✅ Prototyping/proof-of-concept")
    
    print("\n**Use Azure OpenAI when:**")
    print("   ✅ Maximum embedding quality needed")
    print("   ✅ Processing low volumes")
    print("   ✅ Budget allows for premium service")
    print("   ✅ Cloud deployment is acceptable")
    print("   ✅ Enterprise support is required")
    
    print("\n💡 **Quality vs Cost Trade-offs:**")
    print("   • FastEmbed: ~80-90% of premium quality at 0% cost")
    print("   • Azure OpenAI: 100% quality at premium cost")
    print("   • For many applications, FastEmbed's quality is sufficient")
    print("   • Consider hybrid: FastEmbed for bulk processing, Azure for critical queries")
    
    print("\n🧪 **Testing Recommendations:**")
    print("   1. Start with FastEmbed for development/testing")
    print("   2. Evaluate quality with your specific data")
    print("   3. Compare results side-by-side")
    print("   4. Consider cost at production scale")
    print("   5. Choose based on quality requirements vs budget")

def print_performance_estimates():
    print("\n📈 **Performance Estimates (1M documents):**")
    print()
    print("FastEmbed:")
    print("   • Processing time: ~30 minutes")
    print("   • Cost: $0 (hardware already owned)")
    print("   • Quality: Good")
    
    print("\nAzure OpenAI:")
    print("   • Processing time: ~3-4 hours (network + rate limits)")
    print("   • Cost: ~$200-400 (depending on token count)")
    print("   • Quality: Premium")
    
    print("\n💰 **Break-even Analysis:**")
    print("   • FastEmbed pays for itself after ~10-20M tokens")
    print("   • Higher volume = bigger FastEmbed advantage")
    print("   • Consider hardware costs vs API costs")

if __name__ == "__main__":
    print_model_comparison()
    print_performance_estimates()
    
    print("\n✅ Run azure_demo.py to see live comparison!")