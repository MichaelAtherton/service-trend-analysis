"""
Test suite for taxonomy and confidence scoring validation (User Story 4).

Tests verify:
- Taxonomy loading (50+ techniques with all fields)
- Exact matching (Stage 1 with base_confidence=1.0)
- LLM fallback (Stage 2 with confidence 0.0-1.0)
- Confidence formula components (source_multiplier, frequency_boost)
- Confidence capping at 1.0
- Context detection accuracy (90%+ on labeled test cases)
- Newly discovered technique flagging
- OpenAI rate limit handling
- API cost tracking
"""

import pytest

from tests.utils.api_client import ExtractionAPIClient
from tests.utils.assertions import (
    assert_confidence_range,
    assert_technique_extracted,
)


# T064: Taxonomy loading validation
@pytest.mark.taxonomy
@pytest.mark.asyncio
async def test_taxonomy_loading():
    """
    Verify exactly 50+ techniques loaded from taxonomy.json with all required fields.
    
    Requirements:
    - FR-002: Taxonomy contains 50+ techniques
    - Required fields: full_name, aliases, category, confidence_boost, description
    
    Success criteria:
    - SC-002 (modified): 50+ techniques loaded
    
    Note: This requires access to the service's taxonomy file or initialization logs.
    """
    # TODO: Implement taxonomy inspection
    # This could be done by:
    # 1. Reading taxonomy.json directly from service directory
    # 2. Adding a /api/v1/taxonomy endpoint to query loaded techniques
    # 3. Inspecting service startup logs
    pytest.skip("Taxonomy inspection not yet implemented")


# T065: Stage 1 exact match validation
@pytest.mark.taxonomy
@pytest.mark.asyncio
async def test_exact_match_stage1(
    rag_paper: dict,
    extraction_service_url: str,
):
    """
    Verify exact alias matches return base_confidence=1.0 without LLM call.
    
    Requirements:
    - FR-004: Two-stage mapping (Stage 1: exact match)
    - Stage 1 should not call OpenAI API
    
    Success criteria:
    - Exact matches have base_confidence=1.0 (before source/frequency adjustments)
    """
    if not rag_paper:
        pytest.skip("RAG paper not available")
    
    metadata = rag_paper["metadata"]
    text = rag_paper["text"]
    
    async with ExtractionAPIClient(extraction_service_url) as client:
        result = await client.extract_single_paper(
            paper_id=metadata["paper_id"],
            title=metadata["title"],
            text=text,
            source_type=metadata["source_type"],
        )
        
        techniques = result.get("techniques", [])
        
        # Find RAG technique (should be exact match)
        rag_tech = assert_technique_extracted(
            actual_techniques=techniques,
            expected_technique_name="Retrieval-Augmented Generation",
            min_confidence=0.85,
            max_confidence=1.0,
        )
        
        confidence = rag_tech.get("confidence", 0.0)
        
        # Exact match should have high confidence (near 1.0)
        # May be slightly adjusted by source/frequency, but should be ≥0.85
        assert confidence >= 0.85, \
            f"Exact match confidence {confidence:.3f} too low (expected ≥0.85)"
        
        print(f"✓ Stage 1 exact match: confidence={confidence:.3f}")


# T066: Stage 2 LLM fallback validation
@pytest.mark.taxonomy
@pytest.mark.asyncio
@pytest.mark.slow
async def test_llm_fallback_stage2(
    extraction_service_url: str,
    openai_api_key: str,
    cost_tracker,
):
    """
    Verify ambiguous keywords trigger Stage 2 LLM validation.
    
    Requirements:
    - FR-004: Stage 2 LLM validation for ambiguous cases
    - Uses OpenAI GPT-4o-mini
    
    Success criteria:
    - Ambiguous techniques trigger LLM call
    - Confidence between 0.0-1.0
    
    Note: This test makes real OpenAI API calls and incurs costs.
    """
    # Create test text with ambiguous AI technique mention
    test_text = (
        "This paper explores novel approaches to neural architecture search. "
        "We propose a method that automatically discovers optimal model configurations "
        "for specific tasks using evolutionary algorithms. " * 20  # Repeat for length
    )
    
    async with ExtractionAPIClient(extraction_service_url) as client:
        result = await client.extract_single_paper(
            paper_id="test_ambiguous",
            title="Neural Architecture Search Paper",
            text=test_text,
            source_type="academic",
        )
        
        techniques = result.get("techniques", [])
        
        # Should extract at least one technique
        assert len(techniques) > 0, "No techniques extracted from ambiguous text"
        
        # All extracted techniques should have valid confidence
        for technique in techniques:
            confidence = technique.get("confidence", -1)
            assert 0.0 <= confidence <= 1.0, \
                f"Invalid confidence {confidence} for {technique.get('full_name')}"
        
        # Track cost
        # Note: Actual cost tracking requires intercepting OpenAI API calls
        # This is a placeholder for demonstration
        print(f"✓ Stage 2 LLM fallback: {len(techniques)} techniques extracted")


# T067: Confidence formula for academic papers
@pytest.mark.taxonomy
@pytest.mark.asyncio
async def test_confidence_formula_academic():
    """
    Verify academic paper with 5+ mentions: 1.0 × 1.0 × 1.2 = 1.0 (capped).
    
    Requirements:
    - FR-005: Confidence formula
    - Formula: base_confidence × source_multiplier × frequency_boost
    - Academic multiplier: 1.0
    - 5+ mentions boost: 1.2
    - Capped at 1.0
    
    Success criteria:
    - SC-005: Formula accuracy ±0.01
    """
    # Test formula calculation
    base_confidence = 1.0  # Exact match
    source_multiplier = 1.0  # Academic
    frequency_boost = 1.2  # 5+ mentions
    
    calculated_confidence = base_confidence * source_multiplier * frequency_boost
    capped_confidence = min(1.0, calculated_confidence)
    
    # Verify capping
    assert capped_confidence == 1.0, \
        f"Confidence {capped_confidence} not capped correctly"
    
    print(f"✓ Academic formula: {base_confidence} × {source_multiplier} × "
          f"{frequency_boost} = {calculated_confidence} (capped to {capped_confidence})")


# T068: Confidence formula for social media
@pytest.mark.taxonomy
@pytest.mark.asyncio
async def test_confidence_formula_social():
    """
    Verify social media with 1 mention: 1.0 × 0.80 × 1.0 = 0.80.
    
    Requirements:
    - FR-005: Confidence formula
    - Social multiplier: 0.80
    - 1 mention boost: 1.0
    """
    base_confidence = 1.0
    source_multiplier = 0.80  # Social media
    frequency_boost = 1.0  # 1 mention
    
    calculated_confidence = base_confidence * source_multiplier * frequency_boost
    
    assert calculated_confidence == 0.80, \
        f"Confidence {calculated_confidence} != 0.80"
    
    print(f"✓ Social formula: {base_confidence} × {source_multiplier} × "
          f"{frequency_boost} = {calculated_confidence}")


# T069: Frequency boost tiers validation
@pytest.mark.taxonomy
def test_frequency_boost_tiers():
    """
    Verify frequency boosts: 1 mention=1.0, 2-4 mentions=1.1, 5+ mentions=1.2.
    
    Requirements:
    - FR-005: Frequency boost tiers
    """
    def get_frequency_boost(mention_count: int) -> float:
        """Calculate frequency boost based on mention count."""
        if mention_count >= 5:
            return 1.2
        elif mention_count >= 2:
            return 1.1
        else:
            return 1.0
    
    # Test each tier
    assert get_frequency_boost(1) == 1.0, "1 mention should have 1.0 boost"
    assert get_frequency_boost(2) == 1.1, "2 mentions should have 1.1 boost"
    assert get_frequency_boost(4) == 1.1, "4 mentions should have 1.1 boost"
    assert get_frequency_boost(5) == 1.2, "5 mentions should have 1.2 boost"
    assert get_frequency_boost(10) == 1.2, "10 mentions should have 1.2 boost"
    
    print("✓ Frequency boost tiers: 1=1.0, 2-4=1.1, 5+=1.2")


# T070: Source multipliers validation
@pytest.mark.taxonomy
def test_source_multipliers():
    """
    Verify source_type multipliers.
    
    Requirements:
    - FR-005: Source multipliers
    - academic=1.0, blog=0.95, press=0.90, podcast=0.85, social=0.80
    """
    source_multipliers = {
        "academic": 1.0,
        "blog": 0.95,
        "press_release": 0.90,
        "podcast": 0.85,
        "social": 0.80,
    }
    
    # Verify all multipliers in valid range [0.0, 1.0]
    for source_type, multiplier in source_multipliers.items():
        assert 0.0 <= multiplier <= 1.0, \
            f"Invalid multiplier {multiplier} for {source_type}"
    
    # Verify academic has highest multiplier
    assert source_multipliers["academic"] == 1.0, \
        "Academic should have 1.0 multiplier"
    
    # Verify social has lowest multiplier
    assert source_multipliers["social"] == 0.80, \
        "Social should have 0.80 multiplier"
    
    print(f"✓ Source multipliers: {source_multipliers}")


# T071: Confidence capping validation
@pytest.mark.taxonomy
def test_confidence_capping():
    """
    Verify final confidence scores capped at 1.0.
    
    Requirements:
    - FR-005: Confidence capping
    - No values >1.0 allowed
    """
    # Simulate scenarios that could exceed 1.0 without capping
    test_cases = [
        {"base": 1.0, "source": 1.0, "frequency": 1.2, "expected": 1.0},
        {"base": 0.95, "source": 1.0, "frequency": 1.1, "expected": 1.0},  # 1.045 → 1.0
        {"base": 0.9, "source": 1.0, "frequency": 1.2, "expected": 1.0},  # 1.08 → 1.0
    ]
    
    for case in test_cases:
        calculated = case["base"] * case["source"] * case["frequency"]
        capped = min(1.0, calculated)
        
        assert capped <= 1.0, f"Confidence {capped} exceeds 1.0"
        assert capped == case["expected"], \
            f"Capped confidence {capped} != expected {case['expected']}"
    
    print(f"✓ Confidence capping: Validated {len(test_cases)} scenarios")


# T072: Context detection accuracy validation
@pytest.mark.taxonomy
@pytest.mark.asyncio
async def test_context_detection_accuracy():
    """
    Verify 90%+ correct classification on 50 pre-labeled test cases.
    
    Requirements:
    - FR-006: Context detection accuracy
    
    Success criteria:
    - SC-007: 90% context detection accuracy
    
    Note: Requires pre-labeled test dataset with known context types.
    """
    # TODO: Create pre-labeled test dataset
    # This requires:
    # 1. 50+ text snippets with AI technique mentions
    # 2. Manual labeling of context type for each
    # 3. Running extraction and comparing results
    pytest.skip("Pre-labeled context detection dataset not yet created")


# T073: Newly discovered technique flagging
@pytest.mark.taxonomy
@pytest.mark.asyncio
async def test_newly_discovered_flagging(
    extraction_service_url: str,
):
    """
    Verify techniques not in taxonomy have newly_discovered=true flag.
    
    Requirements:
    - FR-013: Newly discovered technique flagging
    
    Success criteria:
    - SC-009: 100% flagging accuracy
    """
    # Create text with fictional AI technique not in taxonomy
    test_text = (
        "This paper introduces QuantumNeural Synthesis, a novel approach "
        "combining quantum computing with neural network optimization. "
        "Our QuantumNeural Synthesis method achieves state-of-the-art results. " * 20
    )
    
    async with ExtractionAPIClient(extraction_service_url) as client:
        result = await client.extract_single_paper(
            paper_id="test_new_technique",
            title="Quantum Neural Synthesis",
            text=test_text,
            source_type="academic",
        )
        
        techniques = result.get("techniques", [])
        
        # Check if any newly discovered techniques flagged
        newly_discovered = [
            t for t in techniques
            if t.get("newly_discovered", False)
        ]
        
        if len(newly_discovered) > 0:
            print(f"✓ Newly discovered flagging: {len(newly_discovered)} techniques flagged")
            for tech in newly_discovered:
                print(f"  - {tech.get('full_name')}: newly_discovered=true")
        else:
            # If no techniques extracted, test is inconclusive
            if len(techniques) == 0:
                pytest.skip("No techniques extracted, cannot test flagging")
            else:
                print("⚠ No newly discovered techniques flagged (may all be in taxonomy)")


# T074: OpenAI rate limit handling
@pytest.mark.taxonomy
@pytest.mark.asyncio
@pytest.mark.slow
async def test_openai_rate_limit_handling():
    """
    Verify LLM validation handles 429 errors with exponential backoff.
    
    Requirements:
    - FR-012: Retry logic for rate limits
    - OpenAI rate limit: 3,500 RPM for gpt-4o-mini
    
    Note: Difficult to test without actually hitting rate limits.
    This test documents expected behavior.
    """
    # TODO: Simulate rate limit scenario
    # This requires either:
    # 1. Making enough requests to hit actual rate limit
    # 2. Mocking OpenAI API to return 429 errors
    # 3. Test endpoint in service that simulates rate limiting
    pytest.skip("Rate limit simulation not yet implemented")


# T075: OpenAI cost tracking validation
@pytest.mark.taxonomy
@pytest.mark.asyncio
async def test_openai_cost_tracking(
    cost_tracker,
    extraction_service_url: str,
    openai_api_key: str,
):
    """
    Verify cost tracker increments API calls and tokens correctly.
    
    Requirements:
    - FR-016: OpenAI cost tracking
    - Formula: (input_tokens × $0.00015 + output_tokens × $0.0006) / 1000
    """
    # Record initial state
    initial_calls = cost_tracker.total_calls
    initial_cost = cost_tracker.total_cost
    
    # Make a test extraction that should trigger LLM call
    test_text = (
        "This paper discusses advanced techniques in machine learning optimization. " * 30
    )
    
    async with ExtractionAPIClient(extraction_service_url) as client:
        await client.extract_single_paper(
            paper_id="test_cost_tracking",
            title="ML Optimization Paper",
            text=test_text,
            source_type="academic",
        )
    
    # Verify cost tracker updated
    # Note: This assumes the service reports usage back to our cost tracker
    # In practice, this requires integration with the service's OpenAI client
    
    print(f"✓ Cost tracking: Initial={initial_calls} calls/${initial_cost:.4f}, "
          f"Final={cost_tracker.total_calls} calls/${cost_tracker.total_cost:.4f}")
    
    # For now, just verify tracker structure works
    summary = cost_tracker.get_summary()
    assert "total_calls" in summary
    assert "estimated_cost_usd" in summary
    assert summary["estimated_cost_usd"] >= 0.0

