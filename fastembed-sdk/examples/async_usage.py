#!/usr/bin/env python3
"""
FastEmbed SDK - Async Usage Examples
High-throughput applications with async/await patterns
"""

import asyncio
import time
import fastembed
from typing import List


async def basic_async_example():
    """Basic async embedding example"""
    print("🚀 Basic Async Example")
    print("=" * 40)
    
    async with fastembed.AsyncFastEmbedClient() as client:
        # Check health
        health = await client.health()
        print(f"✅ Server connected - NPU: {health.npu_available}")
        
        # Single async embedding
        start_time = time.time()
        response = await client.embeddings.create(input="Async FastEmbed is fast!")
        latency = (time.time() - start_time) * 1000
        
        print(f"📝 Embedding created in {latency:.1f}ms")
        print(f"📊 Dimensions: {len(response.data[0].embedding)}")


async def concurrent_embeddings_example():
    """Demonstrate concurrent embedding processing"""
    print("\n⚡ Concurrent Embeddings Example")
    print("=" * 40)
    
    async with fastembed.AsyncFastEmbedClient() as client:
        # Create multiple embedding tasks
        tasks = []
        for i in range(5):
            task = client.embeddings.create(input=f"Concurrent embedding task {i}")
            tasks.append(task)
        
        print(f"📋 Processing {len(tasks)} embeddings concurrently...")
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        total_time = (time.time() - start_time) * 1000
        
        print(f"✅ Completed {len(responses)} embeddings in {total_time:.1f}ms")
        print(f"⚡ Average per embedding: {total_time/len(responses):.1f}ms")
        print(f"🚀 Throughput: {len(responses) / (total_time/1000):.1f} embeddings/sec")


async def batch_processing_example():
    """Process large batches efficiently with async"""
    print("\n📦 Batch Processing Example")
    print("=" * 40)
    
    # Simulate a large dataset
    documents = [f"Document {i}: This is sample text for embedding" for i in range(100)]
    
    async with fastembed.AsyncFastEmbedClient() as client:
        # Process in optimal batch sizes
        batch_size = 10  # Good balance for throughput
        batches = [documents[i:i+batch_size] for i in range(0, len(documents), batch_size)]
        
        print(f"📚 Processing {len(documents)} documents in {len(batches)} batches...")
        
        start_time = time.time()
        
        # Process batches concurrently
        tasks = []
        for batch in batches:
            task = client.embeddings.create(input=batch)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        total_time = (time.time() - start_time) * 1000
        total_embeddings = sum(len(response.data) for response in responses)
        
        print(f"✅ Processed {total_embeddings} embeddings in {total_time:.1f}ms")
        print(f"⚡ Throughput: {total_embeddings / (total_time/1000):.1f} embeddings/sec")
        print(f"💰 Cost: $0.00 (vs cloud APIs: ~${total_embeddings * 0.02 / 1000:.2f})")


async def streaming_similarity_search():
    """Real-time similarity search with async processing"""
    print("\n🔍 Streaming Similarity Search")
    print("=" * 40)
    
    # Knowledge base
    knowledge_base = [
        "FastEmbed provides NPU acceleration for embeddings",
        "Local inference ensures complete data privacy",
        "Cost savings reach 90% compared to cloud APIs",
        "Automatic NPU/CPU selection optimizes performance",
        "OpenAI-compatible API enables easy migration",
        "Real-time processing with async capabilities",
        "Snapdragon hardware acceleration delivers speed",
        "Python SDK supports modern async/await patterns",
    ]
    
    async with fastembed.AsyncFastEmbedClient() as client:
        # Pre-compute knowledge base embeddings
        print("📚 Pre-computing knowledge base embeddings...")
        kb_response = await client.embeddings.create(input=knowledge_base)
        kb_embeddings = [item.embedding for item in kb_response.data]
        
        # Simulate real-time queries
        queries = [
            "NPU performance benefits",
            "privacy and security features", 
            "cost comparison with OpenAI",
            "async processing capabilities",
        ]
        
        print(f"\n🔍 Processing {len(queries)} real-time queries...")
        
        # Process queries concurrently
        query_tasks = [client.embeddings.create(input=query) for query in queries]
        query_responses = await asyncio.gather(*query_tasks)
        
        # Find best matches for each query
        import numpy as np
        
        for i, (query, query_response) in enumerate(zip(queries, query_responses)):
            query_embedding = query_response.data[0].embedding
            
            # Calculate similarities
            similarities = []
            for j, kb_embedding in enumerate(kb_embeddings):
                similarity = np.dot(query_embedding, kb_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(kb_embedding)
                )
                similarities.append((similarity, knowledge_base[j]))
            
            # Get best match
            best_match = max(similarities, key=lambda x: x[0])
            
            print(f"\n🎯 Query {i+1}: '{query}'")
            print(f"   Best match (score: {best_match[0]:.3f}): {best_match[1]}")


async def error_handling_async():
    """Async error handling patterns"""
    print("\n🛡️ Async Error Handling")
    print("=" * 40)
    
    from fastembed import (
        FastEmbedConnectionError,
        FastEmbedTimeoutError,
        FastEmbedValidationError,
    )
    
    try:
        async with fastembed.AsyncFastEmbedClient() as client:
            # Test various error conditions
            tasks = [
                client.embeddings.create(input="Valid input 1"),
                client.embeddings.create(input="Valid input 2"), 
                # This would cause validation error:
                # client.embeddings.create(input=[]),
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"❌ Task {i+1} failed: {response}")
                else:
                    print(f"✅ Task {i+1} succeeded: {len(response.data)} embeddings")
                    
    except FastEmbedConnectionError:
        print("❌ Connection failed - check server")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def performance_comparison():
    """Compare sync vs async performance"""
    print("\n🏁 Sync vs Async Performance Comparison")
    print("=" * 40)
    
    texts = [f"Performance test text {i}" for i in range(20)]
    
    # Sync version
    print("🐌 Testing synchronous processing...")
    sync_start = time.time()
    
    client = fastembed.FastEmbedClient()
    for text in texts:
        response = client.embeddings.create(input=text)
    client.close()
    
    sync_time = time.time() - sync_start
    
    # Async version
    print("⚡ Testing asynchronous processing...")
    async_start = time.time()
    
    async with fastembed.AsyncFastEmbedClient() as client:
        tasks = [client.embeddings.create(input=text) for text in texts]
        responses = await asyncio.gather(*tasks)
    
    async_time = time.time() - async_start
    
    # Results
    speedup = sync_time / async_time
    print(f"\n📊 Performance Results:")
    print(f"   Sync time: {sync_time*1000:.1f}ms")
    print(f"   Async time: {async_time*1000:.1f}ms")
    print(f"   Speedup: {speedup:.1f}x faster with async")
    print(f"   Throughput: {len(texts) / async_time:.1f} embeddings/sec")


async def main():
    """Run all async examples"""
    print("🎯 FastEmbed SDK Async Examples")
    print("=" * 60)
    
    try:
        await basic_async_example()
        await concurrent_embeddings_example()
        await batch_processing_example()
        await streaming_similarity_search()
        await error_handling_async()
        await performance_comparison()
        
        print("\n" + "=" * 60)
        print("🎉 All async examples completed successfully!")
        print("💡 Key takeaways:")
        print("   • Use async for high-throughput applications")
        print("   • Process batches concurrently for best performance") 
        print("   • NPU acceleration works with async patterns")
        print("   • Significant speedup vs synchronous processing")
        
    except KeyboardInterrupt:
        print("\n❌ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())