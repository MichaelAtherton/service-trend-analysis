"""
Detailed diagnostic tests to understand extraction logic
"""
import asyncio
import httpx
import json

async def test_extraction_with_various_papers():
    """Test with papers mentioning different techniques"""
    print("\n" + "="*60)
    print("DETAILED EXTRACTION DIAGNOSTICS")
    print("="*60)
    
    test_cases = [
        {
            "paper_id": "test_rlhf",
            "title": "RLHF Paper",
            "text": "Reinforcement Learning from Human Feedback (RLHF) and reward modeling are used. Proximal Policy Optimization (PPO) is the algorithm.",
            "expected": ["RLHF", "Reward Modeling", "PPO"]
        },
        {
            "paper_id": "test_transformers",
            "title": "Transformer Paper",
            "text": "Transformers use self-attention mechanisms. BERT and GPT are transformer models. The attention mechanism is key.",
            "expected": ["Transformer", "BERT", "GPT", "Attention Mechanism"]
        },
        {
            "paper_id": "test_finetuning",
            "title": "Fine-tuning Paper",
            "text": "Fine-tuning with LoRA (Low-Rank Adaptation) enables efficient training. Instruction tuning improves the model.",
            "expected": ["Fine-tuning", "LoRA", "Instruction Tuning"]
        },
        {
            "paper_id": "test_explicit_mentions",
            "title": "Explicit Mentions",
            "text": """
            This paper discusses several AI techniques:
            1. Reinforcement Learning from Human Feedback
            2. Reward Modeling
            3. Proximal Policy Optimization
            4. Transformer architecture
            5. BERT language model
            6. Fine-Tuning
            7. Instruction Tuning
            """,
            "expected": ["Multiple techniques"]
        }
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'-'*60}")
            print(f"Test Case {i}: {test_case['title']}")
            print(f"{'-'*60}")
            print(f"Expected to find: {', '.join(test_case['expected'])}")
            print(f"Text length: {len(test_case['text'])} chars")
            
            paper = {
                "paper_id": test_case["paper_id"],
                "title": test_case["title"],
                "text": test_case["text"],
                "source_type": "academic"
            }
            
            try:
                response = await client.post(
                    "http://localhost:8000/api/v1/extract/techniques",
                    json=[paper],
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        enriched = result[0]
                        techniques = enriched.get('techniques', [])
                        
                        print(f"\n✓ Status: {response.status_code}")
                        print(f"✓ Techniques Found: {len(techniques)}")
                        print(f"✓ Processing Time: {enriched.get('processing_duration_ms')}ms")
                        
                        if techniques:
                            print(f"\nFound Techniques:")
                            for t in techniques:
                                print(f"  • {t['technique_name']} (confidence: {t['confidence']:.3f}, context: {t['context_type']})")
                                if t.get('text_snippets'):
                                    print(f"    Snippet: \"{t['text_snippets'][0]['snippet'][:60]}...\"")
                        else:
                            print("\n⚠️  No techniques found")
                    else:
                        print(f"✗ Unexpected response format")
                else:
                    print(f"✗ Status: {response.status_code}")
                    print(f"  Error: {response.text}")
                    
            except Exception as e:
                print(f"✗ Error: {e}")

async def test_taxonomy_coverage():
    """Check what's in the taxonomy"""
    print("\n" + "="*60)
    print("TAXONOMY ANALYSIS")
    print("="*60)
    
    import sys
    sys.path.insert(0, 'services/technique-extraction/src')
    
    try:
        import json
        with open('services/technique-extraction/src/data/taxonomy.json', 'r') as f:
            taxonomy = json.load(f)
        
        print(f"\n✓ Taxonomy loaded: {len(taxonomy.get('techniques', []))} techniques")
        
        # Show sample techniques
        print(f"\nSample Techniques (first 10):")
        for i, tech in enumerate(taxonomy.get('techniques', [])[:10], 1):
            print(f"  {i}. {tech['full_name']}")
            if tech.get('aliases'):
                print(f"     Aliases: {', '.join(tech['aliases'][:3])}")
        
        # Check for expected techniques
        print(f"\nSearching for expected techniques:")
        expected = [
            "Reinforcement Learning from Human Feedback",
            "Reward Modeling",
            "Proximal Policy Optimization",
            "Transformer",
            "BERT",
            "Fine-Tuning"
        ]
        
        tech_names = [t['full_name'].lower() for t in taxonomy.get('techniques', [])]
        for exp in expected:
            found = any(exp.lower() in name for name in tech_names)
            status = "✓" if found else "✗"
            print(f"  {status} {exp}")
            
    except Exception as e:
        print(f"✗ Error loading taxonomy: {e}")

async def main():
    """Run all detailed diagnostics"""
    await test_extraction_with_various_papers()
    await test_taxonomy_coverage()
    
    print("\n" + "="*60)
    print("DETAILED DIAGNOSTICS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
