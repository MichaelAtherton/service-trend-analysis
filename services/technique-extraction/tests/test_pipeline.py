"""
Test suite for core extraction pipeline validation (User Story 1).

Tests verify:
- End-to-end extraction accuracy (85%+ technique identification)
- Processing time (<10s per paper)
- Preprocessing (LaTeX removal, content preservation)
- Exact technique matching (Stage 1)
- Context detection (production/research/tutorial/criticism/general)
- Text snippet extraction (50-char windows with offsets)
- Confidence score ranges (±0.05 tolerance for BERTrend variation)
- expected_accuracy field calculation
"""

import time
from typing import Any

import pytest

from tests.utils.api_client import ExtractionAPIClient
from tests.utils.assertions import (
    assert_confidence_range,
    assert_context_type,
    assert_extraction_accuracy,
    assert_technique_extracted,
)


# T028: Health check validation
@pytest.mark.pipeline
@pytest.mark.asyncio
async def test_health_check(extraction_service_url: str):
    """
    Verify service is running and health check endpoint responds correctly.
    
    Requirements:
    - FR-001: Health check <100ms response time
    - Railway deployment standard: /health endpoint available
    
    Success criteria:
    - SC-003: Health check responds <100ms
    """
    async with ExtractionAPIClient(extraction_service_url) as client:
        start_time = time.time()
        health_response = await client.health_check()
        duration_ms = (time.time() - start_time) * 1000
        
        # Verify response structure
        assert "status" in health_response, "Health response missing 'status' field"
        assert health_response["status"] in ["healthy", "unhealthy"], \
            f"Invalid status: {health_response['status']}"
        
        # Verify response time
        assert duration_ms < 100, \
            f"Health check took {duration_ms:.1f}ms (expected <100ms)"
        
        # Log response for debugging
        print(f"✓ Health check passed: {health_response} ({duration_ms:.1f}ms)")


# T029: Extraction accuracy validation
@pytest.mark.pipeline
@pytest.mark.asyncio
@pytest.mark.parametrize("paper_id", [
    "paper_001",  # RAG
    "paper_002",  # RLHF
    "paper_003",  # Fine-tuning
    "paper_004",  # Transformers
    "paper_005",  # Diffusion
    "paper_006",  # Multi-modal
    "paper_007",  # Quantization
    "paper_008",  # Prompt Engineering
    "paper_009",  # Evaluation
    "paper_010",  # AI Agents
])
async def test_extraction_accuracy(
    paper_id: str,
    sample_papers: dict[str, dict[str, Any]],
    extraction_service_url: str,
):
    """
    Verify extraction accuracy meets 85%+ threshold for each sample paper.
    
    Requirements:
    - FR-004: Two-stage technique mapping (exact + LLM)
    - FR-005: Confidence formula validation
    
    Success criteria:
    - SC-001: 85%+ technique identification rate
    """
    paper_data = sample_papers.get(paper_id)
    if not paper_data:
        pytest.skip(f"Paper {paper_id} not available")
    
    metadata = paper_data["metadata"]
    text = paper_data["text"]
    expected_techniques = metadata["expected_techniques"]
    
    async with ExtractionAPIClient(extraction_service_url) as client:
        result = await client.extract_single_paper(
            paper_id=paper_id,
            title=metadata["title"],
            text=text,
            source_type=metadata["source_type"],
        )
        
        actual_techniques = result.get("techniques", [])
        
        # Assert 85%+ accuracy using custom assertion
        stats = assert_extraction_accuracy(
            actual_techniques=actual_techniques,
            expected_techniques=expected_techniques,
            min_accuracy=0.85,
            tolerance=0.05,  # ±0.05 for BERTrend stochastic variation
        )
        
        # Log results
        print(f"✓ {paper_id}: {stats['accuracy']:.1%} accuracy "
              f"({stats['total_actual']}/{stats['total_expected']} techniques)")


# T030: Processing time validation
@pytest.mark.pipeline
@pytest.mark.asyncio
@pytest.mark.parametrize("paper_id", [
    "paper_001", "paper_002", "paper_003", "paper_004", "paper_005",
    "paper_006", "paper_007", "paper_008", "paper_009", "paper_010",
])
async def test_processing_time(
    paper_id: str,
    sample_papers: dict[str, dict[str, Any]],
    extraction_service_url: str,
):
    """
    Verify each paper processes in <10 seconds.
    
    Requirements:
    - FR-014: Duration tracking in milliseconds
    
    Success criteria:
    - SC-002: <10s per paper processing time
    """
    paper_data = sample_papers.get(paper_id)
    if not paper_data:
        pytest.skip(f"Paper {paper_id} not available")
    
    metadata = paper_data["metadata"]
    text = paper_data["text"]
    
    async with ExtractionAPIClient(extraction_service_url) as client:
        start_time = time.time()
        
        result = await client.extract_single_paper(
            paper_id=paper_id,
            title=metadata["title"],
            text=text,
            source_type=metadata["source_type"],
        )
        
        duration_seconds = time.time() - start_time
        
        # Assert <10 seconds
        assert duration_seconds < 10.0, \
            f"Processing took {duration_seconds:.2f}s (expected <10s)"
        
        # Verify duration_ms field if present in response
        if "processing_duration_ms" in result:
            reported_duration = result["processing_duration_ms"] / 1000
            print(f"✓ {paper_id}: {reported_duration:.2f}s "
                  f"(actual: {duration_seconds:.2f}s)")
        else:
            print(f"✓ {paper_id}: {duration_seconds:.2f}s")


# T031: LaTeX preprocessing validation
@pytest.mark.pipeline
@pytest.mark.asyncio
async def test_preprocessing_latex(
    sample_papers: dict[str, dict[str, Any]],
    extraction_service_url: str,
):
    """
    Verify LaTeX removal while preserving technical content.
    
    Requirements:
    - FR-003: Academic paper preprocessing (LaTeX, equations, citations)
    
    Validation approach:
    - Submit paper with LaTeX formatting
    - Verify techniques are still extracted correctly
    - LaTeX commands should not appear in snippet extractions
    """
    # Find a paper with LaTeX
    latex_paper = None
    for paper_data in sample_papers.values():
        if paper_data["metadata"].get("contains_latex"):
            latex_paper = paper_data
            break
    
    if not latex_paper:
        pytest.skip("No papers with LaTeX available")
    
    metadata = latex_paper["metadata"]
    text = latex_paper["text"]
    
    async with ExtractionAPIClient(extraction_service_url) as client:
        result = await client.extract_single_paper(
            paper_id=metadata["paper_id"],
            title=metadata["title"],
            text=text,
            source_type=metadata["source_type"],
        )
        
        techniques = result.get("techniques", [])
        
        # Verify techniques were extracted despite LaTeX
        assert len(techniques) > 0, "No techniques extracted from LaTeX paper"
        
        # Check snippets don't contain common LaTeX commands
        latex_commands = ["\\begin", "\\end", "\\cite", "\\ref", "\\label"]
        for technique in techniques:
            for snippet in technique.get("text_snippets", []):
                snippet_text = snippet.get("text", "")
                for cmd in latex_commands:
                    assert cmd not in snippet_text, \
                        f"LaTeX command '{cmd}' found in snippet: {snippet_text}"
        
        print(f"✓ LaTeX preprocessing validated: {len(techniques)} techniques extracted")


# T032: Exact technique matching validation
@pytest.mark.pipeline
@pytest.mark.asyncio
async def test_exact_technique_matching(
    rag_paper: dict[str, Any],
    extraction_service_url: str,
):
    """
    Verify Stage 1 exact matching returns base_confidence=1.0.
    
    Requirements:
    - FR-004: Two-stage mapping (exact match first)
    - FR-005: Confidence formula (exact match = 1.0 base)
    
    Validation:
    - Submit paper with well-known technique (RAG)
    - Verify confidence near 1.0 (accounting for source/frequency adjustments)
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
        
        # Find RAG technique
        rag_technique = assert_technique_extracted(
            actual_techniques=techniques,
            expected_technique_name="Retrieval-Augmented Generation",
            min_confidence=0.85,  # May be adjusted by source/frequency
            max_confidence=1.0,
        )
        
        # Exact matches should have high confidence
        confidence = rag_technique.get("confidence", 0.0)
        print(f"✓ RAG exact match confidence: {confidence:.3f}")


# T033: Context detection validation
@pytest.mark.pipeline
@pytest.mark.asyncio
async def test_context_detection(
    sample_papers: dict[str, dict[str, Any]],
    extraction_service_url: str,
):
    """
    Verify production/research/tutorial/criticism/general classification.
    
    Requirements:
    - FR-006: Context detection (keyword-based classification)
    
    Success criteria:
    - SC-007: 90% context detection accuracy
    """
    test_count = 0
    correct_count = 0
    
    for paper_id, paper_data in sample_papers.items():
        metadata = paper_data["metadata"]
        text = paper_data["text"]
        expected_techniques = metadata["expected_techniques"]
        
        async with ExtractionAPIClient(extraction_service_url) as client:
            result = await client.extract_single_paper(
                paper_id=paper_id,
                title=metadata["title"],
                text=text,
                source_type=metadata["source_type"],
            )
            
            actual_techniques = result.get("techniques", [])
            
            # Compare context types for each expected technique
            for expected in expected_techniques:
                expected_name = expected["full_name"]
                expected_context = expected.get("expected_context_type", "general")
                
                matching = [t for t in actual_techniques 
                           if t.get("full_name") == expected_name]
                
                if matching:
                    actual_context = matching[0].get("context_type", "general")
                    test_count += 1
                    
                    if actual_context == expected_context:
                        correct_count += 1
                    else:
                        print(f"⚠ {paper_id} - {expected_name}: "
                              f"expected {expected_context}, got {actual_context}")
    
    if test_count == 0:
        pytest.skip("No papers with expected context types available")
    
    accuracy = correct_count / test_count
    
    # Assert 90% accuracy
    assert accuracy >= 0.90, \
        f"Context detection accuracy {accuracy:.1%} below 90% threshold " \
        f"({correct_count}/{test_count} correct)"
    
    print(f"✓ Context detection: {accuracy:.1%} accuracy ({correct_count}/{test_count})")


# T034: Text snippet extraction validation
@pytest.mark.pipeline
@pytest.mark.asyncio
async def test_snippet_extraction(
    sample_papers: dict[str, dict[str, Any]],
    extraction_service_url: str,
):
    """
    Verify 50-character context windows with accurate character offsets.
    
    Requirements:
    - FR-007: Text snippet extraction (±25 chars, max 3 snippets)
    
    Success criteria:
    - SC-008: Zero character offset misalignments
    """
    misalignments = []
    total_snippets = 0
    
    for paper_id, paper_data in list(sample_papers.items())[:3]:  # Test first 3 papers
        metadata = paper_data["metadata"]
        text = paper_data["text"]
        
        async with ExtractionAPIClient(extraction_service_url) as client:
            result = await client.extract_single_paper(
                paper_id=paper_id,
                title=metadata["title"],
                text=text,
                source_type=metadata["source_type"],
            )
            
            techniques = result.get("techniques", [])
            
            for technique in techniques:
                snippets = technique.get("text_snippets", [])
                
                # Verify max 3 snippets
                assert len(snippets) <= 3, \
                    f"Too many snippets: {len(snippets)} (max 3)"
                
                for snippet in snippets:
                    total_snippets += 1
                    snippet_text = snippet.get("text", "")
                    start_char = snippet.get("start_char", 0)
                    end_char = snippet.get("end_char", 0)
                    
                    # Verify offset alignment
                    if start_char >= 0 and end_char <= len(text):
                        expected_text = text[start_char:end_char]
                        if expected_text != snippet_text:
                            misalignments.append({
                                "paper_id": paper_id,
                                "technique": technique.get("full_name"),
                                "expected": expected_text[:50],
                                "actual": snippet_text[:50],
                            })
                    
                    # Verify snippet length (approximately 50 chars, ±25 around mention)
                    assert 20 <= len(snippet_text) <= 100, \
                        f"Snippet length {len(snippet_text)} outside expected range [20, 100]"
    
    if total_snippets == 0:
        pytest.skip("No snippets extracted")
    
    # Assert zero misalignments
    assert len(misalignments) == 0, \
        f"Found {len(misalignments)} snippet offset misalignments: {misalignments}"
    
    print(f"✓ Snippet extraction: {total_snippets} snippets validated, 0 misalignments")


# T035: Confidence score validation
@pytest.mark.pipeline
@pytest.mark.asyncio
async def test_confidence_scores(
    sample_papers: dict[str, dict[str, Any]],
    extraction_service_url: str,
):
    """
    Verify scores within expected ranges (±0.05 tolerance for BERTrend).
    
    Requirements:
    - FR-005: Confidence formula validation
    - Constitution Principle II: ±0.05 tolerance for bounded non-determinism
    
    Success criteria:
    - SC-005: Formula accuracy ±0.01 tolerance (confidence ranges ±0.05)
    """
    for paper_id, paper_data in sample_papers.items():
        metadata = paper_data["metadata"]
        text = paper_data["text"]
        expected_techniques = metadata["expected_techniques"]
        
        async with ExtractionAPIClient(extraction_service_url) as client:
            result = await client.extract_single_paper(
                paper_id=paper_id,
                title=metadata["title"],
                text=text,
                source_type=metadata["source_type"],
            )
            
            actual_techniques = result.get("techniques", [])
            
            # Validate confidence ranges for each expected technique
            for expected in expected_techniques:
                expected_name = expected["full_name"]
                min_conf = expected.get("min_confidence", 0.0)
                max_conf = expected.get("max_confidence", 1.0)
                
                matching = [t for t in actual_techniques 
                           if t.get("full_name") == expected_name]
                
                if matching:
                    confidence = matching[0].get("confidence", 0.0)
                    assert_confidence_range(
                        confidence=confidence,
                        expected_min=min_conf,
                        expected_max=max_conf,
                        tolerance=0.05,
                        technique_name=expected_name,
                    )
    
    print(f"✓ Confidence scores validated for {len(sample_papers)} papers")


# T036: expected_accuracy field validation
@pytest.mark.pipeline
@pytest.mark.asyncio
async def test_expected_accuracy_field(
    sample_papers: dict[str, dict[str, Any]],
    extraction_service_url: str,
):
    """
    Verify expected_accuracy calculated correctly based on source_type.
    
    Requirements:
    - FR-008: expected_accuracy field
    - Formula: academic=0.95, blog=0.90, press_release=0.85, podcast=0.80, social=0.70
    """
    expected_accuracy_by_source = {
        "academic": 0.95,
        "blog": 0.90,
        "press_release": 0.85,
        "podcast": 0.80,
        "social": 0.70,
    }
    
    for paper_id, paper_data in list(sample_papers.items())[:5]:  # Test first 5
        metadata = paper_data["metadata"]
        text = paper_data["text"]
        source_type = metadata["source_type"]
        
        async with ExtractionAPIClient(extraction_service_url) as client:
            result = await client.extract_single_paper(
                paper_id=paper_id,
                title=metadata["title"],
                text=text,
                source_type=source_type,
            )
            
            actual_accuracy = result.get("expected_accuracy")
            expected_accuracy = expected_accuracy_by_source.get(source_type, 0.90)
            
            assert actual_accuracy is not None, \
                f"expected_accuracy field missing for {paper_id}"
            
            assert actual_accuracy == expected_accuracy, \
                f"expected_accuracy {actual_accuracy} != {expected_accuracy} " \
                f"for source_type {source_type}"
    
    print(f"✓ expected_accuracy field validated")

