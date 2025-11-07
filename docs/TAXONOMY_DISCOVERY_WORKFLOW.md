# Taxonomy Discovery & Approval Workflow

**Date**: November 7, 2025  
**Context**: Human-in-the-loop taxonomy curation from user input + corpus analysis  
**Key Principle**: All entities (manual or discovered) require user approval

---

## Overview

### Two Sources of Entities

```
┌─────────────────────────────────────────────────────┐
│           TAXONOMY ENTITY SOURCES                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Source 1: User-Provided                           │
│  ├─ Expert knowledge                               │
│  ├─ Industry glossaries                            │
│  └─ Known entities they want to track             │
│                                                     │
│  Source 2: Corpus-Discovered                       │
│  ├─ BERTrend clustering on documents               │
│  ├─ LLM entity extraction from clusters            │
│  └─ Frequency analysis (most common terms)         │
│                                                     │
│             ↓                                       │
│                                                     │
│  User Approval (Required for both)                 │
│  ├─ Review entity name                             │
│  ├─ Confirm category                               │
│  ├─ Add/edit aliases                               │
│  └─ Approve or reject                              │
│                                                     │
│             ↓                                       │
│                                                     │
│  Final Taxonomy (Curated entities only)            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Discovery Process: Step-by-Step

### Phase 1: Initial Setup (User Creates Project)

**User Action**:
```
1. Create new client project: "Healthcare Client A"
2. Select domain: "Healthcare"
3. Upload seed documents (optional): 10-500 PDFs
4. Manually add known entities (optional): 5-20 entities
```

**System Action**:
```
1. Create client record in database
2. Initialize empty taxonomy (version 0.1.0)
3. Inherit base taxonomy (AI techniques)
4. Queue documents for discovery
```

**UI Example**:
```
┌──────────────────────────────────────────────────┐
│  Create New Client                               │
├──────────────────────────────────────────────────┤
│                                                  │
│  Client Name: [Healthcare Client A         ]    │
│                                                  │
│  Domain: [Healthcare ▼]                          │
│                                                  │
│  Seed Documents (optional):                      │
│  [Drag & drop PDFs or Browse]                    │
│                                                  │
│  Known Entities (optional):                      │
│  ┌────────────────────────────────────────────┐ │
│  │ Entity           Category      [+ Add]    │ │
│  ├────────────────────────────────────────────┤ │
│  │ Robotic Surgery  Procedure     [×]        │ │
│  │ MRI              Diagnostic    [×]        │ │
│  │ [New entity...]                           │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  [Cancel]              [Create & Discover →]     │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

### Phase 2: Corpus Discovery (Automated)

**Trigger**: User uploads documents or clicks "Discover Entities"

**System Workflow**:

#### Step 2.1: Document Processing
```python
# Split documents into semantic chunks
documents = []
for pdf in uploaded_pdfs:
    text = extract_text(pdf)
    cleaned = clean_text(text)
    chunks = split_into_paragraphs(cleaned)  # 50-500 word chunks
    documents.extend(chunks)

# Result: 100 documents → 500-2000 chunks
```

#### Step 2.2: BERTrend Clustering
```python
from bertrend.BERTopicModel import BERTopicModel

# Embed all chunks
embeddings = embedding_client.embed_texts(documents)

# Cluster using BERTrend
config = {
    "umap_model": {
        "n_neighbors": min(15, len(documents) // 3),
        "n_components": 5,
        "min_dist": 0.0,
        "metric": "cosine"
    },
    "hdbscan_model": {
        "min_cluster_size": max(5, len(documents) // 20),
        "min_samples": 3,
        "metric": "euclidean"
    },
    "vectorizer_model": {
        "ngram_range": (1, 3),  # Extract 1-3 word phrases
        "stop_words": None,
        "min_df": 2  # Must appear in 2+ documents
    }
}

topic_model = BERTopicModel(config=config)
result = topic_model.fit(documents, embeddings)

# Get clusters with keywords
clusters = result.topic_model.get_topics()
```

**Output Example**:
```python
clusters = {
    0: [
        ("robotic", 0.45), ("surgery", 0.42), ("assisted", 0.38),
        ("robot assisted", 0.35), ("surgical robot", 0.31), ...
    ],
    1: [
        ("mri", 0.51), ("imaging", 0.48), ("diagnostic", 0.44),
        ("magnetic resonance", 0.40), ("scan", 0.38), ...
    ],
    2: [
        ("patient", 0.49), ("monitoring", 0.46), ("vital signs", 0.42),
        ("real time", 0.39), ("continuous monitoring", 0.35), ...
    ],
    # ... 15-30 clusters
}
```

#### Step 2.3: LLM Entity Extraction
```python
from openai import OpenAI

def extract_entity_from_cluster(cluster_id, keywords, sample_docs, domain):
    """Use LLM to identify what entity this cluster represents"""
    
    prompt = f"""
You are helping curate a taxonomy for a {domain} trend detection system.

Analyze this cluster of related text chunks:

TOP KEYWORDS (by relevance):
{format_keywords(keywords[:15])}

SAMPLE DOCUMENTS (3 examples from this cluster):
{format_sample_docs(sample_docs[:3])}

TASK:
1. Identify what specific entity/concept this cluster represents
2. Provide the canonical name (e.g., "Robotic Surgery", "Magnetic Resonance Imaging")
3. List common aliases and variations
4. Categorize it (Procedure, Diagnostic, Treatment, Device, etc.)
5. Rate your confidence (0.0-1.0)

Return JSON:
{{
  "entity_name": "Canonical name",
  "aliases": ["alias1", "alias2", "acronym"],
  "category": "Category name",
  "confidence": 0.95,
  "reasoning": "Brief explanation",
  "documents_count": {len(sample_docs)}
}}

RULES:
- Use domain-standard terminology
- Include common acronyms (MRI, CT, EHR)
- Multi-word names preferred (not just "surgery")
- Reject generic terms ("patient", "system", "method")
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # Lower temperature for consistency
    )
    
    entity = json.loads(response.choices[0].message.content)
    entity["cluster_id"] = cluster_id
    entity["status"] = "pending_review"
    entity["discovered_at"] = datetime.now().isoformat()
    
    return entity

# Extract entity from each cluster
candidates = []
for cluster_id, keywords in clusters.items():
    if cluster_id == -1:  # Skip outliers
        continue
    
    # Get documents in this cluster
    docs_in_cluster = get_cluster_documents(result, cluster_id)
    
    # Skip if too few documents
    if len(docs_in_cluster) < 5:
        continue
    
    # Extract entity
    entity = extract_entity_from_cluster(
        cluster_id=cluster_id,
        keywords=keywords,
        sample_docs=docs_in_cluster,
        domain="Healthcare"
    )
    
    # Only keep high-confidence suggestions
    if entity["confidence"] >= 0.7:
        candidates.append(entity)

# Save to database
save_entity_suggestions(client_id, candidates)
```

**Output Example**:
```json
[
  {
    "entity_name": "Robotic Surgery",
    "aliases": ["robot-assisted surgery", "surgical robotics", "da vinci surgery"],
    "category": "Surgical Procedure",
    "confidence": 0.92,
    "reasoning": "Cluster focuses on robotic systems used in surgical procedures",
    "documents_count": 45,
    "cluster_id": 0,
    "status": "pending_review"
  },
  {
    "entity_name": "Magnetic Resonance Imaging",
    "aliases": ["MRI", "mri scan", "magnetic resonance"],
    "category": "Diagnostic Imaging",
    "confidence": 0.88,
    "reasoning": "Medical imaging technique using magnetic fields",
    "documents_count": 38,
    "cluster_id": 1,
    "status": "pending_review"
  },
  {
    "entity_name": "Patient Monitoring Systems",
    "aliases": ["patient monitoring", "vital signs monitoring", "continuous monitoring"],
    "category": "Clinical Technology",
    "confidence": 0.85,
    "reasoning": "Systems for tracking patient health metrics in real-time",
    "documents_count": 32,
    "cluster_id": 2,
    "status": "pending_review"
  }
]
```

---

### Phase 3: User Review & Approval (Manual)

**System Action**: Notify user that discovery is complete

**UI: Entity Review Dashboard**

```
┌────────────────────────────────────────────────────────────────────┐
│  Taxonomy Discovery Results - Healthcare Client A                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  📊 Discovery Summary                                              │
│  ├─ Documents analyzed: 150                                        │
│  ├─ Clusters found: 18                                             │
│  ├─ Entity candidates: 12                                          │
│  └─ Status: Ready for review                                       │
│                                                                    │
│  Filter: [All ▼] [High Confidence ▼] [Sort: Frequency ▼]         │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  🔍 Entity #1 of 12                               [← →]           │
│                                                                    │
│  Entity Name:  Robotic Surgery                                     │
│  Confidence:   ████████████████████░ 92%                           │
│  Frequency:    45 documents (30% of corpus)                        │
│  Category:     Surgical Procedure                                  │
│                                                                    │
│  Aliases:                                                          │
│  • robot-assisted surgery                                          │
│  • surgical robotics                                               │
│  • da vinci surgery                                                │
│  [+ Add alias]                                                     │
│                                                                    │
│  Sample Mentions (from corpus):                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ "AI-powered robotic surgery systems enable surgeons to       │ │
│  │  perform complex procedures with enhanced precision..."      │ │
│  │                                          [View full context] │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ "Robot-assisted surgery in cardiac procedures has shown      │ │
│  │  improved outcomes compared to traditional methods..."       │ │
│  │                                          [View full context] │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  Related Keywords:                                                 │
│  robotic (0.45) • surgery (0.42) • assisted (0.38) • precision    │
│                                                                    │
│  Actions:                                                          │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Entity Name:  [Robotic Surgery                        ]    │   │
│  │ Category:     [Surgical Procedure ▼                   ]    │   │
│  │                                                            │   │
│  │ [✓ Approve]  [✗ Reject]  [✎ Edit & Approve]           │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  💡 AI Reasoning: "Cluster focuses on robotic systems used in     │
│     surgical procedures with multiple mentions of da Vinci..."    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**User Actions**:

#### Option 1: Approve (Quick)
```
User clicks [✓ Approve]
→ Entity added to taxonomy immediately
→ Move to next candidate
```

#### Option 2: Edit & Approve
```
User modifies:
  - Entity name: "Robotic Surgery" → "Robot-Assisted Surgery"
  - Adds alias: "RALS"
  - Changes category: "Surgical Procedure" → "Surgical Technology"

User clicks [✎ Edit & Approve]
→ Entity added with modifications
→ Move to next candidate
```

#### Option 3: Reject
```
User clicks [✗ Reject]
→ Optional: Provide reason (too generic, duplicate, not relevant)
→ Entity discarded, not added to taxonomy
→ Move to next candidate
```

---

### Phase 4: Bulk Actions (Power Users)

**UI: Batch Review**

```
┌────────────────────────────────────────────────────────────────────┐
│  Batch Review - 12 candidates                                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  [✓] Robotic Surgery            Procedure      45 docs   92%      │
│  [✓] MRI                        Imaging        38 docs   88%      │
│  [✓] Patient Monitoring         Technology     32 docs   85%      │
│  [✓] Chemotherapy               Treatment      28 docs   91%      │
│  [✗] Neural Network             [Duplicate in base taxonomy]      │
│  [✓] CT Scan                    Imaging        25 docs   87%      │
│  [✗] System                     [Too generic]                     │
│  [✓] Immunotherapy              Treatment      22 docs   89%      │
│  [✓] Electronic Health Record   Technology     20 docs   84%      │
│  [✗] Model                      [Too generic]                     │
│  [✓] Predictive Analytics       Analytics      18 docs   86%      │
│  [✓] Wearable Device            Device         15 docs   82%      │
│                                                                    │
│  ✓ Selected: 9     ✗ Rejected: 3              [Bulk Edit]        │
│                                                                    │
│  [Approve Selected (9)]  [Reject Selected]  [Review Individually] │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

### Phase 5: Manual Entity Addition (User-Provided)

**User Action**: "I want to add an entity I know about"

**UI: Add Entity Form**

```
┌──────────────────────────────────────────────────┐
│  Add Custom Entity                               │
├──────────────────────────────────────────────────┤
│                                                  │
│  Entity Name *:                                  │
│  [Laparoscopic Surgery                      ]    │
│                                                  │
│  Category *:                                     │
│  [Surgical Procedure ▼                      ]    │
│                                                  │
│  Aliases (comma-separated):                      │
│  [laparoscopy, minimally invasive surgery,  ]    │
│  [keyhole surgery                           ]    │
│                                                  │
│  Description (optional):                         │
│  ┌────────────────────────────────────────────┐ │
│  │ Surgical technique using small incisions  │ │
│  │ and camera-guided instruments             │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  Confidence Boost (optional):                    │
│  [0.0] ────○──────────── [+1.0]                  │
│  (Increase matching sensitivity for this term)   │
│                                                  │
│  [Cancel]                      [Add to Taxonomy] │
│                                                  │
└──────────────────────────────────────────────────┘
```

**System Action**:
- Validate entity doesn't exist
- Add to taxonomy with `source: "manual"`
- No approval needed (user created it)

---

### Phase 6: Taxonomy Versioning

**After approval session**:

```
User clicks [Finalize Version 1.0]

System creates taxonomy snapshot:
  ├─ Version: 1.0.0
  ├─ Date: 2025-11-07
  ├─ Entities: 25 (15 discovered, 10 manual)
  ├─ Status: Active
  └─ Changelog: "Initial taxonomy with robotic surgery focus"
```

**Version History UI**:

```
┌────────────────────────────────────────────────────────┐
│  Taxonomy Version History                              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ● v1.0.0 (Active)                    Nov 7, 2025     │
│    25 entities • Initial release                       │
│    [View] [Export] [Set as Active]                     │
│                                                        │
│  ○ v0.2.0 (Draft)                     Nov 6, 2025     │
│    18 entities • Post-discovery                        │
│    [View] [Compare] [Delete]                           │
│                                                        │
│  ○ v0.1.0 (Archived)                  Nov 5, 2025     │
│    10 entities • Manual seed                           │
│    [View] [Compare] [Restore]                          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Tables

```sql
-- Clients
CREATE TABLE clients (
    client_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Taxonomies (versions)
CREATE TABLE taxonomies (
    taxonomy_id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(client_id),
    version VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',  -- draft, active, archived
    created_at TIMESTAMP DEFAULT NOW(),
    finalized_at TIMESTAMP,
    changelog TEXT,
    
    UNIQUE(client_id, version)
);

-- Entity Suggestions (pending approval)
CREATE TABLE entity_suggestions (
    suggestion_id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(client_id),
    discovery_job_id UUID,
    
    -- Entity data
    entity_name VARCHAR(255) NOT NULL,
    aliases JSONB,
    category VARCHAR(100),
    description TEXT,
    
    -- Discovery metadata
    source VARCHAR(50),  -- 'corpus_discovery', 'manual', 'imported'
    confidence FLOAT,
    cluster_id INT,
    document_count INT,
    keywords JSONB,
    sample_mentions JSONB,
    
    -- Review state
    status VARCHAR(20) DEFAULT 'pending_review',  -- pending_review, approved, rejected
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Approved Entities (in taxonomy)
CREATE TABLE entities (
    entity_id UUID PRIMARY KEY,
    taxonomy_id UUID REFERENCES taxonomies(taxonomy_id),
    
    -- Entity definition
    entity_key VARCHAR(100) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    aliases JSONB,
    category VARCHAR(100),
    description TEXT,
    confidence_boost FLOAT DEFAULT 0.0,
    
    -- Origin tracking
    source VARCHAR(50),  -- 'corpus_discovery', 'manual', 'inherited'
    original_suggestion_id UUID REFERENCES entity_suggestions(suggestion_id),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(taxonomy_id, entity_key)
);

-- Discovery Jobs (track discovery runs)
CREATE TABLE discovery_jobs (
    job_id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(client_id),
    
    -- Input
    documents_processed INT,
    total_chunks INT,
    
    -- Output
    clusters_found INT,
    suggestions_generated INT,
    
    -- Configuration
    config JSONB,
    
    -- Status
    status VARCHAR(20),  -- running, completed, failed
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT
);
```

### Indexes

```sql
CREATE INDEX idx_suggestions_client ON entity_suggestions(client_id, status);
CREATE INDEX idx_suggestions_job ON entity_suggestions(discovery_job_id);
CREATE INDEX idx_entities_taxonomy ON entities(taxonomy_id);
CREATE INDEX idx_taxonomies_client ON taxonomies(client_id, status);
```

---

## API Endpoints

### Discovery Flow

```python
# 1. Start discovery job
POST /api/v1/clients/{client_id}/discover
{
  "documents": ["doc1.pdf", "doc2.pdf", ...],  # Or S3 URLs
  "config": {
    "min_cluster_size": 5,
    "min_confidence": 0.7,
    "max_suggestions": 30
  }
}
→ Returns: { "job_id": "uuid", "status": "running" }

# 2. Check discovery status
GET /api/v1/clients/{client_id}/discover/{job_id}
→ Returns: {
    "status": "completed",
    "documents_processed": 150,
    "clusters_found": 18,
    "suggestions_generated": 12
  }

# 3. Get suggestions for review
GET /api/v1/clients/{client_id}/suggestions?status=pending_review
→ Returns: [
    {
      "suggestion_id": "uuid",
      "entity_name": "Robotic Surgery",
      "confidence": 0.92,
      "document_count": 45,
      ...
    },
    ...
  ]

# 4. Approve suggestion
POST /api/v1/clients/{client_id}/suggestions/{suggestion_id}/approve
{
  "modifications": {  # Optional
    "entity_name": "Robot-Assisted Surgery",
    "aliases": ["RALS", "robotic surgery"]
  }
}
→ Adds to taxonomy draft

# 5. Reject suggestion
POST /api/v1/clients/{client_id}/suggestions/{suggestion_id}/reject
{
  "reason": "Too generic"
}

# 6. Bulk approve
POST /api/v1/clients/{client_id}/suggestions/bulk-approve
{
  "suggestion_ids": ["uuid1", "uuid2", ...]
}

# 7. Add manual entity
POST /api/v1/clients/{client_id}/entities/manual
{
  "entity_name": "Laparoscopic Surgery",
  "aliases": ["laparoscopy", "minimally invasive"],
  "category": "Surgical Procedure"
}
→ Adds to taxonomy draft directly (no approval needed)

# 8. Finalize taxonomy version
POST /api/v1/clients/{client_id}/taxonomies/finalize
{
  "version": "1.0.0",
  "changelog": "Initial release"
}
→ Creates versioned snapshot, sets as active
```

---

## Workflow Examples

### Example 1: Healthcare Client (Discovery-Heavy)

**Day 1: Setup**
```
User: Create client "Cardiology Department"
User: Upload 200 cardiology papers
System: Start discovery job
  → Process 200 papers → 2,000 chunks
  → Cluster into 25 topics
  → Extract 20 entity candidates
System: Notify user "Discovery complete"
```

**Day 2: Review**
```
User: Review 20 suggestions
User: Approve 15 (heart-related procedures)
User: Reject 3 (generic terms like "treatment")
User: Edit 2 (fix medical terminology)
User: Manually add 5 known entities (specific devices)
```

**Day 3: Finalize**
```
User: Finalize taxonomy v1.0 (20 entities)
System: Set as active
User: Run extraction on full corpus (1,000 papers)
System: Extract entities using v1.0 taxonomy
```

**Month 2: Iteration**
```
User: Upload 500 new papers
User: Click "Discover new entities"
System: Find 8 new candidates
User: Review, approve 6
User: Finalize taxonomy v1.1 (26 entities)
```

---

### Example 2: Marketing Client (Manual-Heavy)

**Day 1: Expert Seeding**
```
User: Create client "Digital Marketing Agency"
User: Manually add 30 known marketing terms
  - Email Marketing
  - Social Media Advertising
  - Content Marketing
  - SEO
  - PPC
  - etc.
User: Finalize taxonomy v1.0
```

**Week 2: Discovery**
```
User: Upload 100 marketing case studies
User: Run discovery to find missing entities
System: Suggest 10 new entities (TikTok Shop, AI Personalization, etc.)
User: Approve 8, reject 2 (already covered)
User: Finalize taxonomy v1.1 (38 entities)
```

---

### Example 3: New Domain (Exploratory)

**Week 1: Cold Start**
```
User: Create client "Legal Tech"
User: Upload 50 legal AI articles
User: Run discovery (no manual entities)
System: Generate 15 suggestions
User: Review, approve 10, manually add 5 more
User: Finalize taxonomy v1.0 (15 entities)
```

**Week 2: Expand**
```
User: Upload 200 more documents
User: Run discovery again
System: Find 20 new candidates
User: Approve 12 (legal-specific terms)
User: Finalize taxonomy v1.1 (27 entities)
```

---

## Quality Assurance

### Auto-Filters (Pre-Review)

System automatically filters out low-quality suggestions:

```python
def filter_suggestions(candidates):
    filtered = []
    
    for entity in candidates:
        # Filter 1: Low confidence
        if entity["confidence"] < 0.7:
            continue
        
        # Filter 2: Too few documents
        if entity["document_count"] < 5:
            continue
        
        # Filter 3: Generic stopwords
        generic_terms = ["system", "method", "approach", "model", "data"]
        if entity["entity_name"].lower() in generic_terms:
            continue
        
        # Filter 4: Duplicate of base taxonomy
        if entity["entity_name"] in base_taxonomy:
            entity["rejection_reason"] = "Already in base taxonomy"
            continue
        
        # Filter 5: Single-word (prefer multi-word entities)
        if len(entity["entity_name"].split()) == 1:
            if entity["confidence"] < 0.85:  # Higher bar for single words
                continue
        
        filtered.append(entity)
    
    return filtered
```

---

### Human Review Guidance

**UI Hints**:

```
┌────────────────────────────────────────────────────┐
│  💡 Review Tips                                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  ✅ Approve if:                                    │
│    • Specific, meaningful term                     │
│    • Commonly used in domain                       │
│    • Not covered by existing entities              │
│    • Multiple document mentions                    │
│                                                    │
│  ✗ Reject if:                                      │
│    • Too generic ("system", "method")              │
│    • Typo or extraction error                      │
│    • Duplicate of existing entity                  │
│    • Not relevant to your domain                   │
│                                                    │
│  ✎ Edit if:                                        │
│    • Name needs correction                         │
│    • Missing important aliases                     │
│    • Wrong category assigned                       │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## Continuous Discovery

### Scheduled Discovery Runs

```python
# Weekly discovery job
@scheduler.scheduled_job('cron', day_of_week='mon', hour=2)
def weekly_discovery():
    for client in get_active_clients():
        # Get new documents uploaded this week
        new_docs = get_new_documents(client.id, since=7_days_ago)
        
        if len(new_docs) < 20:
            continue  # Skip if too few new docs
        
        # Run discovery
        job = run_discovery(client.id, new_docs, config={
            "min_confidence": 0.8,  # Higher bar for auto-suggestions
            "max_suggestions": 10    # Only top 10
        })
        
        # Notify user
        send_notification(client.user_email, {
            "subject": "New entity suggestions available",
            "body": f"We found {job.suggestions_count} new entities in your recent documents."
        })
```

---

## Implementation Roadmap

### Phase 1: Core Discovery (Week 1)
- ✅ BERTrend clustering integration
- ✅ LLM entity extraction
- ⬜ Database schema for suggestions
- ⬜ API endpoints for discovery + approval
- ⬜ Basic CLI for review (no UI yet)

### Phase 2: Review UI (Week 2)
- ⬜ Entity review dashboard
- ⬜ Bulk approval interface
- ⬜ Manual entity addition form
- ⬜ Taxonomy versioning

### Phase 3: Automation (Week 3)
- ⬜ Scheduled discovery jobs
- ⬜ Quality filters
- ⬜ Email notifications
- ⬜ Export/import

### Phase 4: Polish (Week 4)
- ⬜ Search and filtering
- ⬜ Entity analytics (usage stats)
- ⬜ Taxonomy comparison (diff view)
- ⬜ Collaboration (team review)

---

## Summary

**Key Principles**:
1. **Two sources**: User-provided + corpus-discovered
2. **Always human-approved**: No entity added without review
3. **Iterative**: Start small, discover more, refine
4. **Versioned**: Track taxonomy evolution over time

**Workflow**:
```
Upload docs → Discover → Review → Approve → Finalize → Extract → Repeat
```

**Next Steps**:
1. Implement database schema
2. Build discovery pipeline (BERTrend + LLM)
3. Create approval API endpoints
4. Build review UI

Let me know when you're ready to implement!

