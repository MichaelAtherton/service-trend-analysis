# Data Model: MVP Testing Procedures

**Feature**: MVP Testing Procedures | **Branch**: `002-mvp-testing` | **Date**: 2025-11-03

## Purpose

This document defines the data structures for test fixtures, test execution results, and validation reports. These models support the test suite's ability to load sample papers, execute validations, track results, and generate comprehensive reports.

---

## Core Entities

### 1. SamplePaper

Represents a test academic paper fixture with ground truth annotations.

**Purpose**: Input data for extraction pipeline validation tests

**Attributes**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `paper_id` | string | Yes | Unique identifier for the paper | `"paper_001"` |
| `file_path` | string | Yes | Relative path to paper text file | `"tests/fixtures/papers/paper_001_rag.txt"` |
| `title` | string | Yes | Paper title | `"Retrieval-Augmented Generation..."` |
| `text` | string | Runtime | Full paper text (loaded at runtime) | `"Abstract: We introduce..."` |
| `source_type` | string | Yes | Content source category | `"academic"` |
| `character_count` | integer | Yes | Total characters in text | `28450` |
| `contains_latex` | boolean | Yes | Whether paper includes LaTeX formatting | `true` |
| `expected_techniques` | array[ExpectedTechnique] | Yes | Ground truth technique annotations | See ExpectedTechnique below |

**Constraints**:
- `paper_id` must be unique across all fixtures
- `file_path` must exist and be readable
- `character_count` must match actual text length (±10 for whitespace normalization)
- `expected_techniques` must contain at least 1 technique

**Relationships**:
- Contains multiple `ExpectedTechnique` objects
- Used as input for multiple test cases in `test_pipeline.py`, `test_taxonomy.py`

**Storage**: 
- Paper text: `tests/fixtures/papers/{paper_id}.txt`
- Metadata: `tests/fixtures/metadata.json`

---

### 2. ExpectedTechnique

Represents ground truth annotation for a single technique mention in a paper.

**Purpose**: Define pass/fail thresholds for extraction accuracy validation

**Attributes**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `full_name` | string | Yes | Canonical technique name from taxonomy | `"Retrieval-Augmented Generation"` |
| `min_confidence` | float | Yes | Minimum acceptable confidence score | `0.90` |
| `max_confidence` | float | Yes | Maximum expected confidence score | `1.00` |
| `expected_context_type` | string | Yes | Expected context classification | `"research"` |
| `mention_count` | integer | Yes | Number of times technique mentioned | `12` |

**Constraints**:
- `min_confidence` range: 0.0 - 1.0
- `max_confidence` range: 0.0 - 1.0
- `min_confidence` ≤ `max_confidence`
- Range width (`max - min`) should account for BERTrend stochastic variation (typically ±0.05)
- `expected_context_type` must be one of: `"production"`, `"research"`, `"tutorial"`, `"criticism"`, `"general"`
- `mention_count` ≥ 1

**Validation Logic**:
```python
def validate_extraction(actual_technique, expected_technique):
    """Check if extracted technique matches expectations."""
    # Technique name must match exactly
    assert actual_technique["full_name"] == expected_technique["full_name"]
    
    # Confidence must be within range
    assert expected_technique["min_confidence"] <= actual_technique["confidence"] <= expected_technique["max_confidence"]
    
    # Context type must match
    assert actual_technique["context_type"] == expected_technique["expected_context_type"]
```

---

### 3. TestExecutionResult

Records the outcome of running a single test case.

**Purpose**: Capture actual vs. expected results for validation and reporting

**Attributes**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `execution_id` | string | Yes | Unique ID for this test run | `"exec_20251103_143045_001"` |
| `test_case_id` | string | Yes | pytest nodeid | `"tests/test_pipeline.py::test_extraction_accuracy[paper_001]"` |
| `paper_id` | string | Yes | Paper being tested | `"paper_001"` |
| `timestamp` | string (ISO 8601) | Yes | When test executed | `"2025-11-03T14:30:45Z"` |
| `status` | string | Yes | Test outcome | `"passed"` |
| `actual_techniques` | array[object] | Yes | Extracted techniques from API | `[{full_name: "RAG", confidence: 0.95, ...}]` |
| `actual_confidence_scores` | array[float] | Yes | List of confidence scores | `[0.95, 0.82, 0.77]` |
| `duration_ms` | integer | Yes | Test execution time | `8234` |
| `error_messages` | array[string] | Optional | Error details if failed | `["Technique 'BERT' not found"]` |
| `logs` | array[object] | Optional | Captured log entries | `[{level: "INFO", message: "..."}]` |

**Constraints**:
- `status` must be one of: `"passed"`, `"failed"`, `"skipped"`
- `duration_ms` ≥ 0
- `error_messages` required if `status == "failed"`
- `actual_techniques` length should match expected count (±1 for tolerance)

**Relationships**:
- Links to one `SamplePaper` via `paper_id`
- Aggregated into `ValidationReport`

---

### 4. ValidationReport

Aggregated summary of test suite execution.

**Purpose**: Provide high-level metrics and identify failing tests

**Attributes**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `report_id` | string | Yes | Unique report identifier | `"report_20251103_143000"` |
| `timestamp` | string (ISO 8601) | Yes | When suite started | `"2025-11-03T14:30:00Z"` |
| `total_tests` | integer | Yes | Total test cases executed | `54` |
| `passed_tests` | integer | Yes | Number of passed tests | `52` |
| `failed_tests` | integer | Yes | Number of failed tests | `2` |
| `skipped_tests` | integer | Yes | Number of skipped tests | `0` |
| `average_duration_ms` | integer | Yes | Mean test execution time | `5280` |
| `total_duration_s` | float | Yes | Total suite execution time | `285.4` |
| `critical_failures` | array[object] | Yes | High-priority failures | `[{test_id: "...", reason: "..."}]` |
| `recommendations` | array[string] | Yes | Actionable next steps | `["Fix preprocessing for paper_003"]` |
| `output_formats` | array[string] | Yes | Generated report formats | `["console", "html", "json"]` |
| `html_file_path` | string | Optional | Path to HTML report | `"test-reports/report-20251103-143000.html"` |
| `json_file_path` | string | Optional | Path to JSON report | `"test-reports/report-20251103-143000.json"` |

**Constraints**:
- `total_tests` = `passed_tests` + `failed_tests` + `skipped_tests`
- `total_duration_s` < 300 (5-minute timeout)
- `critical_failures` should list tests blocking MVP deployment
- `output_formats` must include all three: `["console", "html", "json"]`

**Relationships**:
- Aggregates multiple `TestExecutionResult` objects
- Generated by pytest plugins (pytest-html, pytest-json-report)

---

### 5. CostTracking

Tracks OpenAI API usage and estimated costs per test suite run.

**Purpose**: Monitor testing expenses for budget management

**Attributes**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `suite_run_id` | string | Yes | Links to ValidationReport | `"report_20251103_143000"` |
| `timestamp` | string (ISO 8601) | Yes | When tracking captured | `"2025-11-03T14:35:00Z"` |
| `total_api_calls` | integer | Yes | Number of OpenAI API requests | `8` |
| `input_tokens` | integer | Yes | Total input tokens consumed | `2400` |
| `output_tokens` | integer | Yes | Total output tokens consumed | `400` |
| `model_used` | string | Yes | OpenAI model identifier | `"gpt-4o-mini"` |
| `estimated_cost_usd` | float | Yes | Calculated cost in USD | `0.00060` |

**Constraints**:
- `total_api_calls` ≥ 0 (could be 0 if all Stage 1 exact matches)
- `estimated_cost_usd` = (input_tokens × $0.00015 + output_tokens × $0.00060) / 1000
- `model_used` should match actual model (expected: `"gpt-4o-mini"`)

**Calculation Formula**:
```python
def calculate_cost(input_tokens, output_tokens, model="gpt-4o-mini"):
    """Calculate OpenAI API cost based on token usage."""
    rates = {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.00060}  # per 1K tokens
    }
    rate = rates.get(model, rates["gpt-4o-mini"])
    return (input_tokens * rate["input"] + output_tokens * rate["output"]) / 1000
```

**Reporting**:
- Printed to console at end of pytest session
- Included in JSON report under `metadata.cost_tracking`
- Tracked in CI/CD logs for monthly budget monitoring

---

## Data Flow Diagram

```
┌─────────────────┐
│  SamplePaper    │  (Loaded from tests/fixtures/)
│  paper_id       │
│  expected_tech  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Test Execution (pytest)            │
│  - Load fixtures                    │
│  - Call extraction API              │
│  - Compare actual vs. expected      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│ TestExecution   │────▶│  CostTracking    │
│ Result          │     │  OpenAI usage    │
│ actual_tech     │     │  estimated_cost  │
│ status          │     └──────────────────┘
│ duration_ms     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ValidationReport│  (Generated by pytest plugins)
│ total_tests     │
│ passed/failed   │
│ critical_fail   │
│ recommendations │
└─────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Output Formats                     │
│  - Console (stdout)                 │
│  - HTML (test-reports/*.html)       │
│  - JSON (test-reports/*.json)       │
└─────────────────────────────────────┘
```

---

## Fixture Loading

### metadata.json Structure

```json
{
  "$schema": "./contracts/sample-paper-schema.json",
  "version": "1.0.0",
  "last_updated": "2025-11-03",
  "papers": [
    {
      "paper_id": "paper_001",
      "file_path": "tests/fixtures/papers/paper_001_rag.txt",
      "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP",
      "source_type": "academic",
      "character_count": 28450,
      "contains_latex": true,
      "expected_techniques": [
        {
          "full_name": "Retrieval-Augmented Generation",
          "min_confidence": 0.90,
          "max_confidence": 1.00,
          "expected_context_type": "research",
          "mention_count": 12
        }
      ]
    }
  ]
}
```

### pytest Fixture Implementation

```python
# tests/conftest.py
import json
import pytest
from pathlib import Path
from typing import List, Dict

@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Get path to fixtures directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def metadata(fixtures_dir: Path) -> Dict:
    """Load metadata.json with all sample paper annotations."""
    metadata_path = fixtures_dir / "metadata.json"
    with open(metadata_path, encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def sample_papers(metadata: Dict, fixtures_dir: Path) -> List[Dict]:
    """Load all sample papers with text content."""
    papers = []
    for paper_meta in metadata["papers"]:
        # Load paper text
        paper_path = fixtures_dir / "papers" / Path(paper_meta["file_path"]).name
        with open(paper_path, encoding="utf-8") as f:
            paper_meta["text"] = f.read()
        papers.append(paper_meta)
    return papers

@pytest.fixture
def rag_paper(sample_papers: List[Dict]) -> Dict:
    """Get paper_001 (RAG paper) for targeted tests."""
    return next(p for p in sample_papers if p["paper_id"] == "paper_001")

@pytest.fixture
def rlhf_paper(sample_papers: List[Dict]) -> Dict:
    """Get paper_002 (RLHF paper) for targeted tests."""
    return next(p for p in sample_papers if p["paper_id"] == "paper_002")

@pytest.fixture(scope="session")
def cost_tracker() -> Dict:
    """Track OpenAI API usage throughout test session."""
    tracker = {
        "suite_run_id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "total_api_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "model_used": "gpt-4o-mini"
    }
    yield tracker
    # Calculate and report cost at end of session
    cost = (tracker["input_tokens"] * 0.00015 + tracker["output_tokens"] * 0.00060) / 1000
    tracker["estimated_cost_usd"] = cost
    print(f"\n{'='*60}")
    print(f"OpenAI API Usage Summary")
    print(f"{'='*60}")
    print(f"Total API calls:    {tracker['total_api_calls']}")
    print(f"Input tokens:       {tracker['input_tokens']:,}")
    print(f"Output tokens:      {tracker['output_tokens']:,}")
    print(f"Estimated cost:     ${cost:.4f}")
    print(f"{'='*60}")
```

---

## Validation Assertions

### Custom Assertions for Technique Validation

```python
# tests/utils/assertions.py
from typing import Dict, List

def assert_technique_extracted(
    actual_techniques: List[Dict],
    expected_technique: Dict
) -> None:
    """Assert that expected technique was extracted correctly."""
    # Find matching technique
    actual = next(
        (t for t in actual_techniques if t["full_name"] == expected_technique["full_name"]),
        None
    )
    
    assert actual is not None, f"Technique '{expected_technique['full_name']}' not found in extraction results"
    
    # Validate confidence range
    min_conf = expected_technique["min_confidence"]
    max_conf = expected_technique["max_confidence"]
    actual_conf = actual["confidence"]
    
    assert min_conf <= actual_conf <= max_conf, (
        f"Confidence {actual_conf:.2f} outside expected range [{min_conf:.2f}, {max_conf:.2f}] "
        f"for technique '{expected_technique['full_name']}'"
    )
    
    # Validate context type
    expected_context = expected_technique["expected_context_type"]
    actual_context = actual["context_type"]
    
    assert actual_context == expected_context, (
        f"Context type '{actual_context}' does not match expected '{expected_context}' "
        f"for technique '{expected_technique['full_name']}'"
    )

def assert_extraction_accuracy(
    actual_techniques: List[Dict],
    expected_techniques: List[Dict],
    min_accuracy: float = 0.85
) -> None:
    """Assert that overall extraction accuracy meets threshold."""
    expected_names = {t["full_name"] for t in expected_techniques}
    actual_names = {t["full_name"] for t in actual_techniques}
    
    correct = len(expected_names & actual_names)
    total = len(expected_names)
    accuracy = correct / total if total > 0 else 0.0
    
    assert accuracy >= min_accuracy, (
        f"Extraction accuracy {accuracy:.1%} below threshold {min_accuracy:.1%}. "
        f"Found {correct}/{total} expected techniques. "
        f"Missing: {expected_names - actual_names}"
    )
```

---

## Data Model Summary

| Entity | Purpose | Storage | Lifecycle |
|--------|---------|---------|-----------|
| **SamplePaper** | Test input with ground truth | `tests/fixtures/` (version controlled) | Static (manual curation) |
| **ExpectedTechnique** | Pass/fail thresholds | Embedded in `metadata.json` | Static (manual labeling) |
| **TestExecutionResult** | Actual vs. expected comparison | Runtime (pytest memory) | Per test run |
| **ValidationReport** | Aggregated metrics | `test-reports/*.{html,json}` | Per suite run |
| **CostTracking** | OpenAI usage monitoring | Console + JSON report | Per suite run |

---

**Data Model Status**: ✅ COMPLETE  
**Schema Validation**: See `contracts/` directory for JSON schemas  
**Implementation**: Ready for pytest fixture development  
**Next Step**: Create `contracts/` directory with JSON schemas

