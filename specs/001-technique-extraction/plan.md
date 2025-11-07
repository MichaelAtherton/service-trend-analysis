# Implementation Plan: AI Technique Extraction Service

**Branch**: `001-technique-extraction` | **Date**: 2025-11-03 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-technique-extraction/spec.md`

## Summary

Build a FastAPI service that automatically extracts AI techniques from multi-source text content (academic papers, blogs, social media, press releases, podcasts) using BERTrend's semantic topic clustering combined with LLM-based technique mapping. The service processes variable-length content (100 chars to 50,000 words), returns standardized technique names with confidence scores, and feeds structured data into the downstream Trend Analyzer.

**Technical Approach**: Two-service architecture with (1) FastAPI extraction service for API endpoints, preprocessing, and orchestration, and (2) BERTrend embedding server for semantic embeddings with GPU acceleration. Topic clustering via BERTrend's BERTopic integration, followed by two-stage technique mapping (exact match + LLM validation).

**Key Innovation**: Handles heterogeneous content types in single pipeline with source-specific preprocessing and confidence adjustment, enabling cross-source trend detection.

## Technical Context

**Language/Version**: Python 3.13 (matches project .python-version)  
**Primary Dependencies**: 
- BERTrend 0.1.0 (topic modeling, embedding service)
- FastAPI 0.104.1 (API framework)
- Pydantic 2.5.0 (validation, OpenAPI generation)
- OpenAI 1.3.7 (GPT-4o-mini for technique validation)
- Uvicorn (ASGI server)
- HTTPX (async HTTP client)

**Storage**: In-memory for MVP (technique taxonomy as static config, no database)  
**Testing**: pytest with async support, contract testing for API endpoints  
**Target Platform**: Railway (Docker deployment with embedding server + API service)  
**Project Type**: Web service (backend only, server-to-server API)

**Performance Goals**:
- Academic papers (10,000 words): <10 seconds per paper
- Short-form content (tweets): <5 seconds per post
- Batch of 100 mixed items: <5 minutes total
- 85%+ precision across all content types

**Constraints**:
- English-only content (reject non-English with HTTP 400)
- Hard global rate limit: 100 batches/hour shared across all API keys
- Server-to-server authentication only (API keys in env vars, never client-side)
- Must handle partial failures gracefully (process remaining items if one fails)
- Deterministic output (same input → same techniques extracted)

**Scale/Scope**:
- Initial taxonomy: ~50 known techniques
- Expected daily volume: 1,000-10,000 papers/day
- Batch size: Up to 1,000 items
- Cost target: <$0.0001 per item for batches of 100+

## Constitution Check

**GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.**

### Principle I: Async-First Job Processing
- ✅ **Applies**: Batch processing may take 5+ minutes for 100 items
- **Implementation**: 
  - POST /extract/techniques returns job_id immediately
  - Background task processes batch using `asyncio.create_task()`
  - GET /jobs/{job_id} for status polling
  - Embedding server calls use async httpx.AsyncClient
  - No blocking operations in request handlers

### Principle II: Deterministic Multi-Pass Detection
- ✅ **Applies with Bounded Non-Determinism Allowance**: Constitution explicitly permits BERTrend's stochastic clustering (see Principle II amendment)
- **Implementation**: 
  - Topic clustering via BERTrend has acceptable stochastic elements (HDBSCAN random initialization)
  - Final technique mapping is deterministic (exact match + LLM validation with fixed prompts)
  - Technique names MUST match exactly (100% reproducible)
  - Confidence scores may vary ±0.05 due to topic cluster variations
  - Set random seeds where possible for test reproducibility
- **Validation**: T044 tests same papers 3x, verifies technique names exact match, confidence ±0.05 (aligns with SC-006)

### Principle III: Constitution-Guided Filtering
- ❌ **Does Not Apply**: This service extracts techniques, does not filter by constitution
- **Note**: Constitution filtering happens in downstream Trend Analyzer

### Principle IV: OpenAPI-First Design
- ✅ **Applies Fully**: 
  - All endpoints defined with FastAPI decorators
  - Pydantic models for request/response with Field(description=..., example=...)
  - Interactive docs at /docs and /redoc
  - Examples for all endpoints including error responses (400, 429, 500)

### Principle V: Three-Tier Error Classification
- ✅ **Applies Fully**:
  - **Tier 1 Expected**: No techniques found (confidence <0.6), return empty list
  - **Tier 2 Retriable**: Embedding server timeout (retry 3x with backoff), LLM rate limit (respect retry-after)
  - **Tier 3 Non-Retriable**: Non-English content (400 error), malformed JSON, API auth failure

### Principle VI: Graceful Degradation & Resilience
- ✅ **Applies Fully**:
  - Batch with 1 failed item → process remaining 99, return partial success
  - Low confidence techniques (<0.6) → still return with warning flag
  - Embedding server down → return 503 with retry-after, don't crash
  - LLM unavailable → fall back to keyword matching only

### Principle VII: Railway Deployment Standards
- ✅ **Applies Fully**:
  - Multi-stage Dockerfile (builder + runtime)
  - Health check at /health responding <100ms
  - Non-root user (appuser)
  - PORT environment variable via ${PORT:-8001}
  - docker-compose for two-service setup (extraction + embedding)
  - Environment variables for all secrets (OPENAI_API_KEY, EMBEDDING_SERVER_URL)

**Constitution Compliance Summary**: 6 of 7 principles apply fully (including Principle II with bounded non-determinism allowance), 1 N/A (Principle III - constitution filtering occurs in downstream Trend Analyzer). All applicable principles will be implemented.

## Project Structure

### Documentation (this feature)

```text
specs/001-technique-extraction/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # BERTrend architecture research (Phase 0)
├── data-model.md        # Entity schemas (Phase 1)
├── contracts/           # API contracts (Phase 1)
│   └── openapi.yaml     # Generated OpenAPI spec
└── tasks.md             # Task breakdown (Phase 2 - /speckit.tasks)
```

### Source Code (repository root)

```text
# Two-service architecture
services/
└── technique-extraction/
    ├── Dockerfile                    # Multi-stage build
    ├── docker-compose.yml            # Extraction + Embedding services
    ├── railway.json                  # Railway deployment config
    ├── pyproject.toml                # Dependencies
    ├── .env.example                  # Environment variable template
    │
    ├── src/
    │   ├── main.py                   # FastAPI app entry point
    │   ├── config.py                 # Settings (Pydantic BaseSettings)
    │   │
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── endpoints.py          # API routes
    │   │   ├── models.py             # Request/response Pydantic models
    │   │   └── dependencies.py       # API key auth, rate limiting
    │   │
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── extraction_service.py # Orchestration (main extraction flow)
    │   │   ├── bertrend_service.py   # BERTrend wrapper (topic clustering)
    │   │   ├── embedding_client.py   # Async client for embedding server
    │   │   ├── technique_mapper.py   # Two-stage mapping (exact + LLM)
    │   │   └── language_detector.py  # English-only validation
    │   │
    │   ├── preprocessing/
    │   │   ├── __init__.py
    │   │   ├── academic.py           # Academic paper cleaning
    │   │   ├── social.py             # Social media cleaning (hashtags, mentions)
    │   │   ├── podcast.py            # Transcript cleaning (timestamps, filler)
    │   │   └── generic.py            # Generic text cleaning
    │   │
    │   ├── data/
    │   │   └── taxonomy.json         # Technique taxonomy (canonical names, aliases)
    │   │
    │   └── utils/
    │       ├── __init__.py
    │       ├── logging.py            # Structured JSON logging
    │       └── rate_limiter.py       # Global rate limiting logic
    │
    └── tests/
        ├── __init__.py
        ├── conftest.py               # Pytest fixtures
        ├── contract/
        │   └── test_api_contract.py  # OpenAPI compliance tests
        ├── integration/
        │   ├── test_extraction_flow.py  # End-to-end extraction
        │   └── test_source_types.py     # Academic, blog, social tests
        └── unit/
            ├── test_preprocessing.py
            ├── test_technique_mapper.py
            └── test_language_detector.py

# Embedding server (FastAPI wrapper around BERTrend, separate deployment)
services/
└── embedding-server/
    ├── app.py                        # FastAPI server exposing /health and /embed endpoints
    ├── start_server.py               # uvicorn launcher for FastAPI app
    ├── Dockerfile                    # BERTrend + GPU support for Railway
    └── config/                       # Optional: future BERTrend configs
        └── services_config.toml      # (reserved for advanced BERTrend settings)
```

**Structure Decision**: Two-service architecture is required because:
1. BERTrend embedding server runs separately (GPU-optimized, stateful cache)
2. Extraction service is stateless (can scale horizontally)
3. Separation allows independent scaling (multiple extraction instances → single embedding server)

## Implementation Phases

### Phase 0: Research & Design (Pre-Implementation)

**Goal**: Understand BERTrend architecture, validate technical approach, design data models

**Activities**:
1. Study BERTrend key files:
   - `bertrend/BERTrend.py` - Main orchestration class, `train_topic_models()` method
   - `bertrend/services/embedding_service.py` - Remote embedding server pattern
   - `bertrend/utils/data_loading.py` - Text preprocessing utilities
   - `bertrend/demos/weak_signals/app.py` - Production example
   - Configuration files: `services_default_config.toml`, `bertopic_default_config.toml`

2. Design data models (create data-model.md):
   - Paper entity (input)
   - EnrichedPaper entity (output with techniques)
   - BatchJob entity (job tracking)
   - TechniqueMatch entity (name + confidence)

3. Design API contracts (create contracts/openapi.yaml):
   - POST /extract/techniques (batch extraction)
   - GET /jobs/{job_id} (status polling)
   - GET /jobs/{job_id}/progress (real-time progress)
   - GET /health (health check)

4. Research BERTrend configuration for multi-source content:
   - HDBSCAN parameters for varied text lengths
   - UMAP dimensionality reduction settings
   - Document splitting strategy for long papers

**Deliverables**:
- research.md with BERTrend architecture notes
- data-model.md with entity schemas
- contracts/openapi.yaml with API specification

---

### Phase 1: Setup

**Goal**: Initialize project structure and basic dependencies.

**Tasks** (T001-T004 in tasks.md):

**T001**: Project setup and dependencies
- Initialize pyproject.toml with BERTrend, FastAPI, Pydantic, OpenAI
- Create docker-compose.yml for two services
- Configure .env.example with required environment variables
- Set up Railway.json with health check configuration

**T002-T004**: Additional setup tasks (see tasks.md for details)

---

### Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Core infrastructure that MUST be complete before ANY user story implementation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

**Tasks** (T005-T013 in tasks.md):

**T005-T007**: Embedding server setup (FastAPI wrapper around BERTrend)
- **Implementation Note**: BERTrend is a Python library, not a standalone server. We've created a FastAPI wrapper that exposes BERTrend's sentence-transformers embedding model via REST API.
- Create FastAPI app in `services/embedding-server/app.py` with endpoints: `/health`, `/embed`
- Implement start_server.py to launch FastAPI app with uvicorn on port 8765
- Create Dockerfile for deployment with BERTrend + GPU support
- Test: Embedding server responds to `/health` endpoint and can embed sample text via `/embed` endpoint

**T007-T009**: FastAPI application scaffold (extraction service)
- Create src/main.py with FastAPI app initialization
- Implement config.py with Pydantic BaseSettings (env var loading):
  ```python
  class Settings(BaseSettings):
      EMBEDDING_SERVER_URL: str
      OPENAI_API_KEY: str
      ALLOWED_API_KEYS: str  # Comma-separated
      DEFAULT_RATE_LIMIT: int = 100  # batches/hour
      LOG_LEVEL: str = "INFO"
      CONFIDENCE_THRESHOLD: float = 0.6  # Min confidence for techniques
      PORT: int = 8001
  ```
  - Techniques below CONFIDENCE_THRESHOLD marked with low_confidence=true flag
- Add /health endpoint (<100ms response, Railway requirement)
- Add CORS middleware if needed for local development
- Test: API starts successfully and /health returns 200

**T010**: Health check endpoint
- Add /health endpoint at /health in src/api/endpoints.py
- Ensure <100ms response (Railway requirement)
- Test: Health check responds quickly

**T011**: Embedding client (src/services/embedding_client.py)
- Implement async httpx.AsyncClient wrapper for embedding server
- Configure authentication (EMBEDDING_CLIENT_ID, EMBEDDING_CLIENT_SECRET)
- Add retry logic with exponential backoff for Tier 2 errors (timeout, 5xx)
- Add connection pooling for performance
- Test: Successfully embed 10 papers via remote server, handle timeout gracefully

**T012**: Technique taxonomy loading (src/data/taxonomy.json)
- Create JSON taxonomy with exactly 50 known techniques
  - **Schema**: 
    ```json
    {
      "technique_name": {
        "full_name": "Full Technique Name",
        "aliases": ["synonym1", "synonym-2", "abbreviation"],
        "category": "Architecture Patterns|Training Methods|Inference Optimization|...",
        "confidence_boost": 0.0,  // Optional: 0.0-0.1 for high-priority techniques
        "description": "Brief description for LLM context"  // Optional
      }
    }
    ```
  - Example: {"RAG": {"full_name": "Retrieval-Augmented Generation", "aliases": ["retrieval augmented", "rag system"], "category": "Architecture Patterns", "confidence_boost": 0.0}}
- Load taxonomy at startup into memory
- Test: Taxonomy loads correctly, all aliases normalized

**T013**: Structured JSON logging (src/utils/logging.py)
- Implement JSON formatter for production logs
- Include required fields: timestamp_iso8601, level, message, request_id, paper_id, source_type, duration_ms, technique_count, confidence metrics
- Never log API keys or full paper text
- Test: All operations log with structured context

**Checkpoint**: Foundation ready - embedding server operational, FastAPI scaffold running, core utilities available

---

### Phase 3: User Story 1 - Extract Techniques from Academic Papers (Priority: P1) 🎯 MVP

**Goal**: Implement end-to-end extraction pipeline for academic papers (highest quality source, 95%+ accuracy target).

**Why This Priority**: Academic papers are the foundation (95%+ accuracy target), longest content (10,000 words), and most complex preprocessing. Success here validates the architecture before adding complexity of other sources.

**Independent Test**: Submit 10 academic papers with known techniques, verify 85%+ identification rate with confidence >0.8, results returned in <60 seconds total.

**Tasks** (T014-T021 in tasks.md, now 12 tasks including T016a, T017a, T018a):

**T014**: Academic paper preprocessing (src/preprocessing/academic.py)
- Implement clean_academic() to remove references, LaTeX, equations
- Use BERTrend's split_data() for documents >50,000 words (split by paragraph)
- Handle common academic formats (abstract + body, sections)
- Test: 10,000-word paper cleans correctly, preserves technical content

**T015**: BERTrend service wrapper (src/services/bertrend_service.py)
- Initialize BERTrend with BERTopicModel configuration
  - HDBSCAN: min_cluster_size=5, min_samples=3 (for granular topics)
  - UMAP: n_neighbors=10, n_components=5
- Implement train_topic_models() call with embeddings from server
- Extract topic keywords using get_topics()
- Test: 20 academic papers cluster into 5-10 topics with meaningful keywords

**T016**: Two-stage technique mapper (src/services/technique_mapper.py)
- **Stage 1 - Exact Matching**: Match topic keywords against taxonomy aliases (fast, confidence=1.0)
- **Stage 2 - LLM Validation**: For ambiguous topics, call GPT-4o-mini with prompt:
  - "Topic keywords: {keywords}. Known techniques: {taxonomy}. Map to standardized names with confidence 0-1. Return only JSON."
- **Confidence Score Formula**:
  ```
  confidence_final = base_confidence × source_multiplier × frequency_boost
  
  Where:
  - base_confidence:
    - Stage 1 exact match: 1.0
    - Stage 2 LLM validation: raw LLM score (0.0-1.0)
  - source_multiplier (applied in T015):
    - academic: 1.0
    - blog: 0.95
    - press_release: 0.90
    - podcast: 0.85
    - social: 0.80
  - frequency_boost:
    - 1 mention: 1.0
    - 2-4 mentions: 1.1
    - 5+ mentions: 1.2 (capped at 1.2)
  
  Example: LLM match (0.7) in social media with 3 mentions:
    confidence = 0.7 × 0.80 × 1.1 = 0.616
  ```
- Combine results, de-duplicate, return top 5 per paper
- Test: "retrieval augmented" → "RAG" (exact match), "advanced search" → "RAG" (LLM, confidence 0.7)

**T016a**: Context detection (implements FR-014)
- Add context type detection via keyword matching (production/research/tutorial/criticism/general)
- Add context_type field to TechniqueMatch model

**T017**: Main extraction orchestration (src/services/extraction_service.py)
- Implement extract_techniques_sync() for single paper:
  1. Preprocess text (academic.py)
  2. Get embeddings (embedding_client.py)
  3. Cluster topics (bertrend_service.py)
  4. Map techniques (technique_mapper.py)
  5. Return EnrichedPaper with techniques[] and confidence scores
- Test: End-to-end extraction for 1 paper completes in <10 seconds

**T017a**: Text snippet extraction (implements FR-010)
- Capture 50-character context windows around technique mentions
- Store up to 3 snippets per technique with character offsets

**T018**: Pydantic request/response models (src/api/models.py)
- Define Paper, EnrichedPaper, TechniqueMatch with Field(description=..., example=...)
- Include all required fields for OpenAPI generation

**T018a**: Expected accuracy indicators (implements FR-016)
- Add expected_accuracy field to EnrichedPaper model
- Auto-calculate from source_type (academic=0.95, blog=0.90, etc.)

**T019**: API endpoint - POST /extract/techniques (synchronous first)
- Implement endpoint calling extraction_service for each paper
- Add Field(description=..., example=...) for OpenAPI
- Test: API accepts 10 papers, returns enriched results with techniques

**T020**: Error handling and three-tier classification
- Implement three-tier error classification:
  - Tier 1: No techniques found → return empty list, log DEBUG
  - Tier 2: Embedding server timeout → retry 3x, log WARNING
  - Tier 3: Malformed input → return 400 error, log ERROR
- Test: Malformed paper rejected with 400, timeout retried 3x before failing

**T021**: End-to-end validation
- Submit 10 academic papers, verify techniques extracted with >85% precision, <10 seconds per paper

**Checkpoint**: User Story 1 fully functional and testable independently - academic papers extract techniques accurately

---

### Phase 4 & 5: Multi-Source Support (User Stories 2 & 3 - P2, P3)

**Goal**: Extend pipeline to handle industry content (blogs, press releases) and social media with source-specific preprocessing and confidence adjustment.

**Note**: See tasks.md for detailed task breakdown. Tasks T022-T031 cover User Stories 2 and 3.

**Why This Priority**: User Stories 2 and 3 build on academic foundation. Industry content (P2) has medium complexity, social media (P3) has lowest accuracy expectations. Implement in order of decreasing data quality.

**Independent Test**: Submit mixed batch of 30 blogs, 10 press releases, 100 social posts. Verify appropriate accuracy per source type (90% blog, 85% press, 70% social), all complete successfully.

#### Key Tasks (see tasks.md T022-T031 for full details):

**T022-T023** (User Story 2): Industry content preprocessing
- Generic preprocessing for blogs and press releases
- Source-specific confidence adjustment

**T024-T026** (User Story 2): Integration and validation
- Source router for content types
- Endpoint updates
- Validation of industry content extraction

**T027-T028** (User Story 3): Social media and podcast preprocessing  
- Social media cleaning (hashtags, mentions, URLs)
- Podcast transcript cleaning (timestamps, filler words)

**T029-T031** (User Story 3): Confidence and validation
- Confidence multipliers by source:
  - Academic: 1.0 (no adjustment)
  - Blog: 0.95
  - Press Release: 0.90
  - Podcast: 0.85
  - Social Media: 0.80
- Source routing and validation

**Checkpoint**: User Stories 2 AND 3 complete - all source types process correctly with appropriate accuracy per source type.

---

### Phase 6: User Story 4 - Cross-Source Batch Processing (Priority: P4)

**Goal**: Enable async batch processing with mixed content types, partial failure handling, and job tracking.

**Independent Test**: Submit mixed batch of 85 items (20 papers, 50 social, 10 blogs, 5 press), all process successfully, complete in <5 minutes.

**Tasks** (T032-T037 in tasks.md): Batch processing, duplicate detection, async job pattern, status/progress endpoints

**Checkpoint**: All user stories functional - production-ready extraction with async batch processing.

---

### Phase 7: Production Hardening & Cross-Cutting Concerns

**Goal**: Meet constitution quality gates - rate limiting, authentication, OpenAPI compliance, monitoring, error resilience.

**Why This Priority**: Core extraction works (Phases 1-6), now make production-ready for deployment.

**Tasks** (T038-T058 in tasks.md, 22 tasks total):

**Security & Rate Limiting** (T038-T040):
- API key authentication (X-API-Key header, server-to-server only)
- Global rate limiter (100 batches/hour, sliding window)
- Rate limit reset validation (T039a)
- Language detection (fasttext ≥0.8 confidence, English-only)

**Documentation & Monitoring** (T041-T044):
- Newly discovered technique flagging
- OpenAPI documentation enhancements (examples, error responses)
- Health check optimization (<100ms response)
- Quasi-deterministic processing validation

**Deployment** (T045-T051):
- Multi-stage Dockerfile (builder + runtime, non-root user)
- docker-compose.yml (extraction + embedding services)
- railway.json (health check, no startCommand)
- Environment variable documentation
- Railway deployment (embedding server with GPU, extraction service)
- End-to-end integration test on Railway

**Validation & Monitoring** (T052-T058):
- Performance validation (academic <10s, blog <5s, social <5s, batch <5min)
- Accuracy validation per source type (academic 95%, blog 90%, press 85%, podcast 80%, social 70%)
- Prometheus metrics export
- Cost monitoring (<$0.0001 per paper for batches)
- Quickstart validation
- New technique discovery rate validation (T057: ≥5 per 1K docs)
- Error reporting latency validation (T058: <30 seconds)

**Checkpoint**: Service is production-ready with auth, rate limiting, monitoring, error handling, graceful degradation, and Railway deployment. All 7 phases complete. System ready for production use.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Two separate services (extraction + embedding) | BERTrend embedding server is GPU-optimized, stateful cache, runs independently | Embedding in extraction service would require GPU for every API instance, not cost-effective |
| Non-deterministic topic clustering | BERTrend's HDBSCAN has stochastic elements (random initialization) | Fully deterministic clustering (k-means) produces lower quality topics, loses semantic relationships |
| Async batch processing with job_id | 100-paper batch takes 5 minutes, can't block HTTP request | Synchronous processing would timeout Railway/client connections, poor UX |

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 0 (Research)**: No dependencies - start immediately (optional, creates data-model.md, contracts/)
- **Phase 1 (Setup)**: No dependencies - start immediately (T001-T004)
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - **BLOCKS all user stories** (T005-T013)
- **Phase 3 (User Story 1 - MVP)**: Depends on Phase 2 - No dependencies on other stories (T014-T021)
- **Phase 4 & 5 (User Stories 2 & 3)**: Depends on Phase 2 - Can integrate with US1 but independently testable (T022-T031)
- **Phase 6 (User Story 4)**: Depends on US1, US2, US3 (needs all source types) - Orchestrates batch processing (T032-T037)
- **Phase 7 (Production)**: Depends on Phase 6 completion - Adds security, deployment, monitoring (T038-T058)

### Critical Path Summary

**See tasks.md for detailed dependency breakdown and parallel execution opportunities.**

Key points:
- Phase 2 (Foundational) MUST complete before ANY user story work
- User Stories 1, 2, 3 can be developed/tested independently after Phase 2
- User Story 4 requires US1-3 complete (needs all source types)
- 20+ tasks can run in parallel (marked [P] in tasks.md)
- Each user story is independently testable with specific success metrics

## Success Criteria Mapping

| Success Criterion | Implementation Phase | Validation Task |
|-------------------|---------------------|-----------------|
| SC-001: 85%+ precision across all content types | Phase 4 & 5 | T053 (accuracy validation) |
| SC-002: 100% submitted content processed | Phase 6 | T032 (partial failure handling) |
| SC-003: Short-form <5 seconds | Phase 7 | T052 (performance validation) |
| SC-004: Long-form <10 seconds | Phase 3 | T021, T052 (validation) |
| SC-005: 100 items in <5 minutes | Phase 6 | T037 (integration test) |
| SC-006: Quasi-deterministic output (technique names exact, confidence ±0.05) | Phase 7 | T044 (quasi-deterministic validation) |
| SC-007: 90% match taxonomy names | Phase 3 | T016 (technique mapper) |
| SC-008: 5 new techniques per 1,000 docs | Phase 7 | T041, T057 (flagging + validation) |
| SC-009: Confidence >0.8 = >90% accuracy | Phase 3 | T016 (confidence formula) |
| SC-010: <$0.0001 per item | Phase 7 | T055 (cost monitoring) |
| SC-011: 1,000 items no degradation | Phase 7 | T052 (performance validation) |
| SC-012: Errors reported <30 seconds | Phase 3, 7 | T020, T058 (error handling + validation) |

## Next Steps

1. ✅ Spec completed and clarified
2. ✅ Tasks generated (tasks.md with 63 tasks organized by user story)
3. ✅ Constitution updated (Principle II allows bounded non-determinism for BERTrend)
4. ✅ Specification analysis complete (all CRITICAL and HIGH issues resolved)
5. **Next**: Execute Phase 0 research (optional, create data-model.md and contracts/openapi.yaml)
6. **Then**: Begin implementation:
   - Phase 1: Setup (T001-T004) 
   - Phase 2: Foundational (T005-T013) - **BLOCKS all user stories**
   - Phase 3: User Story 1 MVP (T014-T021) - Academic papers only
   - Validate MVP independently before proceeding to other phases

**Estimated Timeline**: 4 weeks (Phase 1-2: 1 week, Phase 3: 1 week, Phases 4-5: 1 week, Phases 6-7: 1 week)

**Risk Mitigation**:
- BERTrend learning curve → Phase 0 research mitigates
- Non-determinism concerns → Document acceptable variation, set random seeds
- Embedding server availability → Health check monitoring, 503 responses
- Cost overruns → Monitor per-paper cost daily, alert on threshold

---

**Plan Status**: ✅ Complete and aligned with tasks.md (63 tasks across 7 phases)  
**Constitution Compliance**: 6/7 principles fully implemented (Principle II updated for bounded non-determinism)  
**User Stories Covered**: All 4 (P1-P4) with independent test criteria  
**Phase Organization**: Setup → Foundational → US1 (MVP) → US2-3 → US4 → Production
**Documentation Status**: Constitution updated, spec enhanced with all medium-value fixes, tasks.md complete with 63 tasks

