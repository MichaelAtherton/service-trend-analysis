# MVP Testing Suite - AI Technique Extraction Service

Comprehensive test suite for validating the AI Technique Extraction Service MVP (Phases 1-3).

## Overview

This test suite validates:
- ✅ **Core Extraction Pipeline** (User Story 1) - 85%+ technique identification, <10s processing
- ✅ **Error Handling & Resilience** (User Story 2) - Three-tier error classification
- ✅ **Health & Monitoring** (User Story 3) - <100ms health checks, structured logging
- ✅ **Taxonomy & Confidence** (User Story 4) - 50+ techniques, confidence formula validation

## Quick Start

### 1. Install Dependencies

```bash
cd services/technique-extraction
pip install -e ".[test]"
```

### 2. Configure Environment

```bash
# Copy template
cp .env.test.example .env.test

# Edit .env.test and add your keys:
# - OPENAI_API_KEY (required for LLM validation tests)
# - EXTRACTION_SERVICE_URL (default: http://localhost:8000)
# - EMBEDDING_SERVER_URL (default: http://localhost:8765)
```

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with HTML report
pytest tests/ --html=test-reports/report.html --self-contained-html

# Run with JSON report
pytest tests/ --json-report --json-report-file=test-reports/report.json

# Run specific test suite
pytest tests/test_pipeline.py -v -m pipeline
pytest tests/test_error_handling.py -v -m error_handling
pytest tests/test_monitoring.py -v -m monitoring
pytest tests/test_taxonomy.py -v -m taxonomy

# Run fast tests only (skip slow/API-heavy tests)
pytest tests/ -v -m "not slow"
```

## Test Organization

### Directory Structure

```
tests/
├── README.md                   # This file
├── conftest.py                 # Pytest fixtures (session-scoped)
├── __init__.py
├── fixtures/                   # Test data
│   ├── papers/                 # 10 sample academic papers
│   │   ├── README.md           # Curation instructions
│   │   ├── paper_001_rag.txt
│   │   └── ...
│   └── metadata.json           # Ground truth annotations
├── utils/                      # Test utilities
│   ├── __init__.py
│   ├── api_client.py           # Async HTTP client
│   ├── assertions.py           # Custom assertions
│   └── cost_tracker.py         # OpenAI cost tracking
├── test_pipeline.py            # US1: Core pipeline (12 tests)
├── test_error_handling.py      # US2: Error handling (12 tests)
├── test_monitoring.py          # US3: Monitoring (12 tests)
└── test_taxonomy.py            # US4: Taxonomy (15 tests)
```

### Test Markers

Tests are organized by markers for selective execution:

- `@pytest.mark.pipeline` - Core extraction pipeline tests (US1)
- `@pytest.mark.error_handling` - Error handling tests (US2)
- `@pytest.mark.monitoring` - Health & logging tests (US3)
- `@pytest.mark.taxonomy` - Taxonomy & confidence tests (US4)
- `@pytest.mark.slow` - Tests that take significant time or make many API calls

## Test Fixtures

### Required Fixtures (Manual Setup)

**⚠️ CRITICAL**: Before running tests, you must:

1. **Curate 10 sample papers** (T008-T017):
   - See `fixtures/papers/README.md` for instructions
   - Find papers on arXiv covering RAG, RLHF, fine-tuning, etc.
   - Save as plain text files (remove references, keep LaTeX for testing)

2. **Label expected techniques** (T018):
   - Manually review each paper
   - Identify all AI techniques mentioned
   - Classify context types (production/research/tutorial/criticism/general)
   - Estimate confidence ranges based on frequency and clarity

3. **Update metadata.json** (T019):
   - Fill in expected_techniques for each paper
   - Set character_count, contains_latex, etc.
   - Follow `contracts/sample-paper-schema.json` structure

4. **Validate metadata** (T020):
   ```bash
   jsonschema -i fixtures/metadata.json contracts/sample-paper-schema.json
   ```

### Session-Scoped Fixtures

Defined in `conftest.py`:

- `fixtures_dir` - Path to test fixtures directory
- `metadata` - Loaded metadata.json (ground truth)
- `sample_papers` - Dict of all 10 papers with metadata + text
- `cost_tracker` - OpenAI API usage tracker (reports at end of session)
- `openai_api_key` - API key from environment (skips if not set)
- `extraction_service_url` - Service URL (default: localhost:8000)
- `embedding_server_url` - Embedding server URL (default: localhost:8765)

### Paper-Specific Fixtures

For targeted testing:

- `rag_paper` - RAG paper (paper_001)
- `rlhf_paper` - RLHF paper (paper_002)
- `finetuning_paper` - Fine-tuning paper (paper_003)
- ... (10 total)

## Test Coverage

### User Story 1: Core Pipeline (12 tests)

- ✅ Health check validation
- ✅ Extraction accuracy (85%+ for all 10 papers)
- ✅ Processing time (<10s per paper)
- ✅ LaTeX preprocessing
- ✅ Exact technique matching (Stage 1)
- ✅ Context detection (production/research/etc.)
- ✅ Snippet extraction (50-char windows)
- ✅ Confidence score ranges (±0.05 tolerance)
- ✅ expected_accuracy field

**Run**: `pytest tests/test_pipeline.py -v -m pipeline`

### User Story 2: Error Handling (12 tests)

- ✅ Tier 1: Empty results (HTTP 200, no error)
- ✅ Tier 2: Timeout retry (3 attempts, exponential backoff)
- ✅ Tier 2: 500 error after retries
- ✅ Tier 3: Validation error (HTTP 400, immediate)
- ✅ Tier 3: Malformed JSON (HTTP 422)
- ✅ Tier 3: No retry for validation errors
- ✅ Partial batch failure (graceful degradation)
- ⚠️ Error logging validation (requires log inspection - TODO)

**Run**: `pytest tests/test_error_handling.py -v -m error_handling`

### User Story 3: Monitoring (12 tests)

- ✅ Health check <100ms (100 consecutive requests)
- ✅ Health check schema (status, version, timestamp, etc.)
- ✅ Health check status codes (200=healthy, 503=unhealthy)
- ⚠️ Structured logging validation (requires log inspection - TODO)
- ⚠️ Log phase tracking (requires log inspection - TODO)
- ⚠️ Confidence metrics in logs (requires log inspection - TODO)
- ⚠️ No sensitive data in logs (requires log inspection - TODO)
- ⚠️ Error logging format (requires log inspection - TODO)
- ⚠️ JSON log format (requires log inspection - TODO)
- ✅ Example log structure validation (placeholder)

**Run**: `pytest tests/test_monitoring.py -v -m monitoring`

**Note**: Many logging tests are placeholders pending log inspection implementation.

### User Story 4: Taxonomy (15 tests)

- ⚠️ Taxonomy loading (requires service inspection - TODO)
- ✅ Exact match confidence (Stage 1)
- ✅ LLM fallback (Stage 2, makes real OpenAI calls)
- ✅ Confidence formula for academic papers
- ✅ Confidence formula for social media
- ✅ Frequency boost tiers (1=1.0, 2-4=1.1, 5+=1.2)
- ✅ Source multipliers (academic=1.0, social=0.80, etc.)
- ✅ Confidence capping (max 1.0)
- ⚠️ Context detection accuracy (requires labeled dataset - TODO)
- ✅ Newly discovered technique flagging
- ⚠️ OpenAI rate limit handling (requires simulation - TODO)
- ✅ Cost tracking structure

**Run**: `pytest tests/test_taxonomy.py -v -m taxonomy`

## Success Criteria

Mapped to specification (spec.md):

- **SC-001**: 85%+ technique identification ➔ `test_extraction_accuracy()`
- **SC-002**: <10s per paper ➔ `test_processing_time()`
- **SC-003**: Health <100ms ➔ `test_health_check_response_time()`
- **SC-004**: Three-tier errors ➔ `test_tier1_*/test_tier2_*/test_tier3_*`
- **SC-005**: Confidence formula ➔ `test_confidence_formula_*`
- **SC-006**: Logging fields ➔ `test_structured_logging_fields()`
- **SC-007**: 90% context accuracy ➔ `test_context_detection_accuracy()`
- **SC-008**: Zero offset misalignments ➔ `test_snippet_extraction()`
- **SC-009**: 100% flagging ➔ `test_newly_discovered_flagging()`
- **SC-010**: <5min suite ➔ Measured via pytest duration
- **SC-011**: Clear failures ➔ HTML/JSON reports
- **SC-012**: 95% coverage ➔ Run with `pytest --cov`

## OpenAI API Costs

Tests use **real OpenAI API calls** for LLM validation (Stage 2 technique mapping).

**Estimated Costs**:
- Per test run: $0.001 - $0.005 (minimal, mostly cached/exact matches)
- Full suite (10 papers): ~$0.05 - $0.20
- CI/CD (100 runs/month): ~$5 - $20/month

**Cost Tracking**:
- Automatic cost tracker reports at end of session
- Shows: total API calls, input/output tokens, estimated cost
- Based on gpt-4o-mini pricing: $0.150/1M input, $0.600/1M output tokens

## CI/CD Integration

See Phase 7 tasks (T078-T094) for GitHub Actions workflow setup.

**Workflow**:
```yaml
# .github/workflows/mvp-tests.yml
on: [pull_request, push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -e ".[test]"
      - run: pytest tests/ --html=report.html --json-report
      - uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: test-reports/
```

## Troubleshooting

### Tests skipped with "Paper not available"

**Issue**: Sample papers not curated yet (T008-T017)  
**Solution**: Follow `fixtures/papers/README.md` to curate papers from arXiv

### Tests fail with "OPENAI_API_KEY not set"

**Issue**: Missing OpenAI API key for LLM validation tests  
**Solution**: Set `OPENAI_API_KEY` in `.env.test` or environment

### Connection errors to localhost:8000

**Issue**: Extraction service not running  
**Solution**: Start the service first:
```bash
cd services/technique-extraction
uvicorn src.main:app --reload
```

### Tests take too long (>5 minutes)

**Issue**: Running slow tests or making many API calls  
**Solution**: Skip slow tests: `pytest -m "not slow"`

### Confidence scores outside expected range

**Issue**: BERTrend stochastic variation  
**Solution**: This is expected (±0.05 tolerance). Verify technique names are exact.

## Development Workflow

1. **MVP First** (User Story 1):
   ```bash
   pytest tests/test_pipeline.py -v
   ```

2. **Incremental Addition**:
   ```bash
   pytest tests/test_error_handling.py -v  # US2
   pytest tests/test_monitoring.py -v      # US3
   pytest tests/test_taxonomy.py -v        # US4
   ```

3. **Full Validation**:
   ```bash
   pytest tests/ -v --html=test-reports/report.html
   ```

4. **Review Reports**:
   - Open `test-reports/report.html` in browser
   - Check `test-reports/report.json` for automation

## Contributing

When adding new tests:

1. Follow existing test structure and naming
2. Add appropriate `@pytest.mark.*` markers
3. Document expected behavior in docstrings
4. Update this README if adding new fixtures or utilities
5. Ensure tests can run independently (no cross-dependencies)

## Status

- ✅ **Phase 1: Setup** - Complete
- ✅ **Phase 2: Foundational** - Infrastructure complete, fixtures require manual curation
- ✅ **Phase 3: User Story 1** - Tests implemented (12/12)
- ✅ **Phase 4: User Story 2** - Tests implemented (12/12, some require log inspection)
- ✅ **Phase 5: User Story 3** - Tests implemented (12/12, many require log inspection)
- ✅ **Phase 6: User Story 4** - Tests implemented (15/15, some require datasets)
- ⏳ **Phase 7: CI/CD** - Pending

**Ready for**: Sample paper curation (T008-T018) and first test execution (T038)

