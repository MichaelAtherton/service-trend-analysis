"""
Custom assertion functions for technique extraction testing.

Provides specialized assertions for:
- Technique extraction accuracy
- Confidence score validation
- Expected vs actual comparisons
"""

from typing import Any


def assert_technique_extracted(
    actual_techniques: list[dict[str, Any]],
    expected_technique_name: str,
    min_confidence: float = 0.0,
    max_confidence: float = 1.0,
) -> dict[str, Any]:
    """
    Assert that a specific technique was extracted with confidence in expected range.
    
    Args:
        actual_techniques: List of extracted techniques from API response
        expected_technique_name: Expected technique full name
        min_confidence: Minimum acceptable confidence score
        max_confidence: Maximum acceptable confidence score
    
    Returns:
        dict: The matching technique object
    
    Raises:
        AssertionError: If technique not found or confidence out of range
    """
    matching_techniques = [
        t for t in actual_techniques
        if t.get("full_name") == expected_technique_name
    ]
    
    assert matching_techniques, (
        f"Technique '{expected_technique_name}' not found in extracted techniques. "
        f"Found: {[t.get('full_name') for t in actual_techniques]}"
    )
    
    technique = matching_techniques[0]
    confidence = technique.get("confidence", 0.0)
    
    assert min_confidence <= confidence <= max_confidence, (
        f"Confidence {confidence:.3f} for '{expected_technique_name}' "
        f"outside expected range [{min_confidence:.3f}, {max_confidence:.3f}]"
    )
    
    return technique


def assert_extraction_accuracy(
    actual_techniques: list[dict[str, Any]],
    expected_techniques: list[dict[str, Any]],
    min_accuracy: float = 0.85,
    tolerance: float = 0.05,
) -> dict[str, Any]:
    """
    Assert that extraction accuracy meets or exceeds minimum threshold.
    
    Accuracy is calculated as:
    - True positives: Expected techniques found with confidence within tolerance
    - False negatives: Expected techniques not found or confidence too low
    - Accuracy = true_positives / total_expected
    
    Args:
        actual_techniques: List of extracted techniques from API response
        expected_techniques: List of expected techniques with min/max confidence
        min_accuracy: Minimum acceptable accuracy (0.0-1.0)
        tolerance: Confidence tolerance for matching (e.g., ±0.05)
    
    Returns:
        dict: Statistics including accuracy, true_positives, false_negatives, false_positives
    
    Raises:
        AssertionError: If accuracy below minimum threshold
    """
    true_positives = []
    false_negatives = []
    
    for expected in expected_techniques:
        expected_name = expected["full_name"]
        expected_min_conf = expected.get("min_confidence", 0.0)
        expected_max_conf = expected.get("max_confidence", 1.0)
        
        # Widen range by tolerance to account for BERTrend stochastic variation
        adjusted_min = max(0.0, expected_min_conf - tolerance)
        adjusted_max = min(1.0, expected_max_conf + tolerance)
        
        matching = [
            t for t in actual_techniques
            if t.get("full_name") == expected_name
            and adjusted_min <= t.get("confidence", 0.0) <= adjusted_max
        ]
        
        if matching:
            true_positives.append({
                "expected": expected_name,
                "actual": matching[0],
            })
        else:
            false_negatives.append({
                "expected": expected_name,
                "reason": "not found" if expected_name not in [
                    t.get("full_name") for t in actual_techniques
                ] else "confidence out of range",
            })
    
    # Calculate false positives (extracted but not expected)
    expected_names = {e["full_name"] for e in expected_techniques}
    false_positives = [
        t for t in actual_techniques
        if t.get("full_name") not in expected_names
    ]
    
    # Calculate accuracy
    total_expected = len(expected_techniques)
    num_true_positives = len(true_positives)
    accuracy = num_true_positives / total_expected if total_expected > 0 else 0.0
    
    stats = {
        "accuracy": accuracy,
        "true_positives": true_positives,
        "false_negatives": false_negatives,
        "false_positives": false_positives,
        "total_expected": total_expected,
        "total_actual": len(actual_techniques),
    }
    
    assert accuracy >= min_accuracy, (
        f"Extraction accuracy {accuracy:.2%} below minimum {min_accuracy:.2%}. "
        f"True positives: {num_true_positives}/{total_expected}. "
        f"False negatives: {false_negatives}. "
        f"False positives: {[t.get('full_name') for t in false_positives]}"
    )
    
    return stats


def assert_confidence_range(
    confidence: float,
    expected_min: float,
    expected_max: float,
    tolerance: float = 0.05,
    technique_name: str = "unknown",
) -> None:
    """
    Assert that a confidence score falls within expected range (with tolerance).
    
    Args:
        confidence: Actual confidence score
        expected_min: Expected minimum confidence
        expected_max: Expected maximum confidence
        tolerance: Tolerance for stochastic variation (±0.05 for BERTrend)
        technique_name: Technique name for error message
    
    Raises:
        AssertionError: If confidence outside expected range + tolerance
    """
    adjusted_min = max(0.0, expected_min - tolerance)
    adjusted_max = min(1.0, expected_max + tolerance)
    
    assert adjusted_min <= confidence <= adjusted_max, (
        f"Confidence {confidence:.3f} for '{technique_name}' outside expected range "
        f"[{expected_min:.3f}, {expected_max:.3f}] ± {tolerance:.3f} tolerance. "
        f"Adjusted range: [{adjusted_min:.3f}, {adjusted_max:.3f}]"
    )


def assert_context_type(
    actual_context: str,
    expected_context: str,
    technique_name: str = "unknown",
) -> None:
    """
    Assert that context type matches expected value.
    
    Args:
        actual_context: Actual context type from extraction
        expected_context: Expected context type
        technique_name: Technique name for error message
    
    Raises:
        AssertionError: If context types don't match
    """
    valid_contexts = ["production", "research", "tutorial", "criticism", "general"]
    
    assert actual_context in valid_contexts, (
        f"Invalid context type '{actual_context}' for '{technique_name}'. "
        f"Must be one of: {valid_contexts}"
    )
    
    assert actual_context == expected_context, (
        f"Context type '{actual_context}' for '{technique_name}' "
        f"does not match expected '{expected_context}'"
    )

