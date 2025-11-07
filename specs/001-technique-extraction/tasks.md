# Tasks: AI Technique Extraction Service

**Input**: Design documents from `/specs/001-technique-extraction/`  
**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: No explicit test tasks included (not requested in specification). Tasks focus on implementation with inline testing validation.

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Two-service architecture**: `services/technique-extraction/` and `services/embedding-server/`
- Paths shown assume repository root, adjust based on actual structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md at services/technique-extraction/
- [x] T002 Initialize pyproject.toml with dependencies (BERTrend 0.1.0, FastAPI 0.104.1, Pydantic 2.5.0, OpenAI 1.3.7, httpx, uvicorn)
- [x] T003 [P] Create .env.example with required environment variables (EMBEDDING_SERVER_URL, OPENAI_API_KEY, ALLOWED_API_KEYS, DEFAULT_RATE_LIMIT, LOG_LEVEL)
- [x] T004 [P] Configure .gitignore for Python (.venv, __pycache__, .env, *.pyc)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create FastAPI embedding server wrapper in services/embedding-server/app.py exposing BERTrend's embedding model via REST API (endpoints: /health, /embed) using sentence-transformers with GPU support
- [x] T006 Implement embedding server launcher in services/embedding-server/start_server.py to start FastAPI app with uvicorn on port 8765
- [x] T007 [P] Create embedding server Dockerfile in services/embedding-server/Dockerfile with BERTrend + GPU support for Railway deployment
- [x] T008 [P] Create FastAPI application entry point in services/technique-extraction/src/main.py
- [x] T009 [P] Implement settings configuration in services/technique-extraction/src/config.py using Pydantic BaseSettings
- [x] T010 Add health check endpoint at /health in services/technique-extraction/src/api/endpoints.py (Railway requirement: <100ms response)
- [x] T011 [P] Implement async embedding client wrapper in services/technique-extraction/src/services/embedding_client.py with retry logic (httpx.AsyncClient, exponential backoff)
- [x] T012 Load technique taxonomy from services/technique-extraction/src/data/taxonomy.json with ~50 known techniques (structure: name, full_name, aliases, category)
- [x] T013 [P] Implement structured JSON logging in services/technique-extraction/src/utils/logging.py with required fields: timestamp_iso8601, level, message, request_id (UUID), paper_id, source_type, duration_ms, technique_count, confidence_avg, confidence_min, confidence_max, error_type (if failed), error_message (if failed), job_id (if batch), phase (preprocess/embed/cluster/map) - never log API keys or full paper text (log title+id only) - implements FR-019

**Checkpoint**: Foundation ready - embedding server operational, FastAPI scaffold running, core utilities available

---

## Phase 3: User Story 1 - Extract Techniques from Academic Papers (Priority: P1) 🎯 MVP

**Goal**: Implement end-to-end extraction pipeline for academic papers (highest quality source, 95%+ accuracy target)

**Independent Test**: Submit 10 academic papers with known techniques, verify 85%+ identification with confidence >0.8, results in <60 seconds

### Implementation for User Story 1

- [x] T014 [P] [US1] Implement academic paper preprocessing in services/technique-extraction/src/preprocessing/academic.py (remove references, LaTeX, equations; use BERTrend split_data for >50k words)
- [x] T015 [P] [US1] Create BERTrend service wrapper in services/technique-extraction/src/services/bertrend_service.py (initialize BERTopicModel with HDBSCAN min_cluster_size=5, UMAP n_neighbors=10)
- [x] T016 [US1] Implement two-stage technique mapper in services/technique-extraction/src/services/technique_mapper.py (Stage 1: exact keyword matching against taxonomy; Stage 2: GPT-4o-mini LLM validation for ambiguous topics)
- [x] T016a [US1] Implement context detection in services/technique-extraction/src/services/technique_mapper.py (detect context type via keyword matching: production=['production', 'deployed', 'live', 'released'], research=['study', 'experiment', 'investigate', 'paper'], tutorial=['tutorial', 'guide', 'how-to'], criticism=['failed', 'problem', 'issue'] - add context_type field to TechniqueMatch: production/research/tutorial/criticism/general - implements FR-014)
- [x] T017 [US1] Create main extraction orchestration in services/technique-extraction/src/services/extraction_service.py implementing extract_techniques_sync() (preprocess → embed → cluster → map → return EnrichedPaper)
- [x] T017a [US1] Implement text snippet extraction in services/technique-extraction/src/services/extraction_service.py (capture 50-character context windows around technique mentions - extract ±25 chars around each keyword match - store up to 3 snippets per technique as text_snippets[] in TechniqueMatch with format: {snippet: str, start_char: int, end_char: int} - implements FR-010 traceability requirement)
- [x] T018 [US1] Define Pydantic request/response models in services/technique-extraction/src/api/models.py (Paper, EnrichedPaper, TechniqueMatch with Field(description, example))
- [x] T018a [US1] Add expected_accuracy field to EnrichedPaper model in services/technique-extraction/src/api/models.py (calculate from source_type: academic=0.95, blog=0.90, press_release=0.85, podcast=0.80, social=0.70 - use Pydantic field_validator to auto-calculate based on source_type - implements FR-016 accuracy indicator requirement)
- [x] T019 [US1] Implement POST /extract/techniques endpoint in services/technique-extraction/src/api/endpoints.py calling extraction_service for synchronous processing
- [x] T020 [US1] Add three-tier error classification in extraction flow (Tier 1: no techniques found → empty list; Tier 2: embedding timeout → retry 3x; Tier 3: malformed input → 400 error)
- [x] T021 [US1] Validate end-to-end extraction: submit 10 academic papers, verify techniques extracted with >85% precision, <10 seconds per paper

**Checkpoint**: User Story 1 fully functional and testable independently - academic papers extract techniques accurately

---

## Phase 4: User Story 2 - Extract Techniques from Industry Content (Priority: P2)

**Goal**: Extend pipeline to handle blogs and press releases with source-specific preprocessing

**Independent Test**: Submit 30 blogs + 10 press releases, verify 80%+ accuracy, complete in <2 minutes

### Implementation for User Story 2

- [ ] T022 [P] [US2] Implement generic content preprocessing in services/technique-extraction/src/preprocessing/generic.py for blogs and press releases (remove HTML, marketing boilerplate, normalize whitespace)
- [ ] T023 [US2] Add source-specific confidence adjustment to technique_mapper.py (apply multipliers: academic=1.0, blog=0.95, press=0.90)
- [ ] T024 [US2] Implement source router in extraction_service.py to route by source_type (academic → academic.py, blog/press → generic.py)
- [ ] T025 [US2] Update POST /extract/techniques endpoint to accept source_type field and handle industry content
- [ ] T026 [US2] Validate industry content extraction: submit 30 blogs + 10 press releases, verify 80%+ accuracy, appropriate confidence scoring

**Checkpoint**: User Stories 1 AND 2 both work independently - academic + industry content processing

---

## Phase 5: User Story 3 - Process Social Media for Early Signals (Priority: P3)

**Goal**: Add social media and podcast support with low-quality content handling

**Independent Test**: Submit 100 social posts, verify 70%+ accuracy, handle 280-char content, complete in <90 seconds

### Implementation for User Story 3

- [ ] T027 [P] [US3] Implement social media preprocessing in services/technique-extraction/src/preprocessing/social.py (remove hashtags, @mentions, URLs, emojis; filter <10 word posts)
- [ ] T028 [P] [US3] Implement podcast transcript preprocessing in services/technique-extraction/src/preprocessing/podcast.py (remove timestamps, filler words, speaker labels; chunk if >50k words)
- [ ] T029 [US3] Extend confidence adjustment in technique_mapper.py to include podcast=0.85 and social=0.80 multipliers
- [ ] T030 [US3] Update source router in extraction_service.py to handle social and podcast source types
- [ ] T031 [US3] Validate social media extraction: submit 100 social posts, verify 70%+ accuracy, confidence reflects content quality

**Checkpoint**: User Stories 1, 2, AND 3 all work independently - full multi-source support operational

---

## Phase 6: User Story 4 - Cross-Source Batch Processing (Priority: P4)

**Goal**: Enable async batch processing with mixed content types, partial failure handling, and job tracking

**Independent Test**: Submit mixed batch of 85 items (20 papers, 50 social, 10 blogs, 5 press), all process successfully, complete in <5 minutes

### Implementation for User Story 4

- [ ] T032 [US4] Implement batch processing with partial failure handling in extraction_service.py using process_batch() (asyncio.gather with return_exceptions=True, collect successes and errors separately)
- [ ] T033 [US4] Implement duplicate detection in extraction_service.py using SHA-256 hash of normalized text (hash = SHA-256(full_text.strip().lower().encode('utf-8'))) - process unique content once, return duplicate_of field with original paper_id for duplicates - if hash collision detected (same hash, different titles), process both and flag with potential_duplicate=true for manual review - implements FR-018
- [ ] T034 [US4] Convert POST /extract/techniques to async job pattern (return job_id immediately, background task with asyncio.create_task, store job status in memory)
- [ ] T035 [US4] Add GET /jobs/{job_id} endpoint in endpoints.py for job status polling (status, progress, results when complete)
- [ ] T036 [P] [US4] Add GET /jobs/{job_id}/progress endpoint in endpoints.py for real-time progress tracking (items_completed/total_items)
- [ ] T037 [US4] Validate cross-source batch processing: submit 85 mixed items, verify all sources process correctly, handle duplicates, complete in <5 minutes

**Checkpoint**: All user stories functional - production-ready extraction with async batch processing

---

## Phase 7: Production Hardening & Cross-Cutting Concerns

**Purpose**: Security, rate limiting, deployment, monitoring - affects all user stories

- [ ] T038 [P] Implement API key authentication in services/technique-extraction/src/api/dependencies.py with verify_api_key() dependency (check X-API-Key header, return 401 if invalid)
- [ ] T039 [P] Implement global rate limiter in services/technique-extraction/src/utils/rate_limiter.py (hard limit 100 batches/hour, return 429 with Retry-After header)
- [ ] T039a Validate rate limit reset behavior (test rate limiter resets counter after 1 hour - submit 100 batches successfully, wait 1 hour, verify 101st request in new hour succeeds instead of 429 - validates FR-002 hourly reset requirement and sliding window behavior)
- [ ] T040 [P] Implement language detection in services/technique-extraction/src/services/language_detector.py using fasttext with ≥0.8 confidence threshold (reject non-English with HTTP 400, include language_detected and confidence in error - code-switched text >30% non-English rejected - non-English proper nouns permitted - implements FR-004)
- [ ] T041 [P] Add newly discovered technique flagging in technique_mapper.py (set newly_discovered=true if not in canonical taxonomy)
- [ ] T042 Add OpenAPI documentation enhancements to all endpoints (Field(description, example) for all models, error response examples for 400/401/429/500/503)
- [ ] T043 Optimize health check in endpoints.py (ensure <100ms response, include embedding_server_reachable status)
- [ ] T044 Validate quasi-deterministic processing (test same 10 papers 3x, verify technique names match exactly and confidence scores within ±0.05 absolute difference - aligns with Constitution Principle II bounded non-determinism allowance and SC-006)
- [ ] T045 Create multi-stage Dockerfile in services/technique-extraction/Dockerfile (builder stage with venv, runtime stage with non-root user appuser, CMD with shell form for ${PORT:-8001})
- [ ] T046 Create docker-compose.yml at services/ defining extraction-service (port 8001) and embedding-server (port 8765) with depends_on and environment variables
- [ ] T047 Create railway.json in services/technique-extraction/ (builder: DOCKERFILE, healthcheckPath: /health, healthcheckTimeout: 100, NO startCommand)
- [ ] T048 Document all environment variables in .env.example with descriptions and examples
- [ ] T049 [P] Deploy embedding server to Railway as separate service with GPU support and persistent volume for cache
- [ ] T050 Deploy extraction service to Railway pointing to embedding server URL, configure horizontal scaling
- [ ] T051 Run end-to-end integration test on Railway deployment (submit mixed 85-item batch, verify all processing correctly)
- [ ] T052 [P] Validate performance targets (academic <10s, blog <5s, social <5s, batch of 100 in <5min)
- [ ] T053 [P] Validate accuracy targets per source type using hand-labeled test set (academic 95%, blog 90%, press 85%, podcast 80%, social 70%)
- [ ] T054 [P] Set up Prometheus metrics export (extraction_requests_total, extraction_duration_seconds, techniques_extracted_total, confidence_scores_histogram, llm_api_calls_total)
- [ ] T055 [P] Monitor cost per paper (target <$0.0001 for batches of 100+, alert if exceeds $0.0002)
- [ ] T056 Run quickstart validation (follow README instructions, verify service starts and processes sample batch correctly)
- [ ] T057 Validate new technique discovery rate (process 1,000-document test set, verify ≥5 techniques flagged with newly_discovered=true - validates SC-008 discovery rate requirement - if rate <5, review taxonomy coverage or detection sensitivity)
- [ ] T058 Validate error reporting latency (submit batch with 1 malformed paper triggering immediate validation error, verify error response returned within 30 seconds of submission - validates SC-012 error reporting SLA - measure from POST request to error in response)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - Can integrate with US1 but independently testable
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) - Can integrate with US1/US2 but independently testable
- **User Story 4 (Phase 6)**: Depends on US1, US2, US3 (needs all source types working) - Orchestrates batch processing across sources
- **Production Hardening (Phase 7)**: Depends on US4 completion - Adds security, deployment, monitoring to complete system

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (MVP)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 preprocessing but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1/US2 preprocessing but independently testable
- **User Story 4 (P4)**: Requires US1, US2, US3 complete - Integrates all source types into batch processing

### Within Each User Story

**User Story 1 (Academic Papers)**:
- T014, T015 can run in parallel (preprocessing + BERTrend setup, different files)
- T016 depends on T015 (technique mapper needs BERTrend topics)
- T017 depends on T014, T016 (orchestration needs preprocessing + mapping)
- T018, T019 depend on T017 (API models + endpoints need extraction service)
- T020, T021 depend on T019 (error handling + validation wrap endpoint)

**User Story 2 (Industry Content)**:
- T022 can run in parallel with US1 if capacity allows (independent preprocessing)
- T023, T024 depend on T022 (confidence adjustment + routing need preprocessing)
- T025 depends on T024 (endpoint update needs routing)
- T026 depends on T025 (validation needs complete implementation)

**User Story 3 (Social Media)**:
- T027, T028 can run in parallel (social + podcast preprocessing, different files)
- T029, T030 depend on T027, T028 (confidence + routing need preprocessing)
- T031 depends on T030 (validation needs complete implementation)

**User Story 4 (Batch Processing)**:
- T032, T033 can run in parallel (batch processing + duplicate detection, different concerns)
- T034 depends on T032 (async jobs need batch processing working)
- T035, T036 can run in parallel (status + progress endpoints, different endpoints)
- T037 depends on T035, T036 (validation needs complete async implementation)

### Parallel Opportunities

- **Setup tasks**: T003, T004 can run in parallel (env file + gitignore, no dependencies)
- **Foundational tasks**: T007, T009, T013 can run in parallel (config files, different concerns)
- **US1 preprocessing + BERTrend**: T014, T015 in parallel (different subsystems)
- **US2 preprocessing**: T022 can run before US1 completes (independent preprocessing code)
- **US3 preprocessing**: T027, T028 in parallel (social + podcast, different files)
- **US4 core logic**: T032, T033 in parallel (batch + duplicates, different concerns)
- **Production tasks**: T038, T039, T040, T041, T054, T055 in parallel (independent features)

---

## Parallel Example: User Story 1

```bash
# Launch preprocessing and BERTrend setup together:
Task T014: "Implement academic preprocessing in src/preprocessing/academic.py"
Task T015: "Create BERTrend service wrapper in src/services/bertrend_service.py"

# Both can proceed simultaneously (different files, no shared dependencies)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T013) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T014-T021)
4. **STOP and VALIDATE**: Test academic paper extraction independently
5. Deploy/demo if ready (minimal viable product for academic papers)

### Incremental Delivery

1. **Foundation**: Setup + Foundational (T001-T013) → Foundation ready
2. **MVP**: Add User Story 1 (T014-T021) → Test independently → Deploy/Demo (academic papers only!)
3. **Expand**: Add User Story 2 (T022-T026) → Test independently → Deploy/Demo (+ industry content)
4. **Broaden**: Add User Story 3 (T027-T031) → Test independently → Deploy/Demo (+ social media)
5. **Integrate**: Add User Story 4 (T032-T037) → Test independently → Deploy/Demo (batch processing across all sources)
6. **Harden**: Add Production (T038-T056) → Final deployment with security, monitoring, full Railway setup

Each increment adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T013)
2. Once Foundational is done:
   - Developer A: User Story 1 (T014-T021)
   - Developer B: User Story 2 preprocessing (T022) in parallel
   - Developer C: User Story 3 preprocessing (T027-T028) in parallel
3. Stories complete and integrate incrementally

---

## Task Summary

**Total Tasks**: 63  
**Setup (Phase 1)**: 4 tasks  
**Foundational (Phase 2)**: 9 tasks (includes T013 comprehensive logging)  
**User Story 1 (Phase 3)**: 12 tasks (includes T016a context detection, T017a snippet extraction, T018a accuracy indicators)  
**User Story 2 (Phase 4)**: 5 tasks  
**User Story 3 (Phase 5)**: 5 tasks  
**User Story 4 (Phase 6)**: 6 tasks (includes T033 enhanced duplicate detection)  
**Production & Polish (Phase 7)**: 22 tasks (includes T039a rate limit validation, T040 enhanced language detection, T057 discovery rate validation, T058 error latency validation)

**Parallel Opportunities**: 20+ tasks can run in parallel across different files/concerns  
**Independent Stories**: US1, US2, US3 can be developed and tested independently after Foundational phase  
**Blocking Prerequisites**: 9 foundational tasks must complete before any user story work begins

---

## Success Criteria Checkpoints

| User Story | Tasks | Independent Test | Success Metric |
|------------|-------|------------------|----------------|
| **US1 (P1)** | T014-T021 (12 tasks) | 10 academic papers | 85%+ precision, <60 sec, confidence >0.8 |
| **US2 (P2)** | T022-T026 | 30 blogs + 10 press | 80%+ accuracy, <2 min |
| **US3 (P3)** | T027-T031 | 100 social posts | 70%+ accuracy, <90 sec |
| **US4 (P4)** | T032-T037 | 85 mixed items | 100% processed, <5 min |

---

## Notes

- **[P] tasks**: Different files, no dependencies (safe to parallelize)
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Independently completable and testable after Foundational phase
- **MVP scope**: User Story 1 only (T001-T021) provides minimal viable product
- **Constitution compliance**: Quality gates enforced in Phase 7 (T038-T056)
- **Commit strategy**: Commit after each task or logical group for incremental progress
- **Stop at checkpoints**: Validate story independently before proceeding to next

---

**Format Validation**: ✅ ALL 63 tasks follow checklist format with checkbox, ID, optional [P]/[Story] labels, and file paths

