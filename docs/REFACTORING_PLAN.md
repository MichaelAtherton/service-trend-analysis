# Refactoring Plan: Current → Multi-Domain Taxonomy System

**Date**: November 7, 2025  
**Context**: Migrate from single-taxonomy to multi-tenant discovery-based system  
**Objective**: Support multiple domains (healthcare, marketing, etc.) with user-approved taxonomies

---

## Current Architecture Analysis

### What We Have

```
Current System (Single-Domain, Hardcoded)
├─ src/data/taxonomy.json (50 AI techniques)
├─ services/technique_mapper.py (loads taxonomy once)
├─ services/extraction_service.py (uses TechniqueMapper)
└─ api/endpoints.py (creates TechniqueMapper with default path)

Limitations:
❌ Single hardcoded taxonomy (AI techniques only)
❌ No multi-client support
❌ No discovery workflow
❌ No approval process
❌ No versioning
❌ No domain-specific entities
```

### What Works Well (Keep This)

```
✅ TechniqueMapper: Two-stage matching (exact + LLM)
✅ ExtractionService: Pipeline orchestration
✅ BERTrend integration: Clustering works
✅ Confidence calculation: Source multipliers, frequency boost
✅ Context detection: production/research/tutorial/criticism
✅ Text snippet extraction
✅ API structure: Health check, batch processing
✅ Error handling: Three-tier error classification
```

---

## Refactoring Strategy

### Phase-Based Approach

**Phase 1**: Multi-tenancy (client-specific taxonomies)  
**Phase 2**: Discovery workflow (BERTrend + LLM)  
**Phase 3**: Approval system (review UI)  
**Phase 4**: Base + domain merge (inheritance)

---

## Phase 1: Multi-Tenancy Refactoring

### Goal
Support multiple clients, each with their own taxonomy version

### Changes Required

#### 1.1 New Directory Structure

**Before**:
```
services/technique-extraction/
└─ src/
   └─ data/
      └─ taxonomy.json  ← Single file
```

**After**:
```
services/technique-extraction/
├─ src/
│  └─ data/
│     └─ taxonomies/
│        ├─ base/
│        │  └─ ai-techniques-v1.0.json  ← Shared AI techniques
│        │
│        ├─ healthcare/
│        │  ├─ client-a-v1.0.json
│        │  └─ client-a-v1.1.json
│        │
│        ├─ marketing/
│        │  ├─ client-b-v1.0.json
│        │  └─ client-b-v1.1.json
│        │
│        └─ [future-domain]/
│           └─ [client]-v[version].json
│
└─ tests/
   └─ fixtures/
      └─ taxonomies/  ← Test taxonomies
```

**Migration Script**:
```bash
# Move current taxonomy to base
mkdir -p src/data/taxonomies/base
mv src/data/taxonomy.json src/data/taxonomies/base/ai-techniques-v1.0.json

# Create sample domain taxonomies
mkdir -p src/data/taxonomies/healthcare
mkdir -p src/data/taxonomies/marketing
```

---

#### 1.2 Refactor `TechniqueMapper`

**Current** (`technique_mapper.py`):
```python
class TechniqueMapper:
    def __init__(self, taxonomy_path: Optional[Path] = None):
        if taxonomy_path is None:
            taxonomy_path = Path(__file__).parent.parent / "data" / "taxonomy.json"
        
        self.taxonomy = self._load_taxonomy(taxonomy_path)
        self.alias_map = self._build_alias_map()
```

**New** (`technique_mapper.py`):
```python
class TechniqueMapper:
    def __init__(
        self,
        client_id: Optional[str] = None,
        domain: Optional[str] = None,
        taxonomy_version: str = "latest"
    ):
        """
        Initialize mapper with client-specific taxonomy
        
        Args:
            client_id: Client identifier (e.g., "client-a")
            domain: Domain name (e.g., "healthcare", "marketing")
            taxonomy_version: Version string (e.g., "1.0.0", "latest")
        """
        self.client_id = client_id
        self.domain = domain
        self.version = taxonomy_version
        
        # Load base taxonomy (AI techniques)
        base_taxonomy = self._load_base_taxonomy()
        
        # Load domain taxonomy if client specified
        domain_taxonomy = {}
        if client_id and domain:
            domain_taxonomy = self._load_domain_taxonomy(client_id, domain, taxonomy_version)
        
        # Merge: domain overrides base
        self.taxonomy = {**base_taxonomy, **domain_taxonomy}
        self.alias_map = self._build_alias_map()
    
    def _load_base_taxonomy(self) -> Dict[str, Dict[str, Any]]:
        """Load shared AI techniques taxonomy"""
        path = Path(__file__).parent.parent / "data" / "taxonomies" / "base" / "ai-techniques-v1.0.json"
        return self._load_taxonomy(path)
    
    def _load_domain_taxonomy(self, client_id: str, domain: str, version: str) -> Dict[str, Dict[str, Any]]:
        """Load client-specific domain taxonomy"""
        base_path = Path(__file__).parent.parent / "data" / "taxonomies" / domain
        
        # Handle "latest" version
        if version == "latest":
            # Find highest version number
            taxonomy_files = list(base_path.glob(f"{client_id}-v*.json"))
            if not taxonomy_files:
                logger.warning(f"No taxonomy found for client={client_id}, domain={domain}")
                return {}
            
            # Sort by version (simple alphanumeric for now)
            latest_file = sorted(taxonomy_files)[-1]
            return self._load_taxonomy(latest_file)
        else:
            # Load specific version
            path = base_path / f"{client_id}-v{version}.json"
            if not path.exists():
                logger.warning(f"Taxonomy not found: {path}")
                return {}
            return self._load_taxonomy(path)
    
    def _load_taxonomy(self, path: Path) -> Dict[str, Dict[str, Any]]:
        """Load taxonomy from JSON file"""
        with open(path) as f:
            return json.load(f)
```

**Why this works**:
- Backward compatible: If `client_id=None`, only loads base taxonomy
- Merge strategy: Domain taxonomy overrides base (client can override AI technique definitions)
- Version support: "latest" or specific version
- Graceful fallback: Missing domain taxonomy returns empty dict

---

#### 1.3 Update `ExtractionService`

**Current** (`extraction_service.py`):
```python
class ExtractionService:
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        technique_mapper: TechniqueMapper
    ):
        self.embedding_client = embedding_client
        self.bertrend_service = BERTrendService(embedding_client)
        self.technique_mapper = technique_mapper
```

**New** (no changes needed - dependency injection works!):
```python
# No changes required
# TechniqueMapper is injected from endpoints.py
```

---

#### 1.4 Update API Endpoints

**Current** (`api/endpoints.py`):
```python
async def get_extraction_service() -> ExtractionService:
    """Create extraction service instance"""
    async with EmbeddingClient() as embedding_client:
        technique_mapper = TechniqueMapper()  # ← Uses default taxonomy
        return ExtractionService(embedding_client, technique_mapper)

@router.post("/extract/techniques")
async def extract_techniques(papers: List[Paper]):
    async with EmbeddingClient() as embedding_client:
        technique_mapper = TechniqueMapper()  # ← Hardcoded
        extraction_service = ExtractionService(embedding_client, technique_mapper)
        # ... process papers
```

**New** (`api/endpoints.py`):
```python
# Add client context to request
from .models import ExtractionRequest

class ExtractionRequest(BaseModel):
    """Request with client context"""
    client_id: Optional[str] = None
    domain: Optional[str] = None
    taxonomy_version: str = "latest"
    papers: List[Paper]

@router.post("/extract/techniques")
async def extract_techniques(request: ExtractionRequest):
    """
    Extract techniques using client-specific taxonomy
    
    Args:
        request: Contains client_id, domain, and papers
    """
    request_id = uuid4()
    
    async with EmbeddingClient() as embedding_client:
        # Load client-specific taxonomy
        technique_mapper = TechniqueMapper(
            client_id=request.client_id,
            domain=request.domain,
            taxonomy_version=request.taxonomy_version
        )
        extraction_service = ExtractionService(embedding_client, technique_mapper)
        
        results = []
        for paper in request.papers:
            enriched = await extraction_service.extract_techniques_sync(
                paper_id=paper.paper_id,
                title=paper.title,
                text=paper.text,
                source_type=paper.source_type,
            )
            results.append(EnrichedPaper(**enriched))
        
        return results
```

**API Request Example**:
```json
POST /api/v1/extract/techniques
{
  "client_id": "healthcare-client-a",
  "domain": "healthcare",
  "taxonomy_version": "1.0.0",
  "papers": [
    {
      "paper_id": "paper_001",
      "title": "AI in Robotic Surgery",
      "text": "...",
      "source_type": "academic"
    }
  ]
}
```

**Backward Compatibility**:
```python
# If client_id not provided, use base taxonomy only
if request.client_id is None:
    logger.info("No client_id provided, using base taxonomy only")
    technique_mapper = TechniqueMapper()  # Only AI techniques
else:
    technique_mapper = TechniqueMapper(
        client_id=request.client_id,
        domain=request.domain,
        taxonomy_version=request.taxonomy_version
    )
```

---

#### 1.5 Update API Models

**New** (`api/models.py`):
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class ExtractionRequest(BaseModel):
    """Request for technique extraction"""
    client_id: Optional[str] = Field(
        None,
        description="Client identifier (if None, uses base taxonomy only)",
        example="healthcare-client-a"
    )
    domain: Optional[str] = Field(
        None,
        description="Domain name (healthcare, marketing, etc.)",
        example="healthcare"
    )
    taxonomy_version: str = Field(
        "latest",
        description="Taxonomy version to use",
        example="1.0.0"
    )
    papers: List[Paper] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Papers to process"
    )

class EnrichedPaper(BaseModel):
    """Paper with extracted techniques"""
    paper_id: str
    title: str
    source_type: str
    techniques: List[Dict[str, Any]]
    expected_accuracy: float
    processing_duration_ms: float
    total_techniques_found: int
    confidence_distribution: Dict[str, float]
    
    # New: Taxonomy metadata
    taxonomy_used: Optional[Dict[str, Any]] = Field(
        None,
        description="Metadata about taxonomy used for extraction"
    )

# Add taxonomy metadata to response
def add_taxonomy_metadata(enriched_paper, client_id, domain, version):
    enriched_paper["taxonomy_used"] = {
        "client_id": client_id,
        "domain": domain,
        "version": version,
        "entity_count": len(technique_mapper.taxonomy)
    }
```

---

#### 1.6 Update Tests

**Current** (`tests/test_pipeline.py`):
```python
@pytest.mark.asyncio
async def test_extraction_accuracy(sample_paper_file):
    # Uses default taxonomy
    technique_mapper = TechniqueMapper()
    # ...
```

**New** (`tests/test_pipeline.py`):
```python
@pytest.fixture
def test_taxonomy_path():
    """Path to test taxonomy"""
    return Path(__file__).parent / "fixtures" / "taxonomies" / "test-taxonomy-v1.0.json"

@pytest.mark.asyncio
async def test_extraction_accuracy_base_taxonomy(sample_paper_file):
    """Test with base taxonomy only"""
    technique_mapper = TechniqueMapper()  # Base only
    # ...

@pytest.mark.asyncio
async def test_extraction_accuracy_healthcare(sample_paper_file):
    """Test with healthcare client taxonomy"""
    technique_mapper = TechniqueMapper(
        client_id="test-healthcare",
        domain="healthcare",
        taxonomy_version="1.0.0"
    )
    # ...

@pytest.mark.asyncio
async def test_extraction_accuracy_marketing(sample_paper_file):
    """Test with marketing client taxonomy"""
    technique_mapper = TechniqueMapper(
        client_id="test-marketing",
        domain="marketing",
        taxonomy_version="1.0.0"
    )
    # ...
```

**Create Test Taxonomies**:
```bash
# Create test fixtures
mkdir -p tests/fixtures/taxonomies/healthcare
mkdir -p tests/fixtures/taxonomies/marketing

# Healthcare test taxonomy
cat > tests/fixtures/taxonomies/healthcare/test-healthcare-v1.0.json <<EOF
{
  "robotic-surgery": {
    "full_name": "Robotic Surgery",
    "aliases": ["robot-assisted surgery", "surgical robotics"],
    "category": "Surgical Procedure",
    "confidence_boost": 0.0
  },
  "mri": {
    "full_name": "Magnetic Resonance Imaging",
    "aliases": ["mri", "magnetic resonance"],
    "category": "Diagnostic Imaging",
    "confidence_boost": 0.0
  }
}
EOF

# Marketing test taxonomy
cat > tests/fixtures/taxonomies/marketing/test-marketing-v1.0.json <<EOF
{
  "email-marketing": {
    "full_name": "Email Marketing",
    "aliases": ["email campaigns", "newsletter"],
    "category": "Marketing Channel",
    "confidence_boost": 0.0
  },
  "social-media-marketing": {
    "full_name": "Social Media Marketing",
    "aliases": ["smm", "social marketing"],
    "category": "Marketing Channel",
    "confidence_boost": 0.0
  }
}
EOF
```

---

### Phase 1 Summary

**Files to Modify**:
1. ✏️ `src/services/technique_mapper.py` (add multi-tenancy)
2. ✏️ `src/api/endpoints.py` (add client_id parameter)
3. ✏️ `src/api/models.py` (add ExtractionRequest model)
4. ✏️ `tests/test_pipeline.py` (add multi-domain tests)
5. 📁 Reorganize `src/data/taxonomy.json` → `src/data/taxonomies/`

**Files to Keep Unchanged**:
- ✅ `src/services/extraction_service.py` (no changes)
- ✅ `src/services/bertrend_service.py` (no changes)
- ✅ `src/services/embedding_client.py` (no changes)
- ✅ `src/preprocessing/academic.py` (no changes)

**Timeline**: 1-2 days

**Testing**:
```bash
# Test backward compatibility (base taxonomy only)
curl -X POST http://localhost:8000/api/v1/extract/techniques \
  -d '{"papers": [{"paper_id": "1", "title": "Test", "text": "..."}]}'

# Test healthcare client
curl -X POST http://localhost:8000/api/v1/extract/techniques \
  -d '{"client_id": "client-a", "domain": "healthcare", "papers": [...]}'

# Test marketing client
curl -X POST http://localhost:8000/api/v1/extract/techniques \
  -d '{"client_id": "client-b", "domain": "marketing", "papers": [...]}'
```

---

## Phase 2: Discovery Workflow

### Goal
Add BERTrend-based entity discovery with LLM extraction

### New Components

#### 2.1 Discovery Service

**New file**: `src/services/discovery_service.py`

```python
"""
Taxonomy Discovery Service
Uses BERTrend clustering + LLM to discover entity candidates
"""
import logging
from typing import List, Dict, Any
from uuid import uuid4

from .bertrend_service import BERTrendService
from .embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)


class DiscoveryService:
    """
    Discovers entity candidates from corpus using BERTrend + LLM
    """
    
    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client
        self.bertrend_service = BERTrendService(embedding_client)
    
    async def discover_entities(
        self,
        documents: List[str],
        domain: str,
        min_confidence: float = 0.7,
        min_frequency: int = 5,
        max_candidates: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Discover entity candidates from document corpus
        
        Args:
            documents: List of document texts
            domain: Domain name (healthcare, marketing, etc.)
            min_confidence: Minimum LLM confidence threshold
            min_frequency: Minimum document frequency
            max_candidates: Maximum candidates to return
            
        Returns:
            List of entity candidate dictionaries:
                {
                    "entity_name": str,
                    "aliases": List[str],
                    "category": str,
                    "confidence": float,
                    "document_count": int,
                    "cluster_id": int,
                    "keywords": List[str],
                    "sample_mentions": List[str]
                }
        """
        job_id = uuid4()
        logger.info(f"Starting discovery job {job_id} for domain={domain}")
        
        # Step 1: Split documents into paragraphs
        chunks = []
        for doc in documents:
            paragraphs = [p.strip() for p in doc.split('\n\n') if p.strip()]
            chunks.extend(paragraphs)
        
        logger.info(f"Discovery: {len(documents)} documents → {len(chunks)} chunks")
        
        # Step 2: Cluster with BERTrend
        topics = await self.bertrend_service.cluster_topics(chunks)
        logger.info(f"Discovery: Found {len(topics)} topic clusters")
        
        # Step 3: Extract entities from clusters with LLM
        candidates = []
        for topic in topics:
            keywords = topic.get("keywords", [])
            doc_indices = topic.get("document_indices", [])
            
            # Skip small clusters
            if len(doc_indices) < min_frequency:
                continue
            
            # Get sample documents for this cluster
            sample_docs = [chunks[i] for i in doc_indices[:3]]
            
            # Extract entity with LLM
            entity = await self._extract_entity_from_cluster(
                keywords=keywords,
                sample_docs=sample_docs,
                domain=domain
            )
            
            # Filter by confidence
            if entity and entity["confidence"] >= min_confidence:
                entity["document_count"] = len(doc_indices)
                entity["cluster_id"] = topic.get("topic_id", -1)
                entity["keywords"] = keywords
                entity["sample_mentions"] = sample_docs
                candidates.append(entity)
        
        # Step 4: Filter and rank
        filtered = self._filter_candidates(candidates, domain)
        ranked = sorted(filtered, key=lambda x: x["confidence"], reverse=True)
        
        logger.info(f"Discovery: {len(candidates)} raw → {len(ranked)} filtered candidates")
        
        return ranked[:max_candidates]
    
    async def _extract_entity_from_cluster(
        self,
        keywords: List[str],
        sample_docs: List[str],
        domain: str
    ) -> Dict[str, Any]:
        """
        Use LLM to extract entity from cluster
        
        Returns:
            Entity dictionary or None if no valid entity
        """
        from openai import OpenAI
        from ..config import settings
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = f"""You are curating a taxonomy for a {domain} trend detection system.

Analyze this cluster of related text:

TOP KEYWORDS: {', '.join(keywords[:10])}

SAMPLE DOCUMENTS:
1. {sample_docs[0][:200]}
2. {sample_docs[1][:200] if len(sample_docs) > 1 else 'N/A'}
3. {sample_docs[2][:200] if len(sample_docs) > 2 else 'N/A'}

TASK:
Identify the specific {domain} entity/concept this cluster represents.

Return JSON only:
{{
  "entity_name": "Canonical name (e.g., 'Robotic Surgery', 'Email Marketing')",
  "aliases": ["alias1", "alias2", "acronym"],
  "category": "Category (Procedure, Technology, Channel, etc.)",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation"
}}

RULES:
- Use domain-standard terminology
- Multi-word names preferred (not "surgery", but "Robotic Surgery")
- Reject generic terms ("system", "method", "data", "model")
- If no clear entity, return {{"entity_name": null}}
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get("entity_name"):
                return result
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
        
        return None
    
    def _filter_candidates(
        self,
        candidates: List[Dict[str, Any]],
        domain: str
    ) -> List[Dict[str, Any]]:
        """
        Filter out low-quality candidates
        
        Rules:
        - Remove generic stopwords
        - Remove single-word entities (unless high confidence)
        - Remove duplicates
        """
        filtered = []
        seen_names = set()
        
        generic_terms = {"system", "method", "approach", "model", "data", "technique"}
        
        for candidate in candidates:
            name = candidate["entity_name"].lower()
            
            # Filter: Generic terms
            if name in generic_terms:
                continue
            
            # Filter: Single word (unless confidence >0.85)
            if len(name.split()) == 1 and candidate["confidence"] < 0.85:
                continue
            
            # Filter: Duplicates
            if name in seen_names:
                continue
            
            seen_names.add(name)
            filtered.append(candidate)
        
        return filtered
```

---

#### 2.2 Discovery API Endpoints

**Add to** `src/api/endpoints.py`:

```python
from .models import DiscoveryRequest, DiscoveryResponse, EntitySuggestion
from ..services.discovery_service import DiscoveryService

@router.post(
    "/discover/entities",
    status_code=status.HTTP_200_OK,
    summary="Discover Entity Candidates from Corpus",
    response_model=DiscoveryResponse
)
async def discover_entities(request: DiscoveryRequest):
    """
    Run entity discovery on document corpus
    
    Args:
        request: Contains client_id, domain, and documents
        
    Returns:
        DiscoveryResponse with entity candidates for review
    """
    async with EmbeddingClient() as embedding_client:
        discovery_service = DiscoveryService(embedding_client)
        
        candidates = await discovery_service.discover_entities(
            documents=request.documents,
            domain=request.domain,
            min_confidence=request.min_confidence,
            min_frequency=request.min_frequency,
            max_candidates=request.max_candidates
        )
        
        return DiscoveryResponse(
            job_id=str(uuid4()),
            client_id=request.client_id,
            domain=request.domain,
            documents_processed=len(request.documents),
            candidates_found=len(candidates),
            suggestions=[EntitySuggestion(**c) for c in candidates]
        )
```

**Add to** `src/api/models.py`:

```python
class DiscoveryRequest(BaseModel):
    """Request to discover entities from corpus"""
    client_id: str
    domain: str
    documents: List[str] = Field(..., min_length=10, max_length=1000)
    min_confidence: float = Field(0.7, ge=0.0, le=1.0)
    min_frequency: int = Field(5, ge=1)
    max_candidates: int = Field(30, ge=1, le=100)

class EntitySuggestion(BaseModel):
    """Discovered entity candidate"""
    entity_name: str
    aliases: List[str]
    category: str
    confidence: float
    document_count: int
    cluster_id: int
    keywords: List[str]
    sample_mentions: List[str]

class DiscoveryResponse(BaseModel):
    """Discovery job result"""
    job_id: str
    client_id: str
    domain: str
    documents_processed: int
    candidates_found: int
    suggestions: List[EntitySuggestion]
```

---

### Phase 2 Summary

**New Files**:
1. 📄 `src/services/discovery_service.py` (new)
2. ✏️ `src/api/endpoints.py` (add `/discover/entities` endpoint)
3. ✏️ `src/api/models.py` (add discovery models)

**Timeline**: 2-3 days

**Testing**:
```bash
# Discover entities from healthcare corpus
curl -X POST http://localhost:8000/api/v1/discover/entities \
  -d '{
    "client_id": "healthcare-client-a",
    "domain": "healthcare",
    "documents": ["doc1 text...", "doc2 text...", ...],
    "min_confidence": 0.7,
    "max_candidates": 20
  }'

# Response:
{
  "job_id": "uuid",
  "candidates_found": 12,
  "suggestions": [
    {
      "entity_name": "Robotic Surgery",
      "aliases": ["robot-assisted surgery", "surgical robotics"],
      "confidence": 0.92,
      "document_count": 45,
      ...
    },
    ...
  ]
}
```

---

## Phase 3: Approval System

### Goal
User reviews and approves/rejects discovered entities

### New Components

#### 3.1 Database (SQLite for MVP)

**New file**: `src/db/schema.sql`

```sql
CREATE TABLE IF NOT EXISTS entity_suggestions (
    suggestion_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    discovery_job_id TEXT,
    
    -- Entity data
    entity_name TEXT NOT NULL,
    aliases TEXT,  -- JSON array
    category TEXT,
    confidence REAL,
    document_count INTEGER,
    
    -- Review state
    status TEXT DEFAULT 'pending_review',  -- pending_review, approved, rejected
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS taxonomies (
    taxonomy_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT DEFAULT 'draft',  -- draft, active, archived
    entity_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finalized_at TIMESTAMP,
    
    UNIQUE(client_id, domain, version)
);

CREATE INDEX idx_suggestions_client ON entity_suggestions(client_id, status);
CREATE INDEX idx_taxonomies_client ON taxonomies(client_id, status);
```

---

#### 3.2 Approval Service

**New file**: `src/services/approval_service.py`

```python
"""
Taxonomy Approval Service
Manages entity suggestions and taxonomy versioning
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ApprovalService:
    """
    Manages entity approval workflow
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "approvals.db"
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        schema_path = Path(__file__).parent.parent / "db" / "schema.sql"
        with open(schema_path) as f:
            conn.executescript(f.read())
        conn.close()
    
    def save_suggestions(
        self,
        client_id: str,
        domain: str,
        suggestions: List[Dict[str, Any]],
        job_id: str
    ):
        """Save discovery suggestions to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for suggestion in suggestions:
            cursor.execute("""
                INSERT INTO entity_suggestions
                (suggestion_id, client_id, domain, discovery_job_id,
                 entity_name, aliases, category, confidence, document_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid4()),
                client_id,
                domain,
                job_id,
                suggestion["entity_name"],
                json.dumps(suggestion["aliases"]),
                suggestion["category"],
                suggestion["confidence"],
                suggestion["document_count"]
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(suggestions)} suggestions for {client_id}/{domain}")
    
    def get_pending_suggestions(
        self,
        client_id: str,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pending suggestions for review"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if domain:
            cursor.execute("""
                SELECT * FROM entity_suggestions
                WHERE client_id = ? AND domain = ? AND status = 'pending_review'
                ORDER BY confidence DESC
            """, (client_id, domain))
        else:
            cursor.execute("""
                SELECT * FROM entity_suggestions
                WHERE client_id = ? AND status = 'pending_review'
                ORDER BY confidence DESC
            """, (client_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def approve_suggestion(
        self,
        suggestion_id: str,
        modifications: Optional[Dict[str, Any]] = None
    ):
        """Approve a suggestion (with optional edits)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if modifications:
            # Apply modifications
            cursor.execute("""
                UPDATE entity_suggestions
                SET entity_name = ?, aliases = ?, category = ?,
                    status = 'approved', reviewed_at = CURRENT_TIMESTAMP
                WHERE suggestion_id = ?
            """, (
                modifications.get("entity_name"),
                json.dumps(modifications.get("aliases", [])),
                modifications.get("category"),
                suggestion_id
            ))
        else:
            # Approve as-is
            cursor.execute("""
                UPDATE entity_suggestions
                SET status = 'approved', reviewed_at = CURRENT_TIMESTAMP
                WHERE suggestion_id = ?
            """, (suggestion_id,))
        
        conn.commit()
        conn.close()
        logger.info(f"Approved suggestion {suggestion_id}")
    
    def reject_suggestion(self, suggestion_id: str, reason: Optional[str] = None):
        """Reject a suggestion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE entity_suggestions
            SET status = 'rejected', reviewed_at = CURRENT_TIMESTAMP, rejection_reason = ?
            WHERE suggestion_id = ?
        """, (reason, suggestion_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Rejected suggestion {suggestion_id}: {reason}")
    
    def finalize_taxonomy(
        self,
        client_id: str,
        domain: str,
        version: str
    ) -> Path:
        """
        Create taxonomy file from approved suggestions
        
        Returns:
            Path to created taxonomy JSON file
        """
        # Get approved suggestions
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT entity_name, aliases, category, confidence
            FROM entity_suggestions
            WHERE client_id = ? AND domain = ? AND status = 'approved'
        """, (client_id, domain))
        
        approved = cursor.fetchall()
        
        # Build taxonomy dict
        taxonomy = {}
        for row in approved:
            key = row["entity_name"].lower().replace(" ", "-")
            taxonomy[key] = {
                "full_name": row["entity_name"],
                "aliases": json.loads(row["aliases"]),
                "category": row["category"],
                "confidence_boost": 0.0
            }
        
        # Save to file
        taxonomy_dir = Path(__file__).parent.parent / "data" / "taxonomies" / domain
        taxonomy_dir.mkdir(parents=True, exist_ok=True)
        
        taxonomy_path = taxonomy_dir / f"{client_id}-v{version}.json"
        with open(taxonomy_path, 'w') as f:
            json.dump(taxonomy, f, indent=2)
        
        # Record in database
        cursor.execute("""
            INSERT INTO taxonomies
            (taxonomy_id, client_id, domain, version, status, entity_count, finalized_at)
            VALUES (?, ?, ?, ?, 'active', ?, CURRENT_TIMESTAMP)
        """, (str(uuid4()), client_id, domain, version, len(taxonomy)))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Finalized taxonomy {client_id}/{domain} v{version}: {len(taxonomy)} entities")
        return taxonomy_path
```

---

#### 3.3 Approval Endpoints

**Add to** `src/api/endpoints.py`:

```python
from ..services.approval_service import ApprovalService

# Initialize approval service
approval_service = ApprovalService()

@router.get("/suggestions/{client_id}")
async def get_suggestions(client_id: str, domain: Optional[str] = None):
    """Get pending suggestions for review"""
    suggestions = approval_service.get_pending_suggestions(client_id, domain)
    return {"suggestions": suggestions, "count": len(suggestions)}

@router.post("/suggestions/{suggestion_id}/approve")
async def approve_suggestion(
    suggestion_id: str,
    modifications: Optional[Dict[str, Any]] = None
):
    """Approve a suggestion"""
    approval_service.approve_suggestion(suggestion_id, modifications)
    return {"status": "approved", "suggestion_id": suggestion_id}

@router.post("/suggestions/{suggestion_id}/reject")
async def reject_suggestion(
    suggestion_id: str,
    reason: Optional[str] = None
):
    """Reject a suggestion"""
    approval_service.reject_suggestion(suggestion_id, reason)
    return {"status": "rejected", "suggestion_id": suggestion_id}

@router.post("/taxonomies/{client_id}/finalize")
async def finalize_taxonomy(
    client_id: str,
    domain: str,
    version: str
):
    """Finalize taxonomy from approved suggestions"""
    taxonomy_path = approval_service.finalize_taxonomy(client_id, domain, version)
    return {
        "status": "finalized",
        "client_id": client_id,
        "domain": domain,
        "version": version,
        "path": str(taxonomy_path)
    }
```

---

### Phase 3 Summary

**New Files**:
1. 📄 `src/db/schema.sql` (database schema)
2. 📄 `src/services/approval_service.py` (approval logic)
3. ✏️ `src/api/endpoints.py` (add approval endpoints)

**Timeline**: 2-3 days

**Testing**:
```bash
# 1. Discover entities
curl -X POST http://localhost:8000/api/v1/discover/entities -d '{...}'

# 2. Get pending suggestions
curl http://localhost:8000/api/v1/suggestions/healthcare-client-a?domain=healthcare

# 3. Approve suggestion
curl -X POST http://localhost:8000/api/v1/suggestions/{id}/approve

# 4. Finalize taxonomy
curl -X POST http://localhost:8000/api/v1/taxonomies/healthcare-client-a/finalize \
  -d '{"domain": "healthcare", "version": "1.0.0"}'

# 5. Use new taxonomy
curl -X POST http://localhost:8000/api/v1/extract/techniques \
  -d '{
    "client_id": "healthcare-client-a",
    "domain": "healthcare",
    "taxonomy_version": "1.0.0",
    "papers": [...]
  }'
```

---

## Phase 4: Complete Refactoring Checklist

### Before You Start
- [ ] Backup current `src/data/taxonomy.json`
- [ ] Create feature branch: `git checkout -b feature/multi-domain-taxonomy`
- [ ] Run existing tests: `pytest` (ensure baseline passes)

### Phase 1: Multi-Tenancy (Days 1-2)
- [ ] Reorganize directory: `src/data/taxonomies/{base,healthcare,marketing}/`
- [ ] Refactor `TechniqueMapper.__init__` (add `client_id`, `domain` params)
- [ ] Add `_load_base_taxonomy()` and `_load_domain_taxonomy()` methods
- [ ] Update `api/models.py` (add `ExtractionRequest`)
- [ ] Update `api/endpoints.py` (use `ExtractionRequest`)
- [ ] Create test taxonomies in `tests/fixtures/taxonomies/`
- [ ] Update tests: `test_extraction_accuracy` (add multi-domain variants)
- [ ] Test backward compatibility (no client_id)
- [ ] Test healthcare client
- [ ] Test marketing client

### Phase 2: Discovery (Days 3-5)
- [ ] Create `src/services/discovery_service.py`
- [ ] Implement `discover_entities()` method
- [ ] Implement `_extract_entity_from_cluster()` (LLM extraction)
- [ ] Implement `_filter_candidates()` (quality filters)
- [ ] Add `DiscoveryRequest`, `DiscoveryResponse` models
- [ ] Add `/discover/entities` endpoint
- [ ] Test discovery on sample corpus (100+ docs)
- [ ] Validate LLM extraction quality

### Phase 3: Approval (Days 6-8)
- [ ] Create `src/db/schema.sql`
- [ ] Create `src/services/approval_service.py`
- [ ] Implement `save_suggestions()`
- [ ] Implement `get_pending_suggestions()`
- [ ] Implement `approve_suggestion()` and `reject_suggestion()`
- [ ] Implement `finalize_taxonomy()`
- [ ] Add approval endpoints
- [ ] Test full workflow: discover → review → approve → finalize → extract
- [ ] Create sample healthcare taxonomy (20 entities)
- [ ] Create sample marketing taxonomy (20 entities)

### Phase 4: Documentation & Deployment (Day 9-10)
- [ ] Update API documentation (Swagger/OpenAPI)
- [ ] Update README with new workflow
- [ ] Create migration guide for existing users
- [ ] Add example requests/responses
- [ ] Update environment variables (if needed)
- [ ] Deploy to staging
- [ ] Run end-to-end tests on staging
- [ ] Deploy to production

---

## Migration Path for Existing Users

### Option 1: Automatic Migration
```python
# Script: migrate_to_multi_domain.py
import json
from pathlib import Path

# Read old taxonomy
old_path = Path("src/data/taxonomy.json")
with open(old_path) as f:
    old_taxonomy = json.load(f)

# Save as base taxonomy
base_path = Path("src/data/taxonomies/base/ai-techniques-v1.0.json")
base_path.parent.mkdir(parents=True, exist_ok=True)
with open(base_path, 'w') as f:
    json.dump(old_taxonomy, f, indent=2)

print(f"✅ Migrated {len(old_taxonomy)} entities to base taxonomy")
```

### Option 2: Backward Compatibility Layer
```python
# In technique_mapper.py
class TechniqueMapper:
    def __init__(self, client_id=None, domain=None, taxonomy_version="latest", taxonomy_path=None):
        # Legacy support: if taxonomy_path provided, use it
        if taxonomy_path is not None:
            logger.warning("taxonomy_path is deprecated. Use client_id/domain instead.")
            self.taxonomy = self._load_taxonomy(taxonomy_path)
            self.alias_map = self._build_alias_map()
            return
        
        # New multi-domain logic
        # ...
```

---

## Summary

### What Changes
1. **Directory structure**: Single `taxonomy.json` → `taxonomies/{domain}/{client}-v{version}.json`
2. **TechniqueMapper**: Hardcoded path → Dynamic loading by `client_id` + `domain`
3. **API**: `List[Paper]` → `ExtractionRequest(client_id, domain, papers)`
4. **New services**: `DiscoveryService`, `ApprovalService`
5. **New endpoints**: `/discover/entities`, `/suggestions/`, `/taxonomies/.../finalize`
6. **Database**: SQLite for suggestions and taxonomy metadata

### What Stays the Same
- ✅ Core extraction pipeline
- ✅ BERTrend clustering logic
- ✅ Two-stage matching (exact + LLM)
- ✅ Confidence calculation formulas
- ✅ Text snippet extraction
- ✅ Error handling

### Timeline
- **Phase 1 (Multi-tenancy)**: 1-2 days
- **Phase 2 (Discovery)**: 2-3 days
- **Phase 3 (Approval)**: 2-3 days
- **Phase 4 (Docs & Deploy)**: 1-2 days
- **Total**: ~8-10 days for complete refactoring

### Risk Mitigation
- Feature branch development
- Backward compatibility layer
- Incremental testing (phase-by-phase)
- Existing tests continue to pass

---

## Next Steps

**Immediate**:
1. Review this refactoring plan
2. Confirm phases and timeline
3. Start Phase 1 (multi-tenancy) - lowest risk, highest value

**Questions**:
1. Do you want to start with Phase 1 now?
2. Should we create a separate branch for this work?
3. Do you need database choice guidance (SQLite vs. PostgreSQL)?

Let me know and I'll start implementing!

