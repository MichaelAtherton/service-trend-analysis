# Feature Specification: MVP Testing Procedures

**Feature Branch**: `002-mvp-testing`  
**Created**: 2025-11-03  
**Status**: Draft  
**Input**: User description: "i need clear testing procedures for the completed mvp"

## Clarifications

### Session 2025-11-03

- Q: How should the test suite handle OpenAI API calls for LLM validation (Stage 2 technique mapping)? → A: Use real OpenAI API calls with a test account (costs money, slower, rate limits)
- Q: Where should the 8 sample academic papers with known AI techniques be stored for test validation? → A: Dedicated test data directory in the repository (e.g., tests/fixtures/papers/) for version control
- Q: Should the test suite run as part of CI/CD pipeline on every commit, or only manually triggered? → A: CI/CD on pull requests and main branch, manual for debugging (balanced approach)
- Q: How should the test suite report results - as console output, HTML report, JSON file, or multiple formats? → A: Multiple formats: console for CI/CD, HTML for manual review, JSON for automation

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate Core Extraction Pipeline (Priority: P1)

A developer or QA engineer needs to verify that the AI Technique Extraction Service correctly processes academic papers end-to-end, from raw text input through preprocessing, embedding, clustering, technique mapping, and final enriched output.

**Why this priority**: The extraction pipeline is the core MVP functionality. Without confidence in this pipeline, the service cannot be deployed or extended. This is the foundation for all other testing.

**Independent Test**: Submit 8 sample academic papers with known AI techniques (e.g., papers about RAG, RLHF, fine-tuning), verify that the service correctly identifies at least 85% of the expected techniques with confidence scores >0.6, and returns results within 10 seconds per paper.

**Acceptance Scenarios**:

1. **Given** a valid academic paper text with 3 known techniques (RAG, RLHF, transformer), **When** submitted to POST `/api/v1/extract/techniques`, **Then** the response contains all 3 techniques with confidence >0.6 and appropriate context types
2. **Given** an academic paper with LaTeX equations and references, **When** preprocessing occurs, **Then** the cleaned text removes equations, citations, and reference sections while preserving technical content
3. **Given** a paper mentioning "retrieval augmented generation", **When** technique mapping executes, **Then** the system returns the standardized name "Retrieval-Augmented Generation" (exact match from taxonomy)
4. **Given** a paper discussing production deployment of RAG systems, **When** context detection runs, **Then** the technique's context_type is "production" not "research"
5. **Given** a paper with 5 technique mentions, **When** extraction completes, **Then** text snippets show exact 50-character context windows around each mention with accurate character offsets

---

### User Story 2 - Verify Error Handling and Resilience (Priority: P2)

A developer needs to confirm that the service gracefully handles error conditions, timeouts, and malformed inputs according to the three-tier error classification system, ensuring production stability.

**Why this priority**: Robust error handling prevents cascading failures and provides clear feedback for debugging. This is critical for production readiness but secondary to core functionality validation.

**Independent Test**: Submit a series of problematic inputs (empty text, timeout simulation, malformed JSON) and verify that the service returns appropriate HTTP status codes (400 for Tier 3, 500 for Tier 2) with structured error messages, and that Tier 1 errors (no techniques found) return empty lists without failures.

**Acceptance Scenarios**:

1. **Given** a paper with text <50 characters, **When** submitted to the API, **Then** the service returns HTTP 400 with error_type "validation_error" and a clear message
2. **Given** the embedding server is unavailable, **When** extraction is attempted, **Then** the service retries 3 times with exponential backoff, then returns HTTP 500 with error_type "timeout_error"
3. **Given** a paper with no recognizable AI techniques, **When** processing completes, **Then** the service returns HTTP 200 with an empty techniques array (Tier 1: expected condition, not an error)
4. **Given** malformed JSON in the request body, **When** the API receives it, **Then** FastAPI's validation returns HTTP 422 with detailed field-level errors
5. **Given** a processing error for paper_id "test_123", **When** the error occurs, **Then** structured logs include request_id, paper_id, error_type, error_message, and phase (preprocess/embed/cluster/map)

---

### User Story 3 - Validate Service Health and Monitoring (Priority: P3)

An operations engineer needs to verify that the service provides health check endpoints and structured logging for monitoring, alerting, and debugging in production environments.

**Why this priority**: Observability is essential for production operations but doesn't block core functionality testing. This ensures the service can be monitored effectively once deployed.

**Independent Test**: Call GET `/api/v1/health` and verify response time <100ms with status "healthy", then review logs from a sample extraction to confirm all required fields (timestamp_iso8601, request_id, paper_id, duration_ms, technique_count, confidence metrics) are present in JSON format.

**Acceptance Scenarios**:

1. **Given** the service is running, **When** GET `/api/v1/health` is called, **Then** the response is received within 100ms with status 200 and JSON containing status, version, timestamp, and service name
2. **Given** an extraction operation for paper_id "test_001", **When** processing completes, **Then** structured logs contain entries for each phase (preprocess, embed, cluster, map) with request_id linking all operations
3. **Given** an extraction with 3 techniques found, **When** reviewing logs, **Then** the completion log includes technique_count=3, confidence_avg, confidence_min, and confidence_max fields
4. **Given** API keys or full paper text in memory, **When** logging occurs, **Then** logs never contain sensitive data (only paper_id and title for traceability)
5. **Given** a failed extraction, **When** the error is logged, **Then** the log entry includes error_type, error_message, and phase where failure occurred

---

### User Story 4 - Confirm Taxonomy and Confidence Scoring (Priority: P4)

A data scientist or product manager needs to validate that the 50+ technique taxonomy is correctly loaded, that exact matching works for common techniques, that LLM fallback activates for ambiguous cases, and that confidence scores follow the documented formula (base × source_multiplier × frequency_boost).

**Why this priority**: Accuracy and explainability of results are important for user trust, but the basic extraction must work first. This validates the quality and transparency of results.

**Independent Test**: Submit papers with known technique frequencies (e.g., "RAG" mentioned 1 time vs. 5 times) and different source types (academic vs. blog), verify that confidence scores increase with frequency and decrease with lower-quality sources according to the formula, and confirm that newly discovered techniques are flagged appropriately.

**Acceptance Scenarios**:

1. **Given** the service starts up, **When** taxonomy loading occurs, **Then** exactly 50+ techniques are loaded from taxonomy.json with all aliases, categories, and confidence_boost values
2. **Given** a paper mentioning "retrieval augmented generation" (exact alias), **When** technique mapping runs, **Then** Stage 1 exact match succeeds with base_confidence=1.0 (no LLM call needed)
3. **Given** a paper with ambiguous keywords not in taxonomy, **When** Stage 1 fails, **Then** Stage 2 LLM validation is called with GPT-4o-mini, returns a standardized technique name with confidence 0.0-1.0
4. **Given** "RAG" mentioned 5 times in an academic paper, **When** confidence is calculated, **Then** final score = 1.0 (exact) × 1.0 (academic) × 1.2 (5+ mentions) = 1.2 (capped at 1.0)
5. **Given** a social media post mentioning "RAG" once, **When** confidence is calculated, **Then** final score = 1.0 × 0.80 (social) × 1.0 (1 mention) = 0.80
6. **Given** a technique not in the taxonomy is extracted, **When** results are returned, **Then** the technique has newly_discovered=true flag for manual review

---

### Edge Cases

- What happens when a paper contains >50,000 words (document splitting threshold)?
- How does the system handle papers with zero recognizable English text (e.g., all equations)?
- What occurs when the embedding server returns partial results (some embeddings succeed, others fail)?
- How does LLM validation behave when OpenAI API rate limits are hit?
- What happens when a paper mentions the same technique with multiple variations (e.g., "RAG", "retrieval-augmented generation", "retrieval augmented")?
- How does the system handle Unicode characters, special characters, or non-English proper nouns in technical content?
- What occurs when confidence scores from different stages conflict (e.g., exact match high confidence but low frequency)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Testing procedures MUST validate that the health check endpoint responds within 100ms as required by Railway deployment standards
- **FR-002**: Testing procedures MUST verify that the taxonomy contains exactly 50+ techniques with all required fields (full_name, aliases, category, confidence_boost)
- **FR-003**: Testing procedures MUST confirm that academic paper preprocessing removes LaTeX commands, equations, citations, and reference sections while preserving technical terminology
- **FR-004**: Testing procedures MUST validate that the two-stage technique mapper correctly handles Stage 1 exact matching (confidence=1.0) and Stage 2 LLM validation (confidence=0.0-1.0) using real OpenAI API calls with a test account, including validation of rate limit handling and API error responses
- **FR-005**: Testing procedures MUST verify that confidence scoring follows the documented formula: base_confidence × source_multiplier × frequency_boost, with correct multipliers (academic=1.0, blog=0.95, press=0.90, podcast=0.85, social=0.80) and frequency boosts (1=1.0, 2-4=1.1, 5+=1.2 capped)
- **FR-006**: Testing procedures MUST confirm that context detection correctly classifies technique mentions as production/research/tutorial/criticism/general based on keyword patterns
- **FR-007**: Testing procedures MUST validate that text snippet extraction captures 50-character windows (±25 chars around mention) with accurate start_char and end_char offsets, limited to 3 snippets per technique
- **FR-008**: Testing procedures MUST verify that expected_accuracy is calculated correctly based on source_type (academic=0.95, blog=0.90, press_release=0.85, podcast=0.80, social=0.70)
- **FR-009**: Testing procedures MUST confirm that three-tier error classification works correctly: Tier 1 returns empty lists, Tier 2 retries with exponential backoff before 500 errors, Tier 3 returns immediate 400 errors
- **FR-010**: Testing procedures MUST validate that structured JSON logging includes all required fields: timestamp_iso8601, level, message, request_id, paper_id, source_type, duration_ms, technique_count, confidence metrics, error fields (if failed), job_id (if batch), phase
- **FR-011**: Testing procedures MUST verify that logs never contain sensitive data (API keys, passwords, full paper text) and only log paper_id and title for traceability
- **FR-012**: Testing procedures MUST confirm that the embedding client implements retry logic with exponential backoff (2^attempt seconds) for up to 3 attempts on timeouts and 5xx errors
- **FR-013**: Testing procedures MUST validate that newly discovered techniques (not in taxonomy) are flagged with newly_discovered=true
- **FR-014**: Testing procedures MUST verify that processing duration is tracked and reported in milliseconds for each operation
- **FR-015**: Testing procedures MUST confirm that API request validation uses Pydantic models and returns detailed field-level error messages for invalid inputs
- **FR-016**: Testing procedures MUST track and report OpenAI API usage costs per test suite execution, including total API calls made and estimated cost based on gpt-4o-mini pricing
- **FR-017**: Test data (8 sample academic papers with metadata) MUST be stored in a dedicated repository directory (e.g., `tests/fixtures/papers/`) under version control, with each paper stored as a separate file alongside a metadata JSON file listing expected techniques and context types
- **FR-018**: Test suite MUST be integrated into CI/CD pipeline to run automatically on pull requests and commits to main branch, with manual execution capability for local debugging and development iteration
- **FR-019**: Test results MUST be output in multiple formats: console output (with colored pass/fail indicators and summary statistics) for CI/CD pipelines, HTML report (with visual charts, detailed failure information, and drill-down capabilities) for manual review, and JSON file (with structured test results, timing data, and metadata) for programmatic analysis and automation

### Key Entities *(include if feature involves data)*

- **Test Case**: Represents a single validation scenario with input data (sample paper text, expected techniques), expected outcomes (extracted techniques, confidence ranges, error codes), and acceptance criteria (pass/fail thresholds). Attributes: test_id, description, priority, input_paper, expected_techniques, expected_confidence_range, max_duration_ms, source_type.

- **Test Suite**: A collection of related test cases grouped by functionality (e.g., extraction pipeline tests, error handling tests, logging tests). Attributes: suite_id, name, description, test_cases, execution_order. Relationships: Contains multiple Test Cases.

- **Test Execution Result**: Records the outcome of running a test case, including actual vs. expected results, timing metrics, and pass/fail status. Attributes: execution_id, test_case_id, timestamp, status (pass/fail/skip), actual_techniques, actual_confidence_scores, actual_duration_ms, error_messages, logs. Relationships: Links to one Test Case.

- **Sample Academic Paper**: A curated paper with known AI techniques used for validation, including metadata about which techniques should be found. Stored in repository at `tests/fixtures/papers/` for version control and reproducibility. Attributes: paper_id, title, text, known_techniques (list), source_type, expected_context_types, character_count, contains_latex (boolean), file_path. Relationships: Used as input for multiple Test Cases.

- **Validation Report**: Aggregated summary of test suite execution showing overall pass rate, performance metrics, and areas needing attention. Generated in three formats: console (stdout/stderr with colored text and exit codes), HTML (standalone file with interactive visualizations), and JSON (structured data file for automation). Attributes: report_id, timestamp, total_tests, passed_tests, failed_tests, skipped_tests, average_duration_ms, critical_failures (list), recommendations, output_formats (list), html_file_path, json_file_path. Relationships: Aggregates multiple Test Execution Results.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Core extraction pipeline test suite achieves 100% pass rate on 8 sample academic papers with known techniques, correctly identifying at least 85% of expected techniques
- **SC-002**: Each academic paper extraction completes within 10 seconds, meeting the performance requirement from the original specification (SC-004 of feature 001)
- **SC-003**: Health check endpoint responds within 100ms for 100 consecutive requests, meeting Railway deployment standards
- **SC-004**: Error handling tests validate all three tiers correctly: Tier 1 returns empty lists without errors, Tier 2 retries 3 times before failing with 500, Tier 3 returns immediate 400 errors with structured error messages
- **SC-005**: Confidence scoring tests confirm formula accuracy within ±0.01 tolerance for 20 test cases covering different source types and frequency patterns
- **SC-006**: Structured logging validation confirms 100% of test execution logs contain all required fields (timestamp_iso8601, request_id, paper_id, duration_ms, technique_count, confidence metrics, phase) with zero instances of sensitive data leakage (API keys, full text)
- **SC-007**: Context detection achieves 90% accuracy on 50 test cases with pre-labeled context types (production/research/tutorial/criticism/general)
- **SC-008**: Text snippet extraction produces accurate character offsets with zero misalignments when verified against source text for 100 technique mentions
- **SC-009**: Newly discovered technique flagging correctly identifies 100% of techniques not in the 50-technique taxonomy during test suite execution
- **SC-010**: Test suite execution completes within 5 minutes for the full MVP validation, enabling rapid iteration and continuous integration
- **SC-011**: Validation reports clearly identify any failed tests with specific error messages, expected vs. actual outputs, and actionable remediation guidance
- **SC-012**: Test coverage reaches 95% of implemented MVP functionality, with documented rationale for any uncovered edge cases
- **SC-013**: Test suite successfully integrates with CI/CD pipeline and automatically runs on 100% of pull requests and main branch commits, with failing tests blocking merges
- **SC-014**: Test results are generated in all three required formats (console, HTML, JSON) for every test suite execution, with HTML and JSON reports saved to a `test-reports/` directory with timestamps

## Assumptions

### Testing Environment

- Tests run against a local development instance with access to the embedding server (or a mocked embedding service for deterministic results)
- Sample academic papers are stored in a dedicated test data directory within the repository (e.g., `tests/fixtures/papers/`) under version control, ensuring consistency across all test environments
- OpenAI API access is available for LLM validation testing using a dedicated test account with API key; tests will incur real API costs (estimated $0.50-2.00 per full suite run)
- Embedding server is operational and accessible, or embedding responses are mocked to eliminate external dependencies
- OpenAI rate limits (3,500 RPM for gpt-4o-mini) are sufficient for test suite execution; tests may need retry logic or delays if rate limits are approached
- Test reports (HTML and JSON) are saved to `test-reports/` directory (gitignored) locally and uploaded as CI/CD artifacts for preservation and review

### Test Data Quality

- Sample papers contain at least 3-5 recognizable AI techniques from the taxonomy for meaningful validation
- Known techniques in sample papers are clearly mentioned (not oblique references) to enable accurate pass/fail assessment
- Test papers include realistic variations: academic papers with LaTeX, blog posts with informal language, social media posts with abbreviations

### Success Thresholds

- 85% technique identification rate is sufficient for MVP validation (allows for edge cases and ambiguous mentions)
- Confidence score tolerance of ±0.05 is acceptable for stochastic elements (BERTrend clustering) as documented in the constitution
- 100ms health check is measured without network latency (local or same-region testing)

### Scope Boundaries

- Testing focuses on the completed MVP (Phase 1-3: Setup, Foundational, User Story 1 - Academic Papers)
- Industry content preprocessing (blogs, press releases), social media handling, and batch processing are out of scope for this testing specification (Phase 4-7 features not yet implemented)
- Performance testing under load (1000+ concurrent requests) is deferred to production hardening phase
- Security testing (API key authentication, rate limiting) is deferred until Phase 7 implementation

### CI/CD Integration

- Test suite runs automatically on pull requests and commits to main branch to enforce quality gates before merging
- Developers can run tests manually during local development to iterate without incurring API costs on every commit to feature branches
- CI/CD environment must have access to OpenAI test account API key (stored as secure secret) and the embedding server (or mocked service)
- Failed tests block PR merges to maintain code quality and prevent regressions
- HTML and JSON test reports are generated as CI/CD artifacts and available for download/review in the pipeline UI
- Console output provides immediate pass/fail feedback visible in CI/CD logs with exit code 0 (success) or non-zero (failure)
