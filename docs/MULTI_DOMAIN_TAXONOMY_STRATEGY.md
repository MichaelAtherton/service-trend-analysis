# Multi-Domain Taxonomy Strategy

**Date**: November 6, 2025  
**Context**: Designing taxonomy system for diverse knowledge domains  
**Scope**: Healthcare AI, Marketing AI, and future domains

---

## Executive Summary

**The Real Requirement**: Build a flexible trend detection platform where:
- **Client 1** (Healthcare): Track AI techniques in surgery/healthcare
- **Client 2** (Marketing): Track AI applications in marketing
- **Future clients**: Any domain × AI intersection

**Key Insight**: The taxonomy is **not about AI techniques** - it's about **domain-specific entities** that clients care about tracking.

**Recommended Architecture**: Multi-tenant taxonomy system with:
1. **Base taxonomy** (shared AI techniques across all domains)
2. **Domain taxonomies** (healthcare-specific, marketing-specific)
3. **Discovery-first workflow** (use BERTrend to bootstrap taxonomies)
4. **Client-specific configurations** (each client has their own entity catalog)

---

## Current vs. Needed Architecture

### What We Built (Current)

```
Single hardcoded taxonomy.json
  ↓
50 AI techniques (RLHF, LoRA, RAG...)
  ↓
Works for: AI research papers
  ↓
Limitation: One-size-fits-all, AI-only
```

### What You Need (Multi-Domain)

```
Taxonomy Management System
  ↓
  ├─ Client A: Healthcare taxonomy
  │    ├─ Base: AI techniques (RLHF, transformers...)
  │    └─ Domain: Surgery types, procedures, medical devices
  │
  ├─ Client B: Marketing taxonomy
  │    ├─ Base: AI techniques (RAG, LLMs...)
  │    └─ Domain: Campaigns, channels, strategies, platforms
  │
  └─ Client C: [Future domain]
       ├─ Base: AI techniques
       └─ Domain: [Custom entities]
```

---

## Use Case Analysis

### Client 1: Healthcare + AI

**Goal**: "Where is AI impacting surgery and healthcare?"

**Entities to Track**:

**Category 1: AI Techniques** (Base taxonomy)
```json
{
  "computer-vision": {
    "full_name": "Computer Vision",
    "aliases": ["cv", "image recognition", "visual ai"],
    "category": "AI Technique"
  },
  "llm": {
    "full_name": "Large Language Model",
    "aliases": ["llm", "language model", "gpt"],
    "category": "AI Technique"
  }
}
```

**Category 2: Healthcare Domains** (Domain taxonomy)
```json
{
  "robotic-surgery": {
    "full_name": "Robotic Surgery",
    "aliases": ["robot-assisted surgery", "surgical robotics", "da vinci surgery"],
    "category": "Surgical Procedure"
  },
  "diagnostic-imaging": {
    "full_name": "Diagnostic Imaging",
    "aliases": ["medical imaging", "radiology", "ct scan", "mri"],
    "category": "Diagnostic"
  },
  "patient-monitoring": {
    "full_name": "Patient Monitoring",
    "aliases": ["vital signs", "patient tracking", "icu monitoring"],
    "category": "Clinical Care"
  },
  "drug-discovery": {
    "full_name": "Drug Discovery",
    "aliases": ["pharmaceutical research", "compound screening"],
    "category": "Research"
  }
}
```

**Example extraction**:
```
Paper: "Computer vision models for detecting tumors in MRI scans"

Extracted entities:
  ✓ Computer Vision (AI Technique)
  ✓ Diagnostic Imaging (Healthcare Domain)
  ✓ MRI (Medical Device - if in taxonomy)

Trend insight: "Computer Vision increasingly used in Diagnostic Imaging"
```

---

### Client 2: Marketing + AI

**Goal**: "Identify trends in AI for marketing"

**Entities to Track**:

**Category 1: AI Techniques** (Base taxonomy - shared)
```json
{
  "llm": {
    "full_name": "Large Language Model",
    "aliases": ["llm", "gpt", "language model"],
    "category": "AI Technique"
  },
  "generative-ai": {
    "full_name": "Generative AI",
    "aliases": ["genai", "generative models", "content generation"],
    "category": "AI Technique"
  }
}
```

**Category 2: Marketing Domains** (Domain taxonomy)
```json
{
  "content-marketing": {
    "full_name": "Content Marketing",
    "aliases": ["content creation", "blog marketing", "content strategy"],
    "category": "Marketing Strategy"
  },
  "social-media-marketing": {
    "full_name": "Social Media Marketing",
    "aliases": ["smm", "social marketing", "instagram marketing", "tiktok marketing"],
    "category": "Marketing Channel"
  },
  "email-campaigns": {
    "full_name": "Email Marketing",
    "aliases": ["email campaigns", "newsletter", "drip campaigns"],
    "category": "Marketing Channel"
  },
  "customer-segmentation": {
    "full_name": "Customer Segmentation",
    "aliases": ["audience targeting", "market segmentation", "persona"],
    "category": "Marketing Analytics"
  },
  "ad-creative": {
    "full_name": "Ad Creative",
    "aliases": ["advertisement design", "creative assets", "ad copy"],
    "category": "Marketing Content"
  }
}
```

**Example extraction**:
```
Blog post: "Using GPT-4 to generate personalized email campaigns"

Extracted entities:
  ✓ Large Language Model (AI Technique) [matched "GPT-4"]
  ✓ Email Marketing (Marketing Channel) [matched "email campaigns"]
  ✓ Customer Segmentation (Marketing Analytics) [inferred from "personalized"]

Trend insight: "LLMs increasingly used for Email Marketing personalization"
```

---

## Taxonomy Development Workflows

### Workflow 1: Curation-First (Current Approach)

**When to use**: You know the domain well, have existing glossaries

**Process**:
```
1. Expert knowledge
   ↓
2. Manually create taxonomy.json (50-200 entities)
   ↓
3. Extract from documents
   ↓
4. Refine taxonomy based on results
   ↓
5. Repeat
```

**Pros**:
- ✅ High accuracy immediately
- ✅ Controlled vocabulary
- ✅ Fast extraction (direct matching)

**Cons**:
- ❌ Requires domain expertise upfront
- ❌ Time-consuming initial setup
- ❌ May miss emerging entities

**Best for**: Established domains (healthcare, marketing), expert-led projects

---

### Workflow 2: Discovery-First (BERTrend-Led)

**When to use**: Exploring new domain, building taxonomy from scratch

**Process**:
```
1. Collect 100-1000 domain documents
   ↓
2. Run BERTrend clustering
   ↓
3. Extract top keywords from clusters (C-TF-IDF)
   ↓
4. LLM summarizes: "What entities do these keywords represent?"
   ↓
5. Human reviews suggestions
   ↓
6. Curate into taxonomy
   ↓
7. Re-extract with new taxonomy
   ↓
8. Iterate
```

**Pros**:
- ✅ Discover unknown entities
- ✅ Data-driven (not just expert opinion)
- ✅ Faster initial setup

**Cons**:
- ❌ Requires good seed data (100+ docs)
- ❌ Lower accuracy initially
- ❌ Needs human curation loop

**Best for**: New domains, exploratory research, trend detection

---

### Workflow 3: Hybrid (Recommended)

**Combines both approaches**:

```
Phase 1: Bootstrap (Curation-First)
  ├─ Start with 10-20 known entities
  ├─ Domain expert input
  └─ Quick wins on obvious terms

Phase 2: Discover (Discovery-First)
  ├─ Run BERTrend on first 100 documents
  ├─ Extract candidate entities
  └─ Add top 20-30 to taxonomy

Phase 3: Refine (Iterative)
  ├─ Process 1,000+ documents
  ├─ Track which entities appear frequently
  ├─ Remove rare entities (<5 mentions)
  └─ Add common patterns

Phase 4: Maintain (Ongoing)
  ├─ Weekly discovery runs
  ├─ Human reviews new candidates
  └─ Continuous taxonomy growth
```

**Timeline example**:
```
Week 1: Expert seeds 15 healthcare entities → 70% recall
Week 2: BERTrend discovers 25 more → 85% recall
Week 4: Refine to 40 high-quality entities → 90% recall
Month 3: 60 entities, automated discovery → 95% recall
```

---

## Multi-Tenant Architecture

### Design Pattern: Taxonomy-as-a-Service (TaaS)

**Database Schema**:

```sql
-- Clients table
CREATE TABLE clients (
  client_id UUID PRIMARY KEY,
  name VARCHAR(255),
  domain VARCHAR(100),  -- 'healthcare', 'marketing', etc.
  created_at TIMESTAMP
);

-- Taxonomies table (one per client)
CREATE TABLE taxonomies (
  taxonomy_id UUID PRIMARY KEY,
  client_id UUID REFERENCES clients(client_id),
  name VARCHAR(255),  -- 'Healthcare AI Entities'
  version VARCHAR(20),  -- '1.2.0'
  status VARCHAR(20),  -- 'active', 'draft', 'archived'
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Entities table (the actual taxonomy entries)
CREATE TABLE entities (
  entity_id UUID PRIMARY KEY,
  taxonomy_id UUID REFERENCES taxonomies(taxonomy_id),
  entity_key VARCHAR(100),  -- 'robotic-surgery'
  full_name VARCHAR(255),  -- 'Robotic Surgery'
  aliases JSONB,  -- ['robot-assisted surgery', ...]
  category VARCHAR(100),  -- 'Surgical Procedure'
  confidence_boost FLOAT,
  description TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  
  UNIQUE(taxonomy_id, entity_key)
);

-- Extraction jobs (track which taxonomy was used)
CREATE TABLE extraction_jobs (
  job_id UUID PRIMARY KEY,
  client_id UUID REFERENCES clients(client_id),
  taxonomy_id UUID REFERENCES taxonomies(taxonomy_id),
  documents_processed INT,
  entities_found INT,
  created_at TIMESTAMP
);
```

---

### API Design

**Taxonomy Management Endpoints**:

```python
# Create taxonomy for new client
POST /api/v1/clients/{client_id}/taxonomies
{
  "name": "Healthcare AI Entities",
  "domain": "healthcare",
  "base_taxonomy": "ai-techniques-v1",  # Inherit shared AI techniques
  "custom_entities": [
    {
      "entity_key": "robotic-surgery",
      "full_name": "Robotic Surgery",
      "aliases": ["robot-assisted surgery", "surgical robotics"],
      "category": "Surgical Procedure"
    }
  ]
}

# Extract using client-specific taxonomy
POST /api/v1/clients/{client_id}/extract/techniques
{
  "taxonomy_version": "1.2.0",  # Optional: use specific version
  "papers": [...]
}

# Discover new entities
POST /api/v1/clients/{client_id}/taxonomies/{taxonomy_id}/discover
{
  "documents": [...],  # Sample docs for discovery
  "min_frequency": 5,  # Only suggest entities appearing 5+ times
  "top_n": 20  # Return top 20 candidates
}

# Get discovery suggestions
GET /api/v1/clients/{client_id}/taxonomies/{taxonomy_id}/suggestions

# Approve/reject suggestions
POST /api/v1/clients/{client_id}/taxonomies/{taxonomy_id}/suggestions/{suggestion_id}/approve
POST /api/v1/clients/{client_id}/taxonomies/{taxonomy_id}/suggestions/{suggestion_id}/reject
```

---

### File-Based Alternative (Simpler)

For MVP, use file-based approach:

```
taxonomies/
  ├── base/
  │   └── ai-techniques.json  # Shared across all clients
  │
  ├── healthcare/
  │   ├── client-a-v1.0.json
  │   └── client-a-v1.1.json
  │
  ├── marketing/
  │   ├── client-b-v1.0.json
  │   └── client-b-v1.1.json
  │
  └── [domain]/
      └── [client]-v[version].json
```

**Loading logic**:
```python
def load_taxonomy(client_id: str, domain: str, version: str = "latest"):
    # Load base taxonomy
    base = load_json("taxonomies/base/ai-techniques.json")
    
    # Load client-specific taxonomy
    client_file = f"taxonomies/{domain}/{client_id}-v{version}.json"
    client_taxonomy = load_json(client_file)
    
    # Merge (client_taxonomy overrides base)
    merged = {**base, **client_taxonomy}
    
    return merged
```

---

## Developing Domain Taxonomies

### Healthcare Taxonomy Development

**Step 1: Identify categories** (10-15 categories)

```
1. Surgical Procedures (robotic surgery, laparoscopy, etc.)
2. Diagnostic Methods (imaging, lab tests, screening)
3. Treatment Types (chemotherapy, radiation, immunotherapy)
4. Medical Devices (monitors, implants, prosthetics)
5. Clinical Workflows (patient intake, triage, discharge)
6. Healthcare Analytics (predictive models, risk scores)
7. Patient Outcomes (mortality, readmission, quality of life)
8. Medical Specialties (oncology, cardiology, neurology)
9. AI Techniques (computer vision, NLP, robotics)
10. Data Sources (EHR, imaging, wearables)
```

**Step 2: Seed with 5-10 entities per category** (50-100 total)

**Step 3: Run discovery on healthcare documents**
```bash
# Collect 100-500 healthcare AI papers/articles
# Run BERTrend clustering
# Extract top keywords
# Map to categories
```

**Step 4: Expert review**
- Clinician reviews suggested entities
- Validates medical terminology
- Adds missing critical entities

**Step 5: Iterate**
- Process 1,000+ documents
- Track precision/recall
- Refine until 85%+ accuracy

---

### Marketing Taxonomy Development

**Step 1: Identify categories**

```
1. Marketing Channels (email, social, search, display)
2. Campaign Types (awareness, conversion, retention)
3. Content Types (blog, video, infographic, podcast)
4. Marketing Analytics (attribution, ROI, engagement)
5. Customer Journey (awareness, consideration, purchase, loyalty)
6. Marketing Automation (CRM, CDP, MAP)
7. Ad Platforms (Google, Facebook, TikTok, LinkedIn)
8. Marketing Strategies (SEO, content marketing, influencer)
9. AI Techniques (recommendation, personalization, generation)
10. Metrics (CTR, conversion rate, CAC, LTV)
```

**Step 2: Seed from marketing glossaries**
- Use existing industry glossaries
- Add AI-specific marketing terms
- Include platform-specific terms

**Step 3: Discovery on marketing content**
```bash
# Collect marketing blogs, case studies, reports
# Run BERTrend
# Extract marketing-specific entities
```

**Step 4: Marketer review**
- Marketing expert validates
- Ensures industry-standard terminology
- Adds trending terms (e.g., "TikTok Shop")

---

## Base Taxonomy Strategy

### Shared AI Techniques Taxonomy

**Approach**: Maintain one "base" taxonomy of AI techniques shared across all domains

**Contents** (50-100 techniques):
```json
{
  "llm": {
    "full_name": "Large Language Model",
    "aliases": ["llm", "language model", "gpt", "bert", "transformer"],
    "category": "AI Model Type",
    "applies_to": ["all"]  # Universal
  },
  "computer-vision": {
    "full_name": "Computer Vision",
    "aliases": ["cv", "image recognition", "object detection"],
    "category": "AI Capability",
    "applies_to": ["healthcare", "retail", "manufacturing"]
  },
  "reinforcement-learning": {
    "full_name": "Reinforcement Learning",
    "aliases": ["rl", "reward learning", "policy learning"],
    "category": "AI Training Method",
    "applies_to": ["robotics", "gaming", "optimization"]
  }
}
```

**Maintenance**:
- Updated quarterly by AI team
- Versioned (v1.0, v1.1, etc.)
- Clients inherit automatically (but can override)

---

### Domain-Specific Add-Ons

**Pattern**:
```
Client Taxonomy = Base Taxonomy + Domain Taxonomy

Example:
  Healthcare Client = ai-techniques.json + healthcare-entities.json
  Marketing Client = ai-techniques.json + marketing-entities.json
```

**Benefits**:
- Reuse AI technique definitions
- Domain experts focus on domain entities only
- Consistency across clients (same AI terms)
- Easy to update base taxonomy globally

---

## Discovery Workflow (Detailed)

### Using BERTrend for Taxonomy Bootstrap

**Scenario**: Client wants healthcare taxonomy, but you don't have medical expertise

**Process**:

#### Phase 1: Data Collection
```python
# Client provides 100-500 documents
documents = [
    {"id": "doc_1", "text": "AI-powered robotic surgery systems..."},
    {"id": "doc_2", "text": "Deep learning for MRI tumor detection..."},
    # ... 100+ more
]
```

#### Phase 2: BERTrend Clustering
```python
from bertrend.BERTopicModel import BERTopicModel

# Run clustering
model = BERTopicModel(config=healthcare_config)
result = model.fit(documents, embeddings)

# Get clusters
clusters = result.topic_model.get_topics()

# Example output:
clusters = {
    0: [("robotic", 0.45), ("surgery", 0.42), ("assisted", 0.38), ...],
    1: [("imaging", 0.51), ("mri", 0.48), ("diagnostic", 0.44), ...],
    2: [("patient", 0.49), ("monitoring", 0.46), ("vital", 0.42), ...],
    # ... 15-20 clusters
}
```

#### Phase 3: LLM Entity Extraction
```python
from openai import OpenAI

def extract_entities_from_cluster(keywords, sample_docs):
    prompt = f"""
    Analyze these keywords and sample documents from a healthcare AI topic cluster:
    
    Keywords: {keywords}
    Sample docs: {sample_docs}
    
    Identify:
    1. What healthcare entity/concept is this cluster about?
    2. What is the canonical name for this entity?
    3. What are common aliases/variations?
    4. What category does it belong to? (Surgical Procedure, Diagnostic Method, Treatment, Device, etc.)
    
    Return JSON:
    {{
      "entity_name": "...",
      "full_name": "...",
      "aliases": ["...", "..."],
      "category": "...",
      "confidence": 0.0-1.0
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.choices[0].message.content)

# For each cluster
for cluster_id, keywords in clusters.items():
    # Get documents in this cluster
    docs_in_cluster = get_docs_by_cluster(cluster_id)
    sample = docs_in_cluster[:3]  # Use 3 sample docs
    
    # Extract entity
    entity = extract_entities_from_cluster(keywords, sample)
    
    # Add to taxonomy candidates
    taxonomy_candidates.append(entity)
```

#### Phase 4: Human Review UI
```
Suggested Entities (20 found):

[✓] Robotic Surgery
    Full name: Robotic Surgery
    Aliases: robot-assisted surgery, surgical robotics, da vinci
    Category: Surgical Procedure
    Frequency: 45 documents
    Sample: "AI-powered robotic surgery systems enable..."
    [Approve] [Edit] [Reject]

[✓] Diagnostic Imaging
    Full name: Medical Imaging
    Aliases: diagnostic imaging, radiology, medical scans
    Category: Diagnostic Method
    Frequency: 38 documents
    Sample: "Deep learning for MRI tumor detection..."
    [Approve] [Edit] [Reject]

[?] Patient Monitoring
    Full name: Patient Monitoring Systems
    Aliases: vital signs monitoring, patient tracking
    Category: Clinical Technology
    Frequency: 32 documents
    Sample: "Real-time patient monitoring using AI..."
    [Approve] [Edit] [Reject]

[✗] Neural Networks  [Already in base taxonomy]
    [Skip]

...
```

#### Phase 5: Taxonomy Generation
```python
# Approved entities → taxonomy.json
approved_entities = [e for e in taxonomy_candidates if e['status'] == 'approved']

healthcare_taxonomy = {
    entity['key']: {
        "full_name": entity['full_name'],
        "aliases": entity['aliases'],
        "category": entity['category'],
        "confidence_boost": 0.0,
        "description": entity.get('description', ''),
        "discovered_from": {
            "method": "bertrend_clustering",
            "date": "2025-11-06",
            "documents_analyzed": 150,
            "cluster_id": entity['cluster_id']
        }
    }
    for entity in approved_entities
}

# Save
save_json(f"taxonomies/healthcare/{client_id}-v1.0.json", healthcare_taxonomy)
```

---

## Implementation Roadmap

### Phase 1: MVP (Current Sprint) - Single Taxonomy

**Goal**: Get one domain working (healthcare OR marketing)

**Tasks**:
1. ✅ Fix extraction accuracy (direct matching)
2. ✅ Validate with 8 test papers
3. ⬜ Deploy for one pilot client
4. ⬜ Collect feedback

**Timeline**: 1-2 days

---

### Phase 2: Multi-Taxonomy Support (Next Sprint)

**Goal**: Support multiple clients with different taxonomies

**Tasks**:
1. File-based taxonomy management
   ```
   taxonomies/{domain}/{client}-v{version}.json
   ```
2. API parameter: `taxonomy_id` or `client_id`
3. Dynamic taxonomy loading
4. Test with healthcare + marketing

**Timeline**: 3-5 days

---

### Phase 3: Discovery Integration (Sprint 3)

**Goal**: Automate taxonomy discovery using BERTrend

**Tasks**:
1. Implement BERTrend discovery pipeline
2. LLM entity extraction from clusters
3. Build suggestion review UI (simple admin panel)
4. Approval workflow

**Timeline**: 1 week

---

### Phase 4: Taxonomy Management UI (Sprint 4)

**Goal**: Non-technical users can manage taxonomies

**Tasks**:
1. Web UI for taxonomy CRUD
2. Entity search and filtering
3. Version history
4. Import/export (CSV, JSON)
5. Taxonomy comparison (diff between versions)

**Timeline**: 2 weeks

---

### Phase 5: Advanced Features (Future)

- Hierarchical taxonomies (parent-child relationships)
- Cross-domain entity linking
- Automatic synonym detection
- Collaborative curation (team editing)
- Taxonomy quality metrics (coverage, precision)

---

## Immediate Next Steps

### Option A: Healthcare First

**Week 1 Tasks**:
1. Interview healthcare client
   - What entities do they care about?
   - What questions are they asking?
   - Example: "Where is AI used in cardiology?"

2. Create initial healthcare taxonomy (20-30 entities)
   ```
   Surgical: Robotic surgery, laparoscopy, transplant
   Diagnostic: MRI, CT scan, ultrasound, pathology
   Treatment: Chemotherapy, radiation, immunotherapy
   Analytics: Risk prediction, readmission, diagnosis
   AI Tech: Computer vision, NLP, predictive models
   ```

3. Run discovery on healthcare corpus
   - Collect 100 healthcare AI papers
   - BERTrend clustering
   - Extract 30-50 entity candidates

4. Review with client
   - Show extracted entities
   - Get approval/corrections
   - Finalize v1.0 taxonomy

5. Deploy and measure
   - Process client's full document set
   - Track precision/recall
   - Iterate

---

### Option B: Marketing First

**Week 1 Tasks**:
1. Interview marketing client
   - What campaigns/channels do they track?
   - What marketing questions matter?
   - Example: "How is AI changing social media marketing?"

2. Create initial marketing taxonomy (20-30 entities)
   ```
   Channels: Email, social media, search, display, video
   Campaigns: Awareness, conversion, retention, referral
   Content: Blog posts, infographics, podcasts, webinars
   Analytics: Attribution, engagement, conversion, ROI
   AI Tech: Personalization, recommendation, generation
   ```

3. Run discovery on marketing corpus
   - Collect 100 marketing blogs/case studies
   - BERTrend clustering
   - Extract entity candidates

4. Review with client
   - Validate marketing terminology
   - Add platform-specific terms (TikTok, Instagram, etc.)
   - Finalize v1.0 taxonomy

5. Deploy and measure

---

### Option C: Both (Parallel)

**Week 1 Tasks**:
1. Create shared base taxonomy (30 AI techniques)
2. Healthcare domain taxonomy (15 entities)
3. Marketing domain taxonomy (15 entities)
4. Test extraction on both domains
5. Compare results, refine approach

**Risk**: Split focus, but proves multi-domain capability

---

## Recommended Decision Path

### Immediate (Today/Tomorrow)

**Question 1**: Which client domain do you want to prioritize?
- Healthcare (surgical/clinical AI)
- Marketing (campaign/content AI)
- Both (prove multi-domain)

**Question 2**: Do you have domain expertise in-house?
- Yes → Curation-first approach
- No → Discovery-first approach (need sample documents)

**Question 3**: Do you have sample documents (100+)?
- Yes → Can run discovery immediately
- No → Start with expert-curated seed taxonomy

---

### Technical Implementation (This Week)

**Immediate fix** (1-2 hours):
1. Implement direct matching (achieve 85%+ accuracy)
2. Test with current 50-entity AI taxonomy
3. Validate MVP works

**Multi-domain support** (2-3 days):
1. Add `client_id` parameter to API
2. Load taxonomy from `taxonomies/{domain}/{client}.json`
3. Test with 2 sample taxonomies (healthcare + marketing)

**Discovery pipeline** (3-5 days):
1. Integrate BERTrend clustering
2. Add LLM entity extraction
3. Generate taxonomy candidates
4. Build simple review interface

---

## Summary & Recommendations

### Key Insights

1. **You're building a platform, not a single-purpose tool**
   - Multi-tenant architecture required
   - Domain-agnostic extraction engine
   - Configurable taxonomies per client

2. **Taxonomy is the product's core value**
   - Quality of taxonomy = quality of insights
   - Continuous discovery + curation workflow
   - Client-specific, not one-size-fits-all

3. **BERTrend is essential for discovery**
   - Can't manually curate all domains
   - Discovery-first workflow unlocks new domains
   - Human-in-the-loop for quality

### Recommended Path

**Phase 1** (This week): Fix extraction, prove MVP on one domain
**Phase 2** (Next week): Add multi-domain support (2 clients)
**Phase 3** (Week 3): Integrate discovery pipeline
**Phase 4** (Month 2): Build taxonomy management UI

### Questions for You

1. **Which domain first**: Healthcare or Marketing?
2. **Do you have**: 100+ sample documents for that domain?
3. **Do you have**: Domain expert for initial taxonomy?
4. **Timeline**: When do you need this working for clients?

Let me know your answers and I'll create a specific implementation plan!

