# Quickstart: MVP Testing Procedures

**Feature**: MVP Testing Procedures | **Branch**: `002-mvp-testing` | **Date**: 2025-11-03

## Purpose

This guide provides step-by-step instructions for setting up, running, and troubleshooting the MVP test suite for the AI Technique Extraction Service.

---

## Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **pip**: Latest version (comes with Python)
- **Git**: For cloning/version control
- **OpenAI API Access**: Test account with API key

### Required Services
- **Extraction Service**: MVP implementation (Phases 1-3) must be running
- **Embedding Server**: BERTrend embedding server must be accessible (or mocked)

### Environment Setup
- macOS, Linux, or WSL2 on Windows
- ~2GB free disk space (for dependencies + reports)
- Internet connection (for OpenAI API calls)

---

## Quick Start (5 Minutes)

### 1. Install Test Dependencies

From the repository root:

```bash
# Navigate to extraction service directory
cd services/technique-extraction

# Install service with test dependencies
pip install -e ".[test]"

# Verify pytest installation
pytest --version
# Expected output: pytest 7.4.3 (or higher)
```

**What's installed**:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-html` - HTML report generation
- `pytest-json-report` - JSON report generation
- `httpx` - Async HTTP client for API calls
- `openai` - OpenAI API client

### 2. Configure Environment

Create a `.env.test` file (not committed to git):

```bash
# Create .env.test file
cat > .env.test << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=sk-test-your-api-key-here

# Extraction Service Configuration
EXTRACTION_SERVICE_URL=http://localhost:8000
EMBEDDING_SERVER_URL=http://localhost:8765

# Test Configuration
PYTEST_TIMEOUT=300
LOG_LEVEL=INFO
EOF
```

**Load environment variables**:
```bash
export $(cat .env.test | xargs)
```

### 3. Start Required Services

**Terminal 1 - Embedding Server**:
```bash
cd services/embedding-server
python start_server.py
# Wait for: "Server ready on port 8765"
```

**Terminal 2 - Extraction Service**:
```bash
cd services/technique-extraction
uvicorn src.main:app --reload --port 8000
# Wait for: "Application startup complete"
```

### 4. Run Full Test Suite

**Terminal 3 - Tests**:
```bash
cd services/technique-extraction

# Run all tests with reports
pytest tests/ \
    --html=test-reports/report.html \
    --self-contained-html \
    --json-report \
    --json-report-file=test-reports/report.json \
    -v

# Expected output:
# ============================= test session starts ==============================
# collected 54 items
# tests/test_pipeline.py::test_health_check PASSED                         [  1%]
# tests/test_pipeline.py::test_extraction_accuracy[paper_001] PASSED      [  3%]
# ...
# ============================== 52 passed in 285.40s ============================
```

### 5. View Reports

**HTML Report** (Human-readable):
```bash
open test-reports/report.html
# or: xdg-open test-reports/report.html (Linux)
```

**JSON Report** (Programmatic):
```bash
cat test-reports/report.json | jq '.summary'
# Output: {"total": 54, "passed": 52, "failed": 2, "skipped": 0}
```

**Console Output**: Already visible in terminal with colored pass/fail indicators

---

## Detailed Setup

### Installing Development Mode

For development with editable install:

```bash
cd services/technique-extraction

# Create virtual environment (recommended)
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in editable mode with test dependencies
pip install --upgrade pip
pip install -e ".[test]"

# Verify installation
python -c "import pytest; print(pytest.__version__)"
```

### Configuring pytest

The `pytest.ini` file is already configured, but you can customize:

```ini
# services/technique-extraction/pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --maxfail=10

markers =
    pipeline: Core extraction pipeline tests
    error_handling: Error handling tests
    monitoring: Health check and logging tests
    taxonomy: Taxonomy and confidence tests
    slow: Tests that take >10 seconds
```

### Setting Up Test Fixtures

Fixtures are already included in the repository under `tests/fixtures/`:

```text
tests/fixtures/
├── papers/
│   ├── paper_001_rag.txt
│   ├── paper_002_rlhf.txt
│   └── ... (8 total papers)
└── metadata.json
```

**Verify fixtures exist**:
```bash
ls -lh tests/fixtures/papers/
# Should show 8 .txt files

cat tests/fixtures/metadata.json | jq '.papers | length'
# Should output: 8
```

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suite

```bash
# User Story 1: Core extraction pipeline
pytest tests/test_pipeline.py -v

# User Story 2: Error handling
pytest tests/test_error_handling.py -v

# User Story 3: Monitoring
pytest tests/test_monitoring.py -v

# User Story 4: Taxonomy and confidence
pytest tests/test_taxonomy.py -v
```

### Run Single Test

```bash
pytest tests/test_pipeline.py::test_extraction_accuracy -v

# With specific paper
pytest tests/test_pipeline.py::test_extraction_accuracy[paper_001] -v
```

### Run Tests by Marker

```bash
# Only pipeline tests
pytest -m pipeline -v

# Exclude slow tests
pytest -m "not slow" -v

# Multiple markers
pytest -m "pipeline or taxonomy" -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View HTML coverage report
open htmlcov/index.html
```

---

## Interpreting Results

### Console Output

```
============================= test session starts ==============================
platform darwin -- Python 3.11.5, pytest-7.4.3, pluggy-1.3.0
collected 54 items

tests/test_pipeline.py::test_extraction_accuracy[paper_001] PASSED      [  1%]
tests/test_pipeline.py::test_extraction_accuracy[paper_002] PASSED      [  3%]
...
tests/test_taxonomy.py::test_confidence_calculation PASSED              [100%]

=========================== 52 passed, 2 failed in 285.40s =====================
```

**Status Indicators**:
- ✅ `PASSED` - Test succeeded, met all assertions
- ❌ `FAILED` - Test failed, check assertion error details
- ⏭️ `SKIPPED` - Test skipped (e.g., missing OpenAI API key)
- ⚠️ `ERROR` - Setup/teardown error, not a test failure

### HTML Report

**Key Sections**:
1. **Summary Dashboard**: Total/passed/failed/skipped counts, duration
2. **Results Table**: List of all tests with status and duration
3. **Failed Tests**: Expandable details showing assertion errors and stacktraces
4. **Logs**: Captured stdout/stderr for debugging

**Filters**:
- Click "passed", "failed", or "skipped" to filter test list
- Expand test rows to see detailed output

### JSON Report

**Programmatic Analysis**:
```bash
# Check overall pass rate
jq '.summary.passed / .summary.total * 100' test-reports/report.json
# Output: 96.296 (96.3% pass rate)

# List failed tests
jq '.tests[] | select(.outcome == "failed") | .nodeid' test-reports/report.json

# Find slowest tests
jq '.tests | sort_by(.duration) | reverse | .[0:5] | .[] | {test: .nodeid, duration: .duration}' test-reports/report.json
```

### Cost Tracking

At the end of the test run, you'll see:

```
============================================================
OpenAI API Usage Summary
============================================================
Total API calls:    8
Input tokens:       2,400
Output tokens:      400
Estimated cost:     $0.0006
============================================================
```

**Monthly Budget Estimation**:
- Cost per run: ~$0.001
- Estimated CI/CD runs per month: 100 (PRs + main commits)
- **Monthly cost**: ~$0.10

---

## Troubleshooting

### Problem: OpenAI API Key Not Set

**Error**:
```
SKIPPED [1] tests/conftest.py:15: OPENAI_API_KEY not set - skipping LLM validation tests
```

**Solution**:
```bash
export OPENAI_API_KEY="sk-test-your-api-key-here"
pytest tests/ -v
```

### Problem: Extraction Service Not Running

**Error**:
```
httpx.ConnectError: [Errno 61] Connection refused
```

**Solution**:
```bash
# Start service in another terminal
cd services/technique-extraction
uvicorn src.main:app --port 8000

# Verify service is up
curl http://localhost:8000/health
```

### Problem: Embedding Server Timeout

**Error**:
```
TimeoutException: Embedding server did not respond within 30s
```

**Solution**:
```bash
# Check if embedding server is running
curl http://localhost:8765/health

# If not running, start it
cd services/embedding-server
python start_server.py
```

### Problem: Test Fixtures Not Found

**Error**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/metadata.json'
```

**Solution**:
```bash
# Verify you're in the correct directory
pwd
# Should end with: services/technique-extraction

# Check fixtures exist
ls -la tests/fixtures/
# Should show papers/ directory and metadata.json
```

### Problem: Tests Timeout After 5 Minutes

**Error**:
```
E   Failed: Timeout >300.0s
```

**Solution**:
```bash
# Run subset of tests to isolate slow tests
pytest tests/test_pipeline.py -v --durations=10

# Or increase timeout in pytest.ini
# addopts = --timeout=600
```

### Problem: Confidence Scores Outside Expected Range

**Error**:
```
AssertionError: Confidence 0.82 outside expected range [0.90, 1.00] for technique 'RAG'
```

**Analysis**:
- BERTrend clustering has stochastic variation (±0.05 expected)
- If consistently outside range, check:
  1. Is taxonomy loaded correctly? (`pytest tests/test_taxonomy.py::test_taxonomy_loading`)
  2. Is frequency boost calculated? (`pytest tests/test_taxonomy.py::test_confidence_calculation`)
  3. Are text snippets captured correctly? (`pytest tests/test_pipeline.py::test_snippet_extraction`)

**Solution**:
```bash
# Run multiple times to check for consistent variation
for i in {1..5}; do
  pytest tests/test_pipeline.py::test_extraction_accuracy[paper_001] -v
done

# If consistently low, may need to adjust expected range in metadata.json
```

### Problem: OpenAI Rate Limit Hit

**Error**:
```
openai.RateLimitError: Rate limit reached for gpt-4o-mini
```

**Solution**:
```bash
# Wait for rate limit reset (check Retry-After header)
sleep 60

# Or reduce concurrent tests
pytest tests/ -n 1  # Sequential execution (if using pytest-xdist)

# Or skip LLM validation tests temporarily
pytest tests/ -m "not taxonomy" -v
```

---

## Advanced Usage

### Parallel Test Execution

Install `pytest-xdist`:
```bash
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/ -n 4 -v
```

**Note**: May increase OpenAI API costs due to concurrent calls.

### Debugging Failed Tests

```bash
# Enter debugger on failure
pytest tests/test_pipeline.py --pdb

# Show local variables in traceback
pytest tests/test_pipeline.py -l

# Verbose output with print statements
pytest tests/test_pipeline.py -v -s
```

### Marking Tests for Selective Runs

```python
# Add custom marker to slow test
@pytest.mark.slow
def test_large_batch_processing():
    pass
```

```bash
# Run only slow tests
pytest -m slow -v

# Skip slow tests for quick validation
pytest -m "not slow" -v
```

### Mocking External Dependencies

For faster local development without hitting real APIs:

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_openai_client(monkeypatch):
    """Mock OpenAI client to avoid real API calls."""
    mock = AsyncMock()
    mock.chat.completions.create.return_value = MockResponse(
        choices=[{"message": {"content": "Mocked technique"}}]
    )
    monkeypatch.setattr("src.services.technique_mapper.OpenAI", lambda: mock)
    return mock
```

```bash
# Run tests with mocked OpenAI (no API costs)
pytest tests/ --mock-openai -v
```

---

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Pull requests to `main`
- Direct commits to `main`

**View CI/CD Results**:
1. Go to repository on GitHub
2. Click "Actions" tab
3. Select "MVP Testing Suite" workflow
4. View logs and download test report artifacts

**Local Simulation**:
```bash
# Run tests as CI/CD would (strict mode)
pytest tests/ \
    --strict-markers \
    --tb=short \
    --maxfail=1 \
    --html=test-reports/report.html \
    --json-report \
    -v
```

### Pre-commit Hook (Optional)

Run tests before every commit:

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
cd services/technique-extraction
pytest tests/ -q --maxfail=1
EOF

chmod +x .git/hooks/pre-commit
```

**Note**: This will increase commit time but catches failures early.

---

## Best Practices

### Local Development Workflow

1. **Make code changes** in `src/`
2. **Run affected tests** (e.g., `pytest tests/test_pipeline.py -v`)
3. **Verify all tests pass** before committing
4. **Generate reports** for manual review if needed
5. **Push to feature branch** (CI/CD will run full suite)

### Cost Management

- **Local development**: Manual execution (no CI/CD costs)
- **Feature branches**: Manual test runs as needed
- **Pull requests**: Automated CI/CD (incurs OpenAI costs ~$0.001)
- **Main branch**: Automated CI/CD (budget for ~50 runs/month)

### Fixture Maintenance

- **Add new papers**: Place in `tests/fixtures/papers/`, update `metadata.json`
- **Update expected ranges**: Adjust `min_confidence` / `max_confidence` if BERTrend model changes
- **Validate fixtures**: Run `pytest tests/test_fixtures.py -v` after updates

---

## Next Steps

1. **Familiarize with reports**: Run full suite and explore HTML/JSON outputs
2. **Run specific suites**: Target user stories relevant to your work
3. **Integrate into workflow**: Run tests before pushing changes
4. **Monitor costs**: Track OpenAI usage in test reports
5. **Report issues**: If tests consistently fail, check troubleshooting section

---

## Support

**Documentation**:
- Feature spec: [spec.md](./spec.md)
- Implementation plan: [plan.md](./plan.md)
- Data models: [data-model.md](./data-model.md)

**Common Issues**:
- See "Troubleshooting" section above
- Check test logs in `test-reports/` directory
- Review CI/CD workflow logs on GitHub

**Questions**:
- Review existing test code in `tests/` directory
- Check pytest documentation: https://docs.pytest.org/
- Check pytest-asyncio docs: https://pytest-asyncio.readthedocs.io/

---

**Quickstart Status**: ✅ COMPLETE  
**Estimated Setup Time**: 5-10 minutes (with prerequisites)  
**Expected First Run Duration**: ~4 minutes (30s per paper × 8 papers + overhead)  
**Ready for Testing**: YES

