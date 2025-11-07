"""
Diagnostic tests to understand current state and what's needed
"""
import asyncio
import httpx
import json

async def test_embedding_server():
    """Test embedding server directly"""
    print("\n" + "="*60)
    print("TEST 1: Embedding Server")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Health check
        print("\n1.1 Health Check:")
        response = await client.get("http://localhost:8765/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test embedding
        print("\n1.2 Test Embedding:")
        test_texts = [
            "Reinforcement learning from human feedback improves model alignment",
            "Transformer architecture uses self-attention mechanisms"
        ]
        response = await client.post(
            "http://localhost:8765/embed",
            json={"texts": test_texts, "normalize": True}
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Model: {result.get('model')}")
        print(f"   Dimension: {result.get('dimension')}")
        print(f"   Embeddings shape: {len(result['embeddings'])} texts × {len(result['embeddings'][0])} dims")
        print(f"   Sample embedding (first 5 values): {result['embeddings'][0][:5]}")

async def test_extraction_service():
    """Test extraction service with minimal paper"""
    print("\n" + "="*60)
    print("TEST 2: Extraction Service")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Health check
        print("\n2.1 Health Check:")
        response = await client.get("http://localhost:8000/api/v1/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test extraction with minimal paper
        print("\n2.2 Test Extraction (minimal paper):")
        test_paper = {
            "paper_id": "test_001",
            "title": "Test Paper on RLHF",
            "text": """
            Reinforcement Learning from Human Feedback (RLHF) is a technique for training language models.
            The approach combines reward modeling with proximal policy optimization.
            RLHF enables better alignment with human preferences.
            This method has been used in ChatGPT and other modern AI systems.
            The technique involves fine-tuning using human feedback signals.
            """,
            "source_type": "academic"
        }
        
        response = await client.post(
            "http://localhost:8000/api/v1/extract/techniques",
            json=[test_paper],
            timeout=60.0
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            enriched = result[0]
            print(f"   Paper ID: {enriched.get('paper_id')}")
            print(f"   Techniques Found: {enriched.get('total_techniques_found')}")
            print(f"   Expected Accuracy: {enriched.get('expected_accuracy')}")
            print(f"   Processing Time: {enriched.get('processing_duration_ms')}ms")
            print(f"   Techniques: {json.dumps(enriched.get('techniques', []), indent=6)}")
        else:
            print(f"   Unexpected response: {result}")

async def test_internal_components():
    """Test internal components directly"""
    print("\n" + "="*60)
    print("TEST 3: Internal Components")
    print("="*60)
    
    import sys
    sys.path.insert(0, 'services/technique-extraction/src')
    
    # Test taxonomy loading
    print("\n3.1 Taxonomy Loading:")
    from services.technique_mapper import TechniqueMapper
    mapper = TechniqueMapper()
    print(f"   Taxonomy loaded: {len(mapper.taxonomy)} techniques")
    print(f"   Sample techniques: {list(mapper.taxonomy.keys())[:5]}")
    
    # Test preprocessing
    print("\n3.2 Text Preprocessing:")
    from preprocessing.academic import clean_academic
    test_text = "   This is a test\\n\\nwith LaTeX $\\alpha$ and multiple    spaces.   "
    cleaned = clean_academic(test_text)
    print(f"   Original length: {len(test_text)}")
    print(f"   Cleaned length: {len(cleaned)}")
    print(f"   Cleaned text: '{cleaned[:100]}...'")
    
    # Test BERTrend service
    print("\n3.3 BERTrend Service:")
    from services.embedding_client import EmbeddingClient
    from services.bertrend_service import BERTrendService
    
    async with EmbeddingClient() as client:
        bertrend = BERTrendService(client)
        test_paragraphs = [
            "RLHF is used for alignment",
            "Transformers use attention",
            "GPT models are pretrained"
        ]
        topics = await bertrend.cluster_topics(test_paragraphs)
        print(f"   Topics returned: {len(topics)}")
        print(f"   Topics: {topics}")

async def main():
    """Run all diagnostics"""
    print("\n" + "="*60)
    print("DIAGNOSTIC TEST SUITE")
    print("="*60)
    print("Purpose: Identify what's implemented vs. what needs work")
    print()
    
    try:
        await test_embedding_server()
    except Exception as e:
        print(f"\n   ❌ ERROR: {e}")
    
    try:
        await test_extraction_service()
    except Exception as e:
        print(f"\n   ❌ ERROR: {e}")
    
    try:
        await test_internal_components()
    except Exception as e:
        print(f"\n   ❌ ERROR: {e}")
    
    print("\n" + "="*60)
    print("DIAGNOSTICS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
