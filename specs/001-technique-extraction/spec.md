# Feature Specification: AI Technique Extraction Service

**Feature Branch**: `001-technique-extraction`  
**Created**: 2025-11-03  
**Status**: Draft  
**Input**: User description: "AI Technique Extraction Service - Automatically identifies AI techniques mentioned in any text content using semantic understanding and topic clustering"

## Clarifications

### Session 2025-11-03

- Q: How should the service authenticate and authorize users? → A: Server-to-server API key authentication - API keys stored as environment variables on calling servers, never exposed to client-side code
- Q: How should the system handle duplicate content in a batch? → A: Process once, reference for duplicates - detect duplicates and return reference to first processed result
- Q: How should the service handle rate limiting and usage throttling? → A: Hard global limit - all clients share same rate limit (e.g., 100 batches/hour total)
- Q: How should the system handle non-English content submissions? → A: Reject with error - return 400 error for any non-English content detected
- Q: How should newly discovered techniques be reviewed and promoted to the canonical taxonomy? → A: Flag with manual external process - discovered techniques returned in results with flag, admin reviews externally and updates taxonomy

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract Techniques from Academic Papers (Priority: P1)

Research teams need to process academic papers from ArXiv and other sources to identify which AI techniques are being researched. A researcher submits 20 academic papers (each 10,000+ words) and receives structured tags like "RAG", "multi-modal", "function-calling" with confidence scores, enabling them to track emerging techniques across scientific literature.

**Why this priority**: Academic papers are the highest-quality signal for emerging techniques. They provide detailed technical content with clear terminology, making them the most accurate and reliable source for trend detection. This is the foundation that all other sources build upon.

**Independent Test**: Can be fully tested by submitting a batch of 10 academic papers with known techniques mentioned, verifying that the service correctly identifies at least 85% of techniques with appropriate confidence scores (>0.8 for clear mentions), and delivers results in under 60 seconds total.

**Acceptance Scenarios**:

1. **Given** a research paper mentioning "retrieval-augmented generation" in the abstract and body, **When** the service processes the paper, **Then** the output includes technique "RAG" with confidence >0.85
2. **Given** a batch of 20 academic papers submitted for processing, **When** the service completes extraction, **Then** all 20 papers are tagged within 3 minutes with no failures
3. **Given** a paper using term "retrieval augmented" without hyphen, **When** the service processes it, **Then** the output standardizes to "RAG" (same as hyphenated version)
4. **Given** a paper mentioning technique X five times throughout the document, **When** the service processes it, **Then** confidence score reflects the frequency and context of mentions

---

### User Story 2 - Extract Techniques from Industry Content (Priority: P2)

Product teams need to monitor blog posts, press releases, and technical articles to understand which techniques are moving from research to production. A product manager submits 50 blog posts and 10 press releases, receiving standardized technique tags that show "function-calling" appearing in 15 industry blogs with production-related context, signaling technique maturation.

**Why this priority**: Industry content signals when techniques transition from research to practical application. This is critical for product decisions but secondary to academic sources for accuracy. Supports competitive intelligence and adoption tracking.

**Independent Test**: Can be fully tested by submitting 30 blog posts and 10 press releases with known technique mentions, verifying that the service identifies techniques with 80%+ accuracy, distinguishes between research discussion and production claims, and completes processing in under 2 minutes.

**Acceptance Scenarios**:

1. **Given** a blog post discussing "production RAG deployment", **When** the service processes it, **Then** technique "RAG" is tagged with context indicating production readiness
2. **Given** a press release using marketing language like "advanced AI retrieval systems", **When** the service processes it, **Then** the service infers this refers to "RAG" with moderate confidence (0.65-0.75)
3. **Given** 50 blog posts submitted in a single batch, **When** processing completes, **Then** results include technique tags for all 50 posts even if some have low confidence scores
4. **Given** a blog post mentioning a technique not in the predefined taxonomy (e.g., "agentic-RAG"), **When** the service processes it, **Then** the new technique is discovered and tagged for review

---

### User Story 3 - Process Social Media for Early Signals (Priority: P3)

Investment analysts need to detect early buzz about techniques before they appear in formal publications. An analyst submits 200 tweets and LinkedIn posts, receiving technique tags that show "multi-modal" mentioned 40 times across social media in the past week, providing an early signal before research papers are published.

**Why this priority**: Social media provides the earliest signals of technique adoption and discussion, but with lower accuracy due to brevity, informal language, and potential sarcasm. Useful for trend timing but requires validation from higher-quality sources.

**Independent Test**: Can be fully tested by submitting 100 social media posts with known technique mentions, verifying that the service identifies techniques with 70%+ accuracy, handles short-form content (280 characters), filters out obvious sarcasm or jokes, and processes the entire batch in under 90 seconds.

**Acceptance Scenarios**:

1. **Given** a tweet saying "Just implemented RAG in production - game changer", **When** the service processes it, **Then** technique "RAG" is tagged with production context
2. **Given** a tweet with sarcastic tone like "Oh great, another RAG tutorial 🙄", **When** the service processes it, **Then** either confidence score is lowered (<0.5) or the mention is flagged as non-serious
3. **Given** 200 short social media posts submitted, **When** processing completes, **Then** results distinguish between serious technical discussion and casual mentions via confidence scores
4. **Given** a social media post using acronym without explanation, **When** the service processes it, **Then** the service attempts to infer meaning from context with appropriate confidence adjustment

---

### User Story 4 - Cross-Source Batch Processing (Priority: P4)

Operations teams need to process all collected content daily—mixing 20 papers, 50 tweets, 10 blog posts, and 5 press releases in a single batch. They receive a comprehensive extraction report showing technique distribution across all sources, enabling trend analysis to detect techniques moving from academic → blog → press release pipeline.

**Why this priority**: Daily operations require processing heterogeneous content efficiently. This workflow enables the comprehensive monitoring that feeds into trend detection, but it's built on top of the individual content-type capabilities (P1-P3).

**Independent Test**: Can be fully tested by submitting a mixed batch of 85 items (20 papers, 50 social posts, 10 blogs, 5 press releases), verifying that all items are processed successfully with appropriate accuracy for each source type, the service handles variable-length content (280 chars to 10,000 words), and completes within 5 minutes total.

**Acceptance Scenarios**:

1. **Given** a mixed batch of 85 items from different sources, **When** processing completes, **Then** output groups results by source type with accuracy indicators for each
2. **Given** batch includes both a 10,000-word paper and 280-character tweet about same technique, **When** processing completes, **Then** both are tagged with same standardized technique name despite different terminology
3. **Given** one item in batch fails to process (malformed text), **When** batch processing completes, **Then** remaining 84 items are successfully processed and error is reported for failed item
4. **Given** batch processing is running, **When** user checks status, **Then** progress indicator shows items completed and estimated time remaining

---

### Edge Cases

- What happens when content mentions multiple similar techniques (e.g., "RAG" and "agentic-RAG") in same text?
- How does system handle content in multiple languages or code-switched text? System detects non-English content and rejects with HTTP 400 error indicating English-only requirement.
- What happens when technique names are abbreviated without context (e.g., "RLHF" without explanation)?
- How does system distinguish between technique mentions in different contexts (serious discussion vs. tutorial vs. criticism)?
- What happens when content length exceeds typical maximums (e.g., 50,000-word dissertation)?
- How does system handle very low-quality or garbled text input?
- What happens when batch contains duplicate content (same paper submitted twice)? System detects duplicates and processes unique content once, returning references to first processed result for duplicates.
- How does system handle techniques mentioned in negative context ("we tried RAG but it failed")?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate all requests using API key authentication via header (e.g., X-API-Key) for server-to-server communication only - API keys MUST be stored as environment variables on calling servers and MUST NOT be exposed to client-side code or client environment variables
- **FR-002**: System MUST enforce a hard global rate limit shared across all clients (e.g., 100 batches per hour total) and return HTTP 429 with retry-after header when limit exceeded
- **FR-003**: System MUST accept text content in various formats including full papers, articles, blog posts, social media posts, transcripts, and press releases
- **FR-004**: System MUST detect non-English content using fasttext language detection with ≥0.8 confidence threshold and reject it with HTTP 400 error and clear error message indicating English-only requirement. Code-switched text (>30% non-English by word count) is rejected. Non-English proper nouns (company names, person names, technical terms) are permitted as they don't affect technique extraction accuracy
- **FR-005**: System MUST process variable-length content from 100 characters to 50,000 words in a single pipeline
- **FR-006**: System MUST extract AI technique mentions using semantic understanding to recognize synonyms, variations, and related terms
- **FR-007**: System MUST standardize technique names to consistent taxonomy (e.g., "retrieval-augmented generation", "RAG system", "retrieval augmented" all become "RAG")
- **FR-008**: System MUST assign confidence scores (0.0 to 1.0) to each extracted technique indicating certainty of identification
- **FR-009**: System MUST discover new techniques not in predefined taxonomy and return them in results with "newly_discovered" flag set to true, enabling external manual review and taxonomy updates
- **FR-010**: System MUST maintain traceability from extracted techniques back to source content and specific sections where techniques are mentioned by capturing 50-character context windows (±25 chars around technique keyword) with character offsets, storing up to 3 snippets per technique in text_snippets array with format: {snippet: str, start_char: int, end_char: int}
- **FR-011**: System MUST process batch requests containing mixed content types (academic + social + industry) without requiring separate API calls
- **FR-012**: System MUST provide processing status and progress indicators for long-running batch operations
- **FR-013**: System MUST handle partial failures gracefully - if one item in batch fails, remaining items complete successfully
- **FR-014**: System MUST distinguish between different contexts of technique mentions using keyword-based classification: production use (keywords: production, deployed, live, released), research (study, experiment, investigate, paper), criticism (failed, problem, issue, limitation), tutorial (tutorial, guide, how-to, example), with fallback to 'general' context. Context type included in TechniqueMatch output as context_type field
- **FR-015**: System MUST output structured data including: technique names, confidence scores, source content references, context indicators, and processing metadata
- **FR-016**: System MUST indicate expected accuracy level based on content source type (academic: 95%+, blog: 90%+, press release: 85%+, podcast: 80%+, social: 70%+)
- **FR-017**: System MUST process content with quasi-deterministic results - same input produces identical technique names with confidence scores within ±0.05 tolerance due to BERTrend's stochastic clustering initialization (aligns with Constitution Principle II bounded non-determinism allowance)
- **FR-018**: System MUST detect duplicate content within a batch using SHA-256 hash of normalized text (strip().lower()) and process each unique content item only once, returning duplicate_of field with original paper_id for duplicates. If hash collision detected (same hash, different titles), system MUST process both items and flag with potential_duplicate=true for manual review
- **FR-019**: System MUST log all extraction operations with structured JSON format including required fields: timestamp_iso8601, level, message, request_id (UUID), paper_id, source_type, duration_ms, technique_count, confidence_avg/min/max, error_type and error_message (if failed), job_id (if batch), processing phase (preprocess/embed/cluster/map). System MUST NOT log: API keys, passwords, or full paper text (log title+id only for traceability)

### Key Entities

- **Content Item**: Represents a single piece of input text with attributes: unique ID, source type (academic/blog/social/press/podcast), title, full text content, publication date, source URL (optional). Relationships: Contains zero or more extracted techniques.

- **Extracted Technique**: Represents an identified AI technique with attributes: standardized technique name, confidence score (0.0-1.0), context type (production/research/tutorial/criticism/general), newly_discovered flag (boolean indicating if not in canonical taxonomy), text_snippets array (list of {snippet: str, start_char: int, end_char: int} showing 50-char context windows where technique mentioned, max 3 snippets), source content references. Relationships: Belongs to one content item, may link to technique taxonomy entry if canonical.

- **Technique Taxonomy Entry**: Represents a known AI technique in the standardized vocabulary with attributes: canonical name, known synonyms and variations, category/domain, first discovered date. Relationships: Referenced by extracted techniques, may have parent-child relationships with related techniques.

- **Batch Job**: Represents a collection of content items processed together with attributes: job ID, submission timestamp, total items, completed items, failed items, current status (queued/processing/completed/partial failure), estimated completion time. Relationships: Contains multiple content items, produces batch results.

- **Processing Metadata**: Captures processing details with attributes: processing duration, semantic clusters identified, confidence distribution, new techniques discovered, quality indicators. Relationships: Associated with batch job or individual content item.

- **Enriched Content Item** (API response): Extends Content Item with extraction results, adding attributes: list of extracted techniques, expected_accuracy (float 0.0-1.0 based on source_type: academic=0.95, blog=0.90, press_release=0.85, podcast=0.80, social=0.70), processing_duration_ms, total_techniques_found, confidence_distribution. Relationships: Contains original Content Item data plus extraction results.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System achieves 85% or higher precision across all content types when extracting techniques (measured against human-labeled test set of 500+ items)
- **SC-002**: System processes 100% of submitted content regardless of source type or length (no items silently dropped or skipped)
- **SC-003**: Individual short-form content (tweets, posts) processes in under 5 seconds from submission to results
- **SC-004**: Individual long-form content (academic papers) processes in under 10 seconds regardless of length up to 50,000 words
- **SC-005**: Batch of 100 mixed items completes processing within 5 minutes
- **SC-006**: Same input content produces quasi-deterministic technique extraction results when processed multiple times: (1) Technique names MUST match exactly (100% reproducible), (2) Confidence scores within ±0.05 absolute difference, (3) Topic assignments MAY vary but final techniques MUST be stable. Measurement: Process same 10-paper test set 3 times, verify technique names identical and confidence variation <±0.05
- **SC-007**: 90% of extracted techniques match standardized taxonomy names (consistent naming across all extractions)
- **SC-008**: System discovers at least 5 new technique names per 1,000 documents processed that don't exist in initial taxonomy
- **SC-009**: Confidence scores correlate with accuracy - techniques with >0.8 confidence have >90% true positive rate
- **SC-010**: Processing cost per content item averages under $0.0001 for batches of 100+ items
- **SC-011**: System handles batches up to 1,000 items without degradation in per-item processing time
- **SC-012**: Failed items in batch processing are reported with specific error messages within 30 seconds of failure

### Assumptions

- This is a backend service for server-to-server communication - API keys stored securely as environment variables, never exposed to client browsers or client-side code
- Content text is provided by upstream Scraper Agent - this service does not perform PDF extraction, web scraping, or content collection
- Input text quality is reasonable - defined as ≥50% recognizable English words, <30% special characters, coherent sentence structure. Garbage text returns empty results with quality_warning flag but does not crash system
- English is the primary language - multi-lingual support is future enhancement. Language detection uses fasttext with ≥0.8 confidence threshold
- Technique taxonomy will evolve over time - initial set of exactly 50 known techniques with expected growth of 5-10% per 1,000 documents processed (SC-008)
- Confidence thresholds configurable via CONFIDENCE_THRESHOLD environment variable (default: 0.6) - techniques below threshold marked with low_confidence=true flag but still returned for transparency. Confidence score formula: base_confidence (exact=1.0, LLM=0.0-1.0) × source_multiplier (academic=1.0, blog=0.95, press=0.90, podcast=0.85, social=0.80) × frequency_boost (1 mention=1.0, 2-4=1.1, 5+=1.2 capped)
- Source type indicators (academic/blog/social) are provided in input or inferred from content characteristics
- Administrators will review and validate newly discovered techniques via external process (outside this service) before manually updating the canonical taxonomy
- Processing latency requirements assume batch processing - real-time streaming is not required
- Cost targets assume standard pricing for semantic embedding and language model inference services
- Infrastructure can scale horizontally to handle load - no assumption of single-server constraints

