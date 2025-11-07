# Research: MVP Testing Procedures

**Feature**: MVP Testing Procedures | **Branch**: `002-mvp-testing` | **Date**: 2025-11-03

## Purpose

This document resolves all technical unknowns and clarifications identified in the Technical Context section of plan.md. It provides detailed evaluation of testing frameworks, reporting tools, fixture management strategies, and CI/CD integration approaches.

---

## 1. Testing Framework Selection

### Decision

**Selected**: **pytest 7.4+** with pytest-asyncio 0.21+

### Rationale

1. **Native Async Support**: pytest-asyncio plugin enables testing async FastAPI endpoints without manual event loop management
2. **Rich Plugin Ecosystem**: Over 1,000 plugins available including HTML reports, JSON exports, coverage, parallel execution
3. **Fixture System**: Powerful dependency injection for test setup/teardown, reusable across test modules
4. **Parametrization**: Easy testing of multiple scenarios with `@pytest.mark.parametrize`
5. **IDE Integration**: Excellent support in VS Code, PyCharm, and Cursor for test discovery and debugging
6. **Industry Standard**: 90%+ adoption in Python data science/ML projects, extensive documentation

### Alternatives Considered

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **unittest** | Built-in (no install), OOP-based | Verbose boilerplate, no async support, limited plugins | ❌ Rejected - Too basic |
| **nose2** | Similar to pytest | Less maintained (last release 2022), smaller ecosystem | ❌ Rejected - Aging project |
| **Robot Framework** | Keyword-driven, non-technical friendly | Heavyweight, overkill for API testing | ❌ Rejected - Not suitable |
| **pytest** | ✅ All benefits above | Learning curve for fixtures (minor) | ✅ **SELECTED** |

### Implementation Details

**Installation**:
```bash
pip install pytest==7.4.3 pytest-asyncio==0.21.1
```

**Configuration** (`pytest.ini`):
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --maxfail=5
markers =
    pipeline: Core extraction pipeline tests
    error_handling: Error handling and resilience tests
    monitoring: Health check and logging tests
    taxonomy: Taxonomy and confidence scoring tests
    slow: Tests that take >10 seconds
```

---

## 2. Multi-Format Reporting

### Decision

**Selected**: **pytest-html 3.2+** (HTML reports) + **pytest-json-report 1.5+** (JSON exports) + built-in console output

### Rationale

1. **Simultaneous Generation**: Plugins run in parallel, no custom code needed
2. **Human-Readable HTML**: Rich visualizations, collapsible sections, embedded screenshots (if needed)
3. **Machine-Readable JSON**: Structured data for CI/CD integration, trend analysis, custom dashboards
4. **Console Output**: Immediate feedback during local development, colored pass/fail indicators
5. **No Custom Code**: No maintenance burden, community-supported plugins

### Alternatives Considered

| Solution | Pros | Cons | Verdict |
|----------|------|------|---------|
| **pytest-html + pytest-json-report** | ✅ Simultaneous, widely adopted | Separate plugins (minor overhead) | ✅ **SELECTED** |
| **Allure** | Beautiful dashboards, trend history | Complex setup (Java dependency), server required | ❌ Rejected - Overkill |
| **Custom reporter** | Full control, tailored format | Maintenance burden, reinventing wheel | ❌ Rejected - Unnecessary |
| **JUnit XML only** | CI/CD standard | Not human-friendly, no visual reports | ❌ Rejected - Incomplete |

### Implementation Details

**Installation**:
```bash
pip install pytest-html==3.2.0 pytest-json-report==1.5.0
```

**Usage**:
```bash
# Generate all three formats in one run
pytest tests/ \
    --html=test-reports/report-$(date +%Y-%m-%d-%H-%M).html \
    --self-contained-html \
    --json-report \
    --json-report-file=test-reports/report-$(date +%Y-%m-%d-%H-%M).json \
    --json-report-indent=2
```

**HTML Report Features**:
- Summary dashboard (total/passed/failed/skipped/duration)
- Per-test details (assertions, logs, timing)
- Collapsible test body (stacktraces, captured output)
- Filter by status (failed, passed, skipped)
- Embedded CSS/JS (--self-contained-html for artifact portability)

**JSON Report Schema**:
```json
{
  "created": "2025-11-03T14:30:00Z",
  "duration": 285.4,
  "summary": {
    "total": 54,
    "passed": 52,
    "failed": 2,
    "skipped": 0
  },
  "tests": [
    {
      "nodeid": "tests/test_pipeline.py::test_extraction_accuracy",
      "outcome": "passed",
      "duration": 8.2,
      "call": {
        "longrepr": null,
        "outcome": "passed"
      }
    }
  ]
}
```

---

## 3. Fixture Management Strategy

### Decision

**Selected**: **Plain text files** (`tests/fixtures/papers/*.txt`) + **single metadata JSON** (`tests/fixtures/metadata.json`)

### Rationale

1. **Version Control Friendly**: Git diffs work naturally, reviewable in PR
2. **Human Readable**: Easy to edit, no special tools needed
3. **Simple Loading**: Python `open()` or pytest fixtures can read directly
4. **Separation of Concerns**: Paper text separate from expected results (metadata)
5. **Low Overhead**: No database, no binary parsing, no serialization complexity

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Plain text + JSON metadata** | ✅ All benefits above | Multiple files (minor) | ✅ **SELECTED** |
| **Embedded strings in test code** | No extra files | Not maintainable, clutters tests | ❌ Rejected - Unreadable |
| **SQLite database** | Queryable, single file | Binary (not git-diff friendly), overkill | ❌ Rejected - Unnecessary |
| **YAML files** | Human-readable, nested structure | Parsing overhead, YAML quirks | ❌ Rejected - JSON sufficient |
| **Binary formats (pickle, msgpack)** | Fast serialization | Not reviewable in PR, version control issues | ❌ Rejected - Not suitable |

### Fixture Structure

```text
tests/fixtures/
├── papers/
│   ├── paper_001_rag.txt                # RAG-focused paper (3,500 words)
│   ├── paper_002_rlhf.txt               # RLHF paper with production context
│   ├── paper_003_fine_tuning.txt        # Fine-tuning techniques
│   ├── paper_004_transformers.txt       # Transformer architecture paper
│   ├── paper_005_diffusion.txt          # Diffusion models (image generation)
│   ├── paper_006_multimodal.txt         # Multi-modal AI (vision + language)
│   ├── paper_007_quantization.txt       # Model compression techniques
│   ├── paper_008_prompt_engineering.txt # Prompting strategies (tutorial context)
│   ├── paper_009_evaluation.txt         # Evaluation metrics (criticism context)
│   └── paper_010_agents.txt             # AI agents and tool use
└── metadata.json                        # All expected results in one file
```

**metadata.json Schema**:
```json
{
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
        },
        {
          "full_name": "Transformer",
          "min_confidence": 0.75,
          "max_confidence": 0.90,
          "expected_context_type": "general",
          "mention_count": 5
        },
        {
          "full_name": "BERT",
          "min_confidence": 0.70,
          "max_confidence": 0.85,
          "expected_context_type": "general",
          "mention_count": 3
        }
      ]
    },
    {
      "paper_id": "paper_002",
      "file_path": "tests/fixtures/papers/paper_002_rlhf.txt",
      "title": "RLHF: Training Language Models from Human Feedback",
      "source_type": "academic",
      "character_count": 32100,
      "contains_latex": true,
      "expected_techniques": [
        {
          "full_name": "Reinforcement Learning from Human Feedback",
          "min_confidence": 0.95,
          "max_confidence": 1.00,
          "expected_context_type": "research",
          "mention_count": 18
        },
        {
          "full_name": "Proximal Policy Optimization",
          "min_confidence": 0.80,
          "max_confidence": 0.95,
          "expected_context_type": "research",
          "mention_count": 7
        }
      ]
    }
  ]
}
```

**pytest Fixture** (`tests/conftest.py`):
```python
import json
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def sample_papers():
    """Load all sample papers with metadata."""
    metadata_path = Path(__file__).parent / "fixtures" / "metadata.json"
    with open(metadata_path) as f:
        data = json.load(f)
    
    # Load paper text content
    for paper in data["papers"]:
        paper_path = Path(__file__).parent / "fixtures" / "papers" / Path(paper["file_path"]).name
        with open(paper_path, encoding="utf-8") as f:
            paper["text"] = f.read()
    
    return data["papers"]

@pytest.fixture
def rag_paper(sample_papers):
    """Get the RAG-focused paper for targeted tests."""
    return next(p for p in sample_papers if p["paper_id"] == "paper_001")
```

---

## 4. OpenAI API Testing Strategy

### Decision

**Selected**: **Real API calls** using dedicated test account with `OPENAI_API_KEY` environment variable

### Rationale

1. **Production Validation**: Tests actual LLM behavior, validates integration end-to-end
2. **Rate Limit Handling**: Validates retry logic, exponential backoff, 429 error handling
3. **Response Quality**: Ensures LLM validation (Stage 2 technique mapping) works with real responses
4. **No Maintenance**: No mock fixtures to update when API changes, no brittle VCR cassettes

### Cost Analysis

**Pricing** (gpt-4o-mini as of Nov 2025):
- Input: $0.00015 per 1K tokens (~750 words)
- Output: $0.00060 per 1K tokens

**Estimated Usage per Full Test Suite**:
- 8 sample papers × 1 LLM validation per paper (if Stage 1 exact match fails) = ~8 API calls
- Average prompt: 300 tokens (technique keywords + context)
- Average response: 50 tokens (technique name + confidence)
- Cost per call: (300 × $0.00015 + 50 × $0.00060) / 1000 = $0.000075
- **Total per suite**: 8 × $0.000075 = **$0.0006 (~$0.001)**
- **Monthly cost**: 100 CI/CD runs × $0.001 = **$0.10/month**
- **Yearly cost**: ~$1.20/year

**Cost Mitigation**:
- Selective CI/CD runs (PR + main only, not every commit to feature branches)
- Manual local execution for debugging (developers use own API keys)
- Cost tracking in test reports to monitor usage trends

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Real API calls** | ✅ Production validation, low cost ($0.001/run) | API key management, rate limits | ✅ **SELECTED** |
| **Mocking (unittest.mock)** | No cost, fast, deterministic | Doesn't test real API, misses integration issues | ❌ Rejected - Insufficient |
| **VCR.py cassettes** | Record real responses once, replay | Brittle with stochastic responses, cassette updates | ❌ Rejected - Not suitable |
| **Local LLM (ollama)** | No external dependency | Different model quality, setup complexity | ❌ Rejected - Not comparable |

### Implementation Details

**Environment Variable**:
```bash
# .env.test (not committed)
OPENAI_API_KEY=sk-test-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Pytest Configuration**:
```python
# tests/conftest.py
import os
import pytest
from openai import AsyncOpenAI

@pytest.fixture(scope="session")
def openai_client():
    """Async OpenAI client for LLM validation tests."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set - skipping LLM validation tests")
    return AsyncOpenAI(api_key=api_key)

@pytest.fixture(scope="session")
def cost_tracker():
    """Track OpenAI API usage for cost reporting."""
    tracker = {"calls": 0, "input_tokens": 0, "output_tokens": 0}
    yield tracker
    # Report at end of session
    cost = (tracker["input_tokens"] * 0.00015 + tracker["output_tokens"] * 0.00060) / 1000
    print(f"\n=== OpenAI API Usage ===")
    print(f"Total calls: {tracker['calls']}")
    print(f"Input tokens: {tracker['input_tokens']}")
    print(f"Output tokens: {tracker['output_tokens']}")
    print(f"Estimated cost: ${cost:.4f}")
```

**Rate Limit Handling**:
```python
# tests/utils/api_client.py
import asyncio
from openai import RateLimitError

async def call_with_retry(client, prompt, max_retries=3):
    """Call OpenAI API with exponential backoff on rate limits."""
    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
```

---

## 5. CI/CD Platform Selection

### Decision

**Selected**: **GitHub Actions** (primary) with GitLab CI as secondary option

### Rationale

1. **Native Railway Integration**: Railway deployment uses GitHub by default
2. **Free Tier**: 2,000 minutes/month for public repos, sufficient for this project
3. **Secrets Management**: Encrypted environment variables for `OPENAI_API_KEY`
4. **Artifact Uploads**: Built-in support for uploading HTML/JSON reports
5. **Matrix Builds**: Test multiple Python versions (3.11, 3.12) if needed
6. **Wide Adoption**: Standard in open-source Python projects

### Implementation Details

**GitHub Actions Workflow** (`.github/workflows/mvp-tests.yml`):
```yaml
name: MVP Testing Suite

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10  # Enforce <5min suite + buffer
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -e ".[test]"
      
      - name: Run MVP test suite
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY_TEST }}
        run: |
          mkdir -p test-reports
          pytest tests/ \
            --html=test-reports/report.html \
            --self-contained-html \
            --json-report \
            --json-report-file=test-reports/report.json \
            --json-report-indent=2 \
            -v
      
      - name: Upload test reports
        if: always()  # Upload even if tests fail
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: test-reports/
          retention-days: 30
      
      - name: Comment PR with results (if PR)
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('test-reports/report.json', 'utf8'));
            const body = `## MVP Test Results
            
            - **Total**: ${report.summary.total}
            - **Passed**: ✅ ${report.summary.passed}
            - **Failed**: ❌ ${report.summary.failed}
            - **Duration**: ${report.duration.toFixed(1)}s
            
            [View detailed HTML report](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.name,
              body: body
            });
```

**Required Secrets** (GitHub Repository Settings → Secrets):
- `OPENAI_API_KEY_TEST`: Test account API key (format: `sk-test-...`)

**GitLab CI Alternative** (`.gitlab-ci.yml`):
```yaml
mvp-tests:
  stage: test
  image: python:3.11
  only:
    - merge_requests
    - main
  script:
    - pip install -e ".[test]"
    - mkdir -p test-reports
    - pytest tests/ --html=test-reports/report.html --json-report --json-report-file=test-reports/report.json -v
  artifacts:
    when: always
    paths:
      - test-reports/
    expire_in: 30 days
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY_TEST
```

---

## 6. Sample Paper Curation

### Decision

**Selected**: **8 manually curated arXiv papers** (2023-2025) with human-labeled ground truth

### Curation Criteria

1. **Recency**: Published 2023-2025 (contemporary AI techniques)
2. **Language**: English only (validates FR-004 language detection)
3. **Length**: 3-5 pages (~3,000-5,000 words) for reasonable processing time
4. **Clarity**: Clear technique mentions (not oblique references)
5. **LaTeX**: Includes equations/citations for preprocessing validation
6. **Diversity**: Covers multiple technique categories (generation, fine-tuning, evaluation, etc.)
7. **Context Variety**: Mix of research, production, tutorial, criticism, general contexts

### Paper Selection

| Paper ID | Title | Primary Technique | Secondary Techniques | Context Type | Source |
|----------|-------|-------------------|----------------------|--------------|--------|
| paper_001 | Retrieval-Augmented Generation for Knowledge-Intensive NLP | RAG | Transformer, BERT | Research | arXiv:2005.11401 (excerpt) |
| paper_002 | Training Language Models from Human Feedback | RLHF | PPO, Reward Modeling | Research | InstructGPT paper (excerpt) |
| paper_003 | LoRA: Low-Rank Adaptation of Large Language Models | LoRA | Fine-Tuning, Adapter | Research | arXiv:2106.09685 (excerpt) |
| paper_004 | Attention Is All You Need | Transformer | Self-Attention | Research | Original Transformer paper (excerpt) |
| paper_005 | Denoising Diffusion Probabilistic Models | Diffusion | Denoising, DDPM | Research | arXiv:2006.11239 (excerpt) |
| paper_006 | Flamingo: Visual Language Models | Multi-Modal | Vision Transformer | Research | DeepMind paper (excerpt) |
| paper_007 | Quantization for Efficient Inference | Quantization | Pruning, Distillation | Production | Practical deployment paper |
| paper_008 | Best Practices for Prompt Engineering | Prompt Engineering | Few-Shot Learning | Tutorial | OpenAI cookbook style |
| paper_009 | Benchmarking LLM Hallucinations | Evaluation Metrics | Hallucination Detection | Criticism | Survey paper style |
| paper_010 | Tool-Augmented AI Agents | AI Agents | Tool Use, ReAct | Research | LangChain/AutoGPT style |

### Labeling Process

**Ground Truth Annotation**:
1. **Manual Review**: Domain expert (AI researcher/engineer) reads each paper
2. **Technique Identification**: Mark every explicit technique mention with line numbers
3. **Context Classification**: Label each mention as production/research/tutorial/criticism/general
4. **Confidence Baselines**: Establish expected confidence ranges based on:
   - Mention frequency (1 mention: 0.70-0.85, 5+ mentions: 0.90-1.00)
   - Source type (academic: ×1.0, blog: ×0.95, etc.)
   - Exact match vs. LLM validation (exact: 1.0, LLM: 0.0-1.0)
5. **Validation**: Second reviewer verifies labels for accuracy

**Example Annotation** (paper_001_rag.txt):
```
Expected Techniques:
- "Retrieval-Augmented Generation" (RAG)
  - Mentions: 12 (lines 15, 47, 89, 102, 156, 203, 245, 287, 310, 342, 378, 401)
  - Context: Research (all mentions in research context)
  - Expected confidence: 0.90-1.00 (exact match, high frequency, academic source)

- "Transformer"
  - Mentions: 5 (lines 67, 125, 189, 234, 356)
  - Context: General (architectural discussions)
  - Expected confidence: 0.75-0.90 (exact match, medium frequency)

- "BERT"
  - Mentions: 3 (lines 98, 167, 289)
  - Context: General (baseline comparisons)
  - Expected confidence: 0.70-0.85 (exact match, low frequency)
```

### Fixture Maintenance

**Version Control**:
- All 8 papers committed to `tests/fixtures/papers/`
- `metadata.json` committed to `tests/fixtures/`
- `.gitattributes` marks `*.txt` as text (for proper line ending handling)

**Updates**:
- Re-label if taxonomy changes significantly (new technique additions)
- Re-baseline confidence ranges if BERTrend model updated
- Add papers if new technique categories need coverage

---

## Research Completion Summary

### All Unknowns Resolved

✅ **Testing Framework**: pytest 7.4+ with pytest-asyncio  
✅ **Reporting**: pytest-html + pytest-json-report + console  
✅ **Fixtures**: Plain text files + metadata.json  
✅ **OpenAI Strategy**: Real API calls, ~$0.001 per run  
✅ **CI/CD**: GitHub Actions (primary), GitLab CI (secondary)  
✅ **Sample Papers**: 8 curated arXiv papers with human labels

### Implementation Ready

All research decisions documented with:
- Clear rationale for each choice
- Alternatives considered and rejected
- Concrete implementation details (code snippets, config files)
- Cost analysis and risk mitigation strategies

### Next Phase

Proceed to **Phase 1: Design & Contracts** to create:
1. `data-model.md` - Complete test case and fixture schemas
2. `contracts/` - JSON schemas for fixtures and reports
3. `quickstart.md` - Local setup and execution guide

---

**Research Status**: ✅ COMPLETE  
**Blockers**: None  
**Ready for Phase 1**: YES

