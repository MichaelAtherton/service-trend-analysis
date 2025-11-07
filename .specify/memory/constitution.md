<!--
=============================================================================
SYNC IMPACT REPORT - Constitution Update
=============================================================================
Version Change: 1.0.0 (Initial Ratification)
Date: 2025-11-03
Type: NEW - First constitution for AI Trend Analyzer API

Modified Principles:
- NEW: I. Async-First Job Processing
- NEW: II. Deterministic Multi-Pass Detection  
- NEW: III. Constitution-Guided Filtering
- NEW: IV. OpenAPI-First Design
- NEW: V. Three-Tier Error Classification
- NEW: VI. Graceful Degradation & Resilience
- NEW: VII. Railway Deployment Standards

Added Sections:
- Quality Gates Framework (from Railway seeder)
- Deployment Requirements (Railway-specific)

Templates Requiring Updates:
✅ plan-template.md - Already has "Constitution Check" section (line 30-34)
✅ spec-template.md - Already has "Requirements" section aligned with principles
✅ tasks-template.md - Already has phase structure supporting principle-driven tasks

Follow-up TODOs:
- None - All placeholders filled with concrete values

Rationale for Version 1.0.0:
- Initial ratification of constitution for AI Trend Analyzer API
- Combines proven Railway deployment patterns with AI domain requirements
- Establishes governance baseline for future development
=============================================================================
-->

# AI Trend Analyzer API Constitution

## Core Principles

### I. Async-First Job Processing

**Rule**: All I/O operations MUST use async/await patterns. No operation >2 seconds may block the request thread.

**Requirements**:
- HTTP client operations MUST use `httpx.AsyncClient` (not synchronous `requests`)
- File operations MUST use `aiofiles` (not built-in `open()`)
- Database queries MUST use async drivers (asyncpg, motor, etc.)
- Long-running operations (>2s) MUST return `job_id` immediately
- Background task tracking via `asyncio.create_task()`

**Rationale**: Blocking requests timeout users, prevent horizontal scaling, and limit throughput. Async patterns ensure the API remains responsive under load and can handle concurrent trend detection requests efficiently.

**Example**:
```python
# CORRECT: Async pattern
@router.post("/api/v1/analyze")
async def analyze(request: AnalysisRequest):
    job_id = str(uuid4())
    asyncio.create_task(run_detection(job_id, request))
    return {"job_id": job_id, "status": "started"}

# WRONG: Blocking pattern
@router.post("/api/v1/analyze")
def analyze(request: AnalysisRequest):
    results = run_detection(request)  # Blocks for 30+ seconds
    return results
```

---

### II. Deterministic Multi-Pass Detection

**Rule**: Trend detection MUST be rule-based and reproducible. Given the same corpus and constitution, the API MUST return consistent results within documented tolerance bounds.

**Requirements**:
- Four detection passes MUST execute in order: Emergence → Maturation → Decline → Gaps
- Each pass MUST use explicit thresholds (no randomness in threshold evaluation)
- Acceleration rate calculation: `recent_count / historical_count ≥ 3.0`
- Variance calculation: `sqrt(variance) / mean < 0.2` for maturation
- Date range windows MUST be configurable but have sensible defaults (30/60/90 days)
- All thresholds MUST be documented in OpenAPI schema

**Bounded Non-Determinism Allowance**:
- **Technique extraction** (AI Technique Extraction Service) uses BERTrend's neural topic clustering, which has stochastic elements (HDBSCAN initialization)
- **Acceptable variation**: Given the same input text batch:
  - Technique names MUST match exactly (100% reproducible via deterministic taxonomy mapping)
  - Confidence scores MAY vary by ±0.05 absolute difference due to topic cluster variations
  - Topic assignments MAY vary, but final extracted techniques MUST be stable
- **Random seed setting**: Where possible, set random seeds for reproducibility in development/testing
- **Trend detection** (downstream Trend Analyzer service) remains fully deterministic using rule-based thresholds

**Rationale**: Executives and researchers need reproducible analysis. BERTrend's semantic clustering (HDBSCAN + UMAP) provides superior quality over deterministic alternatives (k-means). The stochastic variation in intermediate topic assignments is acceptable because final technique mapping is deterministic. This aligns with BERTrend's production use at RTE France for real-time trend monitoring. Rule-based trend detection provides explainability and consistency.

**Pass Definitions**:
- **Pass A (Emergence)**: Recent acceleration ≥3x, first mention <60 days
- **Pass B (Maturation)**: 12-week variance <20%, ≥2 production signal papers
- **Pass C (Decline)**: Recent volume <30% of historical
- **Pass D (Gaps)**: Mature techniques (≥10 papers) with zero combined papers

---

### III. Constitution-Guided Filtering

**Rule**: Strategic focus areas MUST influence severity classification. Trends matching constitution keywords MUST receive severity boost.

**Requirements**:
- Constitution object MUST include `strategic_focus` array
- Boosting logic MUST be deterministic:
  - Emerging: 2+ focus matches → HIGH becomes CRITICAL
  - Maturing: 1+ "production" match → HIGH becomes CRITICAL  
  - Gaps: Strategic keyword + technique match → MEDIUM becomes HIGH
- Every trend response MUST include `constitution_match` object showing:
  - `matched_focus_areas`: Array of matched keywords
  - `boost_applied`: Boolean indicating if severity was boosted
- Constitution MUST be validated via Pydantic schema

**Rationale**: Generic trend detection lacks business context. Constitution filtering ensures critical trends align with organizational strategy (e.g., "real-time AI systems" boosts streaming-related trends).

**Example**:
```python
# If constitution.strategic_focus = ["real-time AI systems", "production-ready"]
# And trend technique = "streaming"
# Then severity boost: HIGH → CRITICAL (matches "real-time")
```

---

### IV. OpenAPI-First Design

**Rule**: The OpenAPI specification IS the contract. All endpoints, schemas, and examples MUST be auto-generated from FastAPI code using Pydantic models.

**Requirements**:
- Every endpoint MUST have:
  - Summary (1 sentence)
  - Description (detailed behavior)
  - Request/response examples (at least 1 per endpoint)
  - Error response examples (400, 422, 429, 500, 503)
- Every Pydantic field MUST have:
  - Type annotation
  - Description via `Field(description="...")`
  - Example value via `Field(example=...)`
  - Validation rules (min/max, pattern, etc.)
- Interactive docs MUST be available at `/docs` (Swagger UI)
- ReDoc MUST be available at `/redoc`
- Breaking changes REQUIRE major version bump (v2, v3)

**Rationale**: API documentation is infrastructure for consumers. Auto-generated specs eliminate drift between docs and implementation, while examples enable self-service adoption.

**Example**:
```python
class Paper(BaseModel):
    id: str = Field(description="Unique paper identifier", example="paper_001")
    title: str = Field(
        description="Paper title",
        min_length=10,
        max_length=500,
        example="Multi-Modal RAG with Vision APIs"
    )
    techniques: list[str] = Field(
        description="AI techniques mentioned in paper",
        min_items=1,
        example=["RAG", "multi-modal", "vision"]
    )
```

---

### V. Three-Tier Error Classification

**Rule**: Not all errors are failures. Errors MUST be classified into three tiers with distinct handling strategies.

**Requirements**:
- **Tier 1 - Expected (Not Failures)**:
  - HTTP 404 (resource doesn't exist)
  - Empty result sets (no papers found)
  - Action: Return None/empty, log at DEBUG level
- **Tier 2 - Retriable (Transient)**:
  - HTTP 5xx (server errors)
  - Network timeouts
  - Connection refused
  - Rate limit exceeded (429)
  - Action: Exponential backoff retry (max 3 attempts), log at WARNING
- **Tier 3 - Non-Retriable (Permanent)**:
  - HTTP 401/403 (auth failures)
  - HTTP 400 (bad request)
  - Malformed data
  - Action: Log with context at ERROR, continue with other items

**Rationale**: Retrying 404s wastes resources. Failing entire jobs on single item errors reduces data quality. Proper classification ensures resilience without unnecessary work.

**Example**:
```python
# Tier 1: Expected
if response.status_code == 404:
    logger.debug(f"Paper not found: {paper_id}")
    return None

# Tier 2: Retriable
if response.status_code >= 500:
    for attempt in range(3):
        await asyncio.sleep(2 ** attempt)
        # retry logic

# Tier 3: Non-retriable
if response.status_code in [401, 403]:
    logger.error(f"Auth failed for {url}")
    return None  # Skip and continue
```

---

### VI. Graceful Degradation & Resilience

**Rule**: Partial success is acceptable. If 1 of 100 papers fails validation, return 99 successful results with error context for the 1 failure.

**Requirements**:
- Batch operations MUST NOT fail entirely on single item errors
- Analysis response MUST include:
  - `status: "completed"` if all items processed
  - `status: "partial"` if some items failed
  - Error details for failed items (not just counts)
- Corpus validation endpoint MUST return:
  - `valid: true/false` (overall)
  - `warnings`: Array of non-blocking issues
  - `errors`: Array of validation failures with field paths
- Rate limiting MUST respect external API headers:
  - Check `X-RateLimit-Remaining`
  - Wait based on `X-RateLimit-Reset` or `Retry-After`

**Rationale**: Real-world data is messy. Users need their 99 successful results even when 1 paper has bad formatting. Complete failures frustrate users and reduce system utility.

**Example Response**:
```json
{
  "status": "partial",
  "corpus_stats": {
    "total_papers": 100,
    "processed": 99,
    "failed": 1
  },
  "trends": { /* 99 papers analyzed */ },
  "errors": [
    {
      "paper_id": "paper_042",
      "field": "date",
      "issue": "Invalid date format",
      "value": "10/15/2025"
    }
  ]
}
```

---

### VII. Railway Deployment Standards

**Rule**: All deployment configurations MUST follow Railway best practices for health, observability, and port handling.

**Requirements**:
- **Health Check Endpoint**:
  - Path: `/health` (no auth required)
  - Response time: <100ms (Railway timeout)
  - Returns: `{status, version, uptime_seconds, timestamp}`
  - HTTP 200 for healthy, 503 for unhealthy
- **Dockerfile Standards**:
  - Multi-stage build (builder + runtime)
  - Non-root user (`USER appuser`)
  - Virtual environment with proper ownership
  - Shell form CMD: `CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]`
  - No hardcoded PORT (Railway assigns dynamically)
- **railway.json Requirements**:
  - `builder: "DOCKERFILE"`
  - `dockerfilePath: "Dockerfile"`
  - `healthcheckPath: "/health"`
  - `healthcheckTimeout: 100` (milliseconds)
  - NO `startCommand` (use Dockerfile CMD for proper $PORT expansion)
- **Logging Standards**:
  - JSON format for production (structured logging)
  - Include: timestamp, level, message, request_id, user_context
  - Never log: API tokens, passwords, private data, PII

**Rationale**: Railway's platform has specific requirements. Following these standards prevents the 5 critical deployment issues: wrong app path, port mismatch, permission errors, missing files, and PORT variable expansion failures.

**Critical Railway Gotcha**:
```json
// WRONG: railway.json with startCommand (doesn't expand $PORT)
{
  "deploy": {
    "startCommand": "uvicorn src.main:app --port $PORT"
  }
}

// CORRECT: Let Dockerfile CMD handle it
{
  "deploy": {
    "healthcheckPath": "/health"
  }
}
```

---

## Quality Gates Framework

**GATE**: Before marking any feature "complete", it MUST pass ALL gates below.

### Documentation Gates
- [ ] OpenAPI spec generated and valid (no schema errors)
- [ ] All endpoints have request/response examples
- [ ] All data fields have descriptions
- [ ] README or quickstart includes curl example

### Resilience Gates
- [ ] Handles external API rate limits gracefully (no crashes)
- [ ] Handles 1+ failed items without killing entire job
- [ ] Handles network timeouts (retry logic with exponential backoff)
- [ ] Three-tier error classification implemented and tested

### Data Quality Gates
- [ ] Response schema consistent across all successful items
- [ ] Derived fields calculated correctly (acceleration, variance, etc.)
- [ ] No null/undefined fields unless explicitly Optional
- [ ] Timestamps in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- [ ] All numeric metrics have explicit precision (e.g., 2 decimal places)

### Observability Gates
- [ ] All errors logged with actionable context (job_id, paper_id, error_type)
- [ ] Health check endpoint responds in <100ms
- [ ] No sensitive data in logs (tokens masked, PII redacted)
- [ ] Request/response times logged for performance monitoring

### Domain Gates (AI Trend Analyzer Specific)
- [ ] Minimum corpus size enforced (50 papers, 30 days span)
- [ ] Every trend backed by ≥3 source papers
- [ ] Constitution matching logic tested with various focus areas
- [ ] Detection thresholds match OpenAPI documentation

---

## Deployment Requirements

### Local Development
```bash
# Must work with default settings
uvicorn src.main:app --reload --port 8000

# Environment variables via .env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### Railway Production
```bash
# Railway provides these automatically
PORT=<dynamic>
RAILWAY_ENVIRONMENT=production

# Must be set via Railway dashboard
EXTERNAL_API_KEY=<if-needed>
LOG_LEVEL=INFO
```

### Docker Build Requirements
- Image size: <500MB (use multi-stage build)
- Build time: <5 minutes
- Non-root user with UID >1000
- Python virtual environment at `/opt/venv`
- Exposed port: 8000 (default, Railway overrides with $PORT)

### Health Check Behavior
```bash
# Must return 200 OK in <100ms
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "queue_size": 2,
  "timestamp": "2025-11-03T10:00:00Z"
}
```

---

## Governance

### Amendment Process
1. Propose change via pull request to `.specify/memory/constitution.md`
2. Document rationale (why needed, what problem it solves)
3. Update affected templates (plan, spec, tasks)
4. Update version number per semantic versioning rules below
5. Update `LAST_AMENDED_DATE` to amendment date
6. Add sync impact report as HTML comment at top of file

### Version Bump Rules (Semantic Versioning)
- **MAJOR (X.0.0)**: Backward incompatible governance changes
  - Removing a principle
  - Redefining a principle in conflicting way
  - Example: Removing "Async-First" principle
- **MINOR (x.Y.0)**: New principle or material expansion
  - Adding a new principle
  - Significantly expanding guidance for existing principle
  - Example: Adding "Authentication Standards" principle
- **PATCH (x.y.Z)**: Clarifications and refinements
  - Wording improvements
  - Typo fixes
  - Non-semantic refinements
  - Example: Clarifying example code in principle

### Compliance Verification
- All PRs MUST verify constitution compliance before merge
- Spec documents MUST reference relevant principles in Requirements section
- Plan documents MUST include Constitution Check section
- Code reviews MUST check for:
  - Async patterns used for I/O
  - Error classification implemented correctly
  - OpenAPI examples provided
  - Health check response time <100ms

### Violations & Justification
Violations MUST be documented in plan.md Complexity Tracking table:
- What principle is violated
- Why the violation is necessary
- What simpler alternative was rejected and why

**Example**:
| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Synchronous file read | Config read at startup only | Async adds complexity for 1-time read at boot |

---

**Version**: 1.0.0 | **Ratified**: 2025-11-03 | **Last Amended**: 2025-11-03
