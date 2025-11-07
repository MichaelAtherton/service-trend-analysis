# Tasks: MVP Testing Procedures

**Input**: Design documents from `/specs/002-mvp-testing/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Test suite extends existing service: `services/technique-extraction/tests/`
- Fixtures: `services/technique-extraction/tests/fixtures/`
- Test utilities: `services/technique-extraction/tests/utils/`
- Reports: `services/technique-extraction/test-reports/` (gitignored)

---

## Phase 1: Setup (Test Infrastructure)

**Purpose**: Initialize test directory structure and configure pytest framework

- [x] T001 Create test directory structure: `services/technique-extraction/tests/` with subdirectories: `fixtures/`, `fixtures/papers/`, `utils/`
- [x] T002 Add test dependencies to `services/technique-extraction/pyproject.toml`: pytest, pytest-asyncio, pytest-html, pytest-json-report, httpx, openai
- [x] T003 Create `services/technique-extraction/pytest.ini` with asyncio_mode, markers (pipeline, error_handling, monitoring, taxonomy, slow), and report paths
- [x] T004 [P] Create `.env.test` template in `services/technique-extraction/.env.test.example` with OPENAI_API_KEY, EXTRACTION_SERVICE_URL, EMBEDDING_SERVER_URL placeholders
- [x] T005 [P] Update `.gitignore` to exclude `test-reports/`, `.env.test`, and pytest cache directories
- [ ] T006 Install test dependencies: `cd services/technique-extraction && pip install -e ".[test]"`

---

## Phase 2: Foundational (Test Fixtures & Utilities)

**Purpose**: Core test infrastructure that MUST be complete before ANY user story tests can be implemented

**⚠️ CRITICAL**: No user story test work can begin until this phase is complete

- [x] T007 Create pytest configuration fixture in `services/technique-extraction/tests/conftest.py` with session-scoped fixtures: `fixtures_dir`, `metadata`, `sample_papers`
- [x] T008 [P] Curate sample paper 1 (RAG): Find arXiv paper on Retrieval-Augmented Generation, save to `tests/fixtures/papers/paper_001_rag.txt`
- [x] T009 [P] Curate sample paper 2 (RLHF): Find paper on RLHF, save to `tests/fixtures/papers/paper_002_rlhf.txt`
- [x] T010 [P] Curate sample paper 3 (Fine-tuning): Find paper on LoRA/fine-tuning, save to `tests/fixtures/papers/paper_003_finetuning.txt`
- [x] T011 [P] Curate sample paper 4 (Transformers): Find paper on transformer architecture, save to `tests/fixtures/papers/paper_004_transformers.txt`
- [x] T012 [P] Curate sample paper 5 (Diffusion): Find paper on diffusion models, save to `tests/fixtures/papers/paper_005_diffusion.txt`
- [x] T013 [P] Curate sample paper 6 (Multi-modal): Find paper on multi-modal AI, save to `tests/fixtures/papers/paper_006_multimodal.txt`
- [x] T014 [P] Curate sample paper 7 (Quantization): Find paper on model compression, save to `tests/fixtures/papers/paper_007_quantization.txt`
- [x] T015 [P] Curate sample paper 8 (Prompt Engineering): Find paper/tutorial on prompting, save to `tests/fixtures/papers/paper_008_prompting.txt`
- [x] T016 [P] Curate sample paper 9 (Evaluation): Find paper on evaluation metrics, save to `tests/fixtures/papers/paper_009_evaluation.txt`
- [x] T017 [P] Curate sample paper 8 (Prompt Engineering): Find paper on prompt engineering, save to `tests/fixtures/papers/tutorial on prompting.txt`
- [x] T018 Manually label all 8 papers with expected techniques, context types, and confidence ranges (human expert review)
- [x] T019 Create `tests/fixtures/metadata.json` with all 8 papers' ground truth annotations following `contracts/sample-paper-schema.json`
- [ ] T020 Validate metadata.json against JSON schema: `jsonschema -i tests/fixtures/metadata.json tests/fixtures/contracts/sample-paper-schema.json`
- [x] T021 [P] Create API client helper in `tests/utils/api_client.py` with async functions for calling extraction endpoint, handling retries, and rate limits
- [x] T022 [P] Create custom assertions in `tests/utils/assertions.py` with functions: `assert_technique_extracted()`, `assert_extraction_accuracy()`, `assert_confidence_range()`
- [x] T023 [P] Create cost tracker in `tests/utils/cost_tracker.py` for monitoring OpenAI API usage (total calls, tokens, estimated cost)
- [x] T024 Add cost tracking fixture to `tests/conftest.py` with session-scoped tracker and end-of-session cost reporting
- [x] T025 Add OpenAI client fixture to `tests/conftest.py` with API key validation and skip logic if key not set
- [x] T026 Add paper-specific fixtures to `tests/conftest.py`: `rag_paper`, `rlhf_paper`, etc. for targeted test access

**Checkpoint**: Foundation ready - user story test implementation can now begin in parallel

---

## Phase 3: User Story 1 - Validate Core Extraction Pipeline (Priority: P1) 🎯 MVP

**Goal**: Verify that the AI Technique Extraction Service correctly processes academic papers end-to-end, achieving 85%+ technique identification accuracy and <10s processing time per paper

**Independent Test**: Submit 8 sample academic papers, verify 85%+ techniques identified with appropriate confidence scores, all processing <10s per paper

### Implementation for User Story 1

- [ ] T027 [P] [US1] Create `tests/test_pipeline.py` with imports, fixtures, and test class structure
- [ ] T028 [P] [US1] Implement `test_health_check()` in `tests/test_pipeline.py` to verify service is running before extraction tests
- [ ] T029 [US1] Implement `test_extraction_accuracy()` parametrized test in `tests/test_pipeline.py` for all 8 papers, asserting 85%+ technique identification rate
- [ ] T030 [US1] Implement `test_processing_time()` parametrized test in `tests/test_pipeline.py`, asserting each paper processes in <10 seconds
- [ ] T031 [US1] Implement `test_preprocessing_latex()` in `tests/test_pipeline.py` to verify LaTeX removal while preserving technical content
- [ ] T032 [US1] Implement `test_exact_technique_matching()` in `tests/test_pipeline.py` to verify Stage 1 exact matching returns base_confidence=1.0
- [ ] T033 [US1] Implement `test_context_detection()` in `tests/test_pipeline.py` to verify production/research/tutorial/criticism/general classification
- [ ] T034 [US1] Implement `test_snippet_extraction()` in `tests/test_pipeline.py` to verify 50-character context windows with accurate character offsets
- [ ] T035 [US1] Implement `test_confidence_scores()` in `tests/test_pipeline.py` to verify scores within expected ranges (±0.05 tolerance for BERTrend variation)
- [ ] T036 [US1] Implement `test_expected_accuracy_field()` in `tests/test_pipeline.py` to verify expected_accuracy calculated correctly based on source_type
- [ ] T037 [US1] Add pytest markers to all US1 tests: `@pytest.mark.pipeline` for filtering
- [ ] T038 [US1] Run User Story 1 tests locally and verify 100% pass rate: `pytest tests/test_pipeline.py -v -m pipeline`

**Checkpoint**: At this point, User Story 1 (core extraction validation) should be fully functional and independently testable

---

## Phase 4: User Story 2 - Verify Error Handling and Resilience (Priority: P2)

**Goal**: Confirm that the service gracefully handles error conditions according to the three-tier error classification system, ensuring production stability

**Independent Test**: Submit problematic inputs (empty text, timeout simulation, malformed JSON) and verify appropriate HTTP status codes (400 for Tier 3, 500 for Tier 2, 200 with empty list for Tier 1)

### Implementation for User Story 2

- [ ] T039 [P] [US2] Create `tests/test_error_handling.py` with imports, fixtures, and test class structure
- [ ] T040 [US2] Implement `test_tier1_empty_results()` in `tests/test_error_handling.py` to verify papers with no techniques return HTTP 200 with empty techniques array
- [ ] T041 [US2] Implement `test_tier1_no_error_logging()` in `tests/test_error_handling.py` to verify Tier 1 conditions log at DEBUG level, not ERROR
- [ ] T042 [US2] Implement `test_tier2_timeout_retry()` in `tests/test_error_handling.py` to verify embedding server timeout triggers 3 retries with exponential backoff
- [ ] T043 [US2] Implement `test_tier2_500_error()` in `tests/test_error_handling.py` to verify Tier 2 errors return HTTP 500 after retries exhausted
- [ ] T044 [US2] Implement `test_tier3_validation_error()` in `tests/test_error_handling.py` to verify text <50 characters returns HTTP 400 with clear error message
- [ ] T045 [US2] Implement `test_tier3_malformed_json()` in `tests/test_error_handling.py` to verify malformed request returns HTTP 422 with field-level errors
- [ ] T046 [US2] Implement `test_tier3_no_retry()` in `tests/test_error_handling.py` to verify Tier 3 errors do not trigger retry logic
- [ ] T047 [US2] Implement `test_partial_batch_failure()` in `tests/test_error_handling.py` to verify batch with 1 failed paper processes 9 successfully with error report
- [ ] T048 [US2] Implement `test_error_logging_context()` in `tests/test_error_handling.py` to verify error logs include request_id, paper_id, error_type, phase fields
- [ ] T049 [US2] Add pytest markers to all US2 tests: `@pytest.mark.error_handling`
- [ ] T050 [US2] Run User Story 2 tests locally and verify 100% pass rate: `pytest tests/test_error_handling.py -v -m error_handling`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Validate Service Health and Monitoring (Priority: P3)

**Goal**: Verify that the service provides health check endpoints and structured logging for monitoring, alerting, and debugging in production environments

**Independent Test**: Call GET `/api/v1/health` and verify <100ms response with status "healthy", review logs from sample extraction to confirm all required fields present in JSON format

### Implementation for User Story 3

- [ ] T051 [P] [US3] Create `tests/test_monitoring.py` with imports, fixtures, and test class structure
- [ ] T052 [US3] Implement `test_health_check_response_time()` in `tests/test_monitoring.py` to verify 100 consecutive `/health` calls respond in <100ms
- [ ] T053 [US3] Implement `test_health_check_schema()` in `tests/test_monitoring.py` to verify health response contains status, version, uptime_seconds, timestamp, service_name
- [ ] T054 [US3] Implement `test_health_check_status_codes()` in `tests/test_monitoring.py` to verify healthy service returns 200, unhealthy returns 503
- [ ] T055 [US3] Implement `test_structured_logging_fields()` in `tests/test_monitoring.py` to verify logs contain all required fields: timestamp_iso8601, level, message, request_id, paper_id, duration_ms, technique_count
- [ ] T056 [US3] Implement `test_logging_per_phase()` in `tests/test_monitoring.py` to verify logs include phase field (preprocess/embed/cluster/map) and request_id links all operations
- [ ] T057 [US3] Implement `test_logging_confidence_metrics()` in `tests/test_monitoring.py` to verify completion logs include confidence_avg, confidence_min, confidence_max
- [ ] T058 [US3] Implement `test_no_sensitive_data_in_logs()` in `tests/test_monitoring.py` to verify logs never contain API keys, passwords, or full paper text (only paper_id and title)
- [ ] T059 [US3] Implement `test_error_logging_format()` in `tests/test_monitoring.py` to verify error logs include error_type, error_message, phase where failure occurred
- [ ] T060 [US3] Implement `test_json_log_format()` in `tests/test_monitoring.py` to verify all logs are valid JSON and parseable
- [ ] T061 [US3] Add pytest markers to all US3 tests: `@pytest.mark.monitoring`
- [ ] T062 [US3] Run User Story 3 tests locally and verify 100% pass rate: `pytest tests/test_monitoring.py -v -m monitoring`

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Confirm Taxonomy and Confidence Scoring (Priority: P4)

**Goal**: Validate that the 50+ technique taxonomy is correctly loaded, exact matching works, LLM fallback activates for ambiguous cases, and confidence scores follow the documented formula

**Independent Test**: Submit papers with known technique frequencies and verify confidence scores increase with frequency and vary by source type according to the formula (base × source_multiplier × frequency_boost)

### Implementation for User Story 4

- [ ] T063 [P] [US4] Create `tests/test_taxonomy.py` with imports, fixtures, and test class structure
- [ ] T064 [US4] Implement `test_taxonomy_loading()` in `tests/test_taxonomy.py` to verify exactly 50+ techniques loaded from `src/data/taxonomy.json` with all required fields
- [ ] T065 [US4] Implement `test_exact_match_stage1()` in `tests/test_taxonomy.py` to verify exact alias matches return base_confidence=1.0 without LLM call
- [ ] T066 [US4] Implement `test_llm_fallback_stage2()` in `tests/test_taxonomy.py` to verify ambiguous keywords trigger Stage 2 LLM validation with confidence 0.0-1.0
- [ ] T067 [US4] Implement `test_confidence_formula_academic()` in `tests/test_taxonomy.py` to verify academic paper with 5+ mentions: 1.0 × 1.0 × 1.2 = 1.0 (capped)
- [ ] T068 [US4] Implement `test_confidence_formula_social()` in `tests/test_taxonomy.py` to verify social media with 1 mention: 1.0 × 0.80 × 1.0 = 0.80
- [ ] T069 [US4] Implement `test_frequency_boost_tiers()` in `tests/test_taxonomy.py` to verify frequency boosts: 1 mention=1.0, 2-4 mentions=1.1, 5+ mentions=1.2
- [ ] T070 [US4] Implement `test_source_multipliers()` in `tests/test_taxonomy.py` to verify source_type multipliers: academic=1.0, blog=0.95, press=0.90, podcast=0.85, social=0.80
- [ ] T071 [US4] Implement `test_confidence_capping()` in `tests/test_taxonomy.py` to verify final confidence scores capped at 1.0 (no values >1.0)
- [ ] T072 [US4] Implement `test_context_detection_accuracy()` in `tests/test_taxonomy.py` with 50 pre-labeled test cases, asserting 90%+ correct classification
- [ ] T073 [US4] Implement `test_newly_discovered_flagging()` in `tests/test_taxonomy.py` to verify techniques not in taxonomy have `newly_discovered=true` flag
- [ ] T074 [US4] Implement `test_openai_rate_limit_handling()` in `tests/test_taxonomy.py` to verify LLM validation handles 429 errors with exponential backoff
- [ ] T075 [US4] Implement `test_openai_cost_tracking()` in `tests/test_taxonomy.py` to verify cost tracker increments API calls and tokens correctly
- [ ] T076 [US4] Add pytest markers to all US4 tests: `@pytest.mark.taxonomy`
- [ ] T077 [US4] Run User Story 4 tests locally and verify 100% pass rate: `pytest tests/test_taxonomy.py -v -m taxonomy`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: CI/CD Integration and Polish

**Purpose**: Automate test execution in CI/CD pipeline and finalize documentation

- [ ] T078 [P] Create GitHub Actions workflow in `.github/workflows/mvp-tests.yml` with triggers for pull_request and push to main
- [ ] T079 [P] Configure workflow to install Python 3.11, test dependencies, and run pytest with HTML/JSON report generation
- [ ] T080 [P] Add workflow step to upload test reports as artifacts with 30-day retention
- [ ] T081 [P] Add workflow step to comment PR with test results summary (total/passed/failed/duration)
- [ ] T082 [P] Configure GitHub repository secret `OPENAI_API_KEY_TEST` for CI/CD test account
- [ ] T083 [P] Test GitHub Actions workflow by creating a test PR and verifying it runs successfully
- [ ] T084 [P] Update main README in `services/technique-extraction/README.md` with "Testing" section linking to quickstart.md
- [ ] T085 [P] Create troubleshooting guide in `services/technique-extraction/docs/TESTING_TROUBLESHOOTING.md` based on quickstart.md common issues
- [ ] T086 [P] Add test coverage reporting to workflow: install pytest-cov, run with --cov flag, generate HTML coverage report
- [ ] T087 Validate full test suite runs in <5 minutes: `pytest tests/ -v --html=test-reports/report.html --json-report`
- [ ] T088 Verify test reports generated in all three formats: console output visible, HTML report at test-reports/report.html, JSON at test-reports/report.json
- [ ] T089 Review HTML report for visual quality: summary dashboard, per-test details, collapsible failures, filter functionality
- [ ] T090 Validate cost tracking reports at end of test run: total API calls, input/output tokens, estimated cost displayed
- [ ] T091 Run full suite 3 times to verify quasi-deterministic behavior: technique names exact, confidence ±0.05 variation acceptable
- [ ] T092 Verify all 4 user stories can be tested independently: run each test module separately and confirm no cross-dependencies
- [ ] T093 Commit all test code, fixtures, and metadata to version control with meaningful commit messages per user story
- [ ] T094 Create git tag `v1.0.0-mvp-testing` for initial test suite release

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **CI/CD & Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Core Pipeline**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2) - Error Handling**: Can start after Foundational (Phase 2) - Independent of US1 but may reuse API client utilities
- **User Story 3 (P3) - Monitoring**: Can start after Foundational (Phase 2) - Independent of US1/US2, tests different aspects
- **User Story 4 (P4) - Taxonomy**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3, focuses on technique mapping

### Within Each User Story

- Fixtures and utilities before tests
- Core tests before edge case tests
- Independent test verification before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: T004, T005 can run in parallel (different files)
- **Foundational (Phase 2)**: T008-T017 (all paper curation) can run in parallel, T021-T023 (utilities) can run in parallel
- **User Story 1**: T027-T028 can run in parallel (different test functions), T029-T036 tests can be written in parallel after test file created
- **User Story 2**: T039-T049 tests can be written in parallel after test file created
- **User Story 3**: T051-T062 tests can be written in parallel after test file created
- **User Story 4**: T063-T077 tests can be written in parallel after test file created
- **CI/CD & Polish**: T078-T086 (documentation and workflow tasks) can run in parallel
- **All 4 user stories (Phase 3-6)** can be worked on in parallel by different team members after Foundational phase completes

---

## Parallel Example: User Story 1

```bash
# After T027 creates test_pipeline.py, launch all test implementations in parallel:
Task T029: "Implement test_extraction_accuracy() parametrized test"
Task T030: "Implement test_processing_time() parametrized test"
Task T031: "Implement test_preprocessing_latex()"
Task T032: "Implement test_exact_technique_matching()"
Task T033: "Implement test_context_detection()"
Task T034: "Implement test_snippet_extraction()"

# All can be written simultaneously in different parts of the test file
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T026) - **CRITICAL** - blocks all stories
3. Complete Phase 3: User Story 1 (T027-T038)
4. **STOP and VALIDATE**: Run `pytest tests/test_pipeline.py -v` and verify 100% pass
5. Generate reports and review HTML output
6. **MVP COMPLETE** - Core extraction pipeline validation ready

### Incremental Delivery

1. Complete Setup + Foundational (Phases 1-2) → Foundation ready
2. Add User Story 1 (Phase 3) → Test independently → **MVP delivered**
3. Add User Story 2 (Phase 4) → Test independently → Error handling validated
4. Add User Story 3 (Phase 5) → Test independently → Monitoring validated
5. Add User Story 4 (Phase 6) → Test independently → Taxonomy validated
6. Add CI/CD & Polish (Phase 7) → Automation complete
7. Each story adds validation coverage without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Phases 1-2)
2. Once Foundational is done:
   - Developer A: User Story 1 (core pipeline tests)
   - Developer B: User Story 2 (error handling tests)
   - Developer C: User Story 3 (monitoring tests)
   - Developer D: User Story 4 (taxonomy tests)
3. Stories complete and validate independently
4. Team collaborates on CI/CD & Polish (Phase 7)

---

## Task Summary

**Total Tasks**: 94

**Tasks per Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 20 tasks
- Phase 3 (User Story 1): 12 tasks
- Phase 4 (User Story 2): 12 tasks
- Phase 5 (User Story 3): 12 tasks
- Phase 6 (User Story 4): 15 tasks
- Phase 7 (CI/CD & Polish): 17 tasks

**Tasks per User Story**:
- US1 (Core Pipeline): 12 implementation tasks
- US2 (Error Handling): 12 implementation tasks
- US3 (Monitoring): 12 implementation tasks
- US4 (Taxonomy): 15 implementation tasks

**Parallel Opportunities**: 45 tasks marked [P] can be executed in parallel within their phases

**Independent Test Criteria**:
- US1: Run `pytest tests/test_pipeline.py -m pipeline -v` → 100% pass, 85%+ technique identification, <10s per paper
- US2: Run `pytest tests/test_error_handling.py -m error_handling -v` → 100% pass, all three error tiers validated
- US3: Run `pytest tests/test_monitoring.py -m monitoring -v` → 100% pass, health <100ms, logs structured
- US4: Run `pytest tests/test_taxonomy.py -m taxonomy -v` → 100% pass, 50+ techniques loaded, confidence formula validated

**Suggested MVP Scope**: Phases 1-3 (Setup + Foundational + User Story 1) = 38 tasks = Core extraction pipeline validation

**Estimated Effort**:
- MVP (Phases 1-3): 15-20 hours
- Full Suite (All phases): 25-35 hours
- CI/CD Integration: 2-3 hours
- Total: 27-38 hours

---

## Notes

- [P] tasks = different files, no dependencies, can execute in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each user story phase completion
- Stop at any checkpoint to validate story independently
- All tests validate existing service implementation (no new service features)
- Test suite is the implementation - there are no "tests for tests"
- OpenAI API costs: ~$0.001 per full suite run
- Expected first full run: ~4 minutes for 8 papers


