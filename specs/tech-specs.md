# BERTrend Technique Extraction Service - Technical PRD

## BERTrend Project References

**GitHub Repository:** https://github.com/rte-france/BERTrend

**Key Files for Reference:**
- Core API: `bertrend/BERTrend.py` - Main BERTrend class
- Topic Modeling: `bertrend/BERTopicModel.py` - BERTopic wrapper
- Embedding Service: `bertrend/services/embedding_service.py` - Document embedding
- Data Loading: `bertrend/utils/data_loading.py` - Data preparation utilities
- Configuration: `bertrend/config/bertrend_default_config.toml` - Default parameters

**Documentation:**
- Main README: https://github.com/rte-france/BERTrend/blob/main/README.md
- Architecture: https://github.com/rte-france/BERTrend/blob/main/docs/architecture.md
- Getting Started: https://github.com/rte-france/BERTrend/blob/main/getting_started/bertrend_quickstart.ipynb

**Installation:**
```bash
# Already installed via uv
uv pip install bertrend
```

## Executive Summary

Build a Python microservice that uses BERTrend to automatically extract AI technique tags from research papers. This service sits between the Scraper Agent and Analysis Agent, enriching raw articles with semantic technique classifications.

**Primary Goal:** Convert unstructured paper text into structured `techniques[]` field for deterministic trend analysis.

## Problem Statement

The deterministic trend analyzer requires papers with pre-tagged `techniques[]` field:

```json
{
  "id": "paper_001",
  "title": "Multi-Modal RAG with Vision APIs",
  "techniques": ["RAG", "multi-modal", "vision"]  // ← Need to generate this!
}
```

**Current gap:** Scraper Agent provides raw text, but not technique tags. Manual tagging doesn't scale.

**Solution:** BERTrend service that:
1. Ingests raw papers (title + abstract + full text)
2. Discovers semantic topics using BERT embeddings
3. Maps topics to standardized technique names
4. Outputs enriched papers with `techniques[]` populated

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Scraper Agent                             │
│  (Provides raw papers: title, abstract, url, date)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ POST /extract/techniques
                     │ { papers: [...raw...] }
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              BERTrend Extraction Service                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  1. Text Preprocessing                                 │  │
│  │     - Combine title + abstract                         │  │
│  │     - Clean text, remove noise                         │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  2. BERT Embedding (via Remote Server)                │  │
│  │     - HTTP request to embedding server                 │  │
│  │     - Server caches embeddings in-memory              │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  3. BERTopic Clustering                                │  │
│  │     - HDBSCAN clustering on embeddings                │  │
│  │     - UMAP dimensionality reduction                    │  │
│  │     - Extract topic keywords                           │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  4. Technique Mapping                                  │  │
│  │     - Map topic keywords → standard technique names   │  │
│  │     - Use LLM (GPT-4) for mapping validation         │  │
│  │     - Maintain technique taxonomy                      │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
          ┌──────────────────────────┐
          │  Embedding Server        │
          │  (BERTrend provided)     │
          │  - sentence-transformers │
          │  - In-memory cache       │
          │  - Rate limiting         │
          │  - Auth (API keys)       │
          └──────────────────────────┘
                     │
                     │ { papers: [...enriched...] }
                     │ techniques: ["RAG", "multi-modal"]
                     ↓
┌─────────────────────────────────────────────────────────────┐
│           Deterministic Trend Analyzer                       │
│  (Receives enriched papers with techniques[] populated)      │
└─────────────────────────────────────────────────────────────┘
```

## Success Metrics

**Accuracy:**
- Technique extraction precision: >85% (validated against human labels)
- Topic coherence: >0.7 (automated metric)
- Technique coverage: Captures 90%+ of relevant techniques from papers

**Performance:**
- Batch processing: 100 papers in <60 seconds
- Single paper: <2 seconds
- Cold start: <10 seconds (model loading)

**Quality:**
- False positive rate: <10% (wrong techniques assigned)
- False negative rate: <15% (missed techniques)
- Technique diversity: 30-50 unique techniques discovered

## Technology Stack

### Core Framework
**FastAPI** - RESTful API with async support

### BERTrend Components
**bertrend** - Core library for topic modeling
**sentence-transformers** - BERT embeddings (all-MiniLM-L6-v2)
**bertopic** - Topic modeling wrapper
**umap-learn** - Dimensionality reduction
**hdbscan** - Hierarchical clustering

### LLM Integration
**OpenAI API** - GPT-4 for technique mapping and validation
**tiktoken** - Token counting for cost optimization

### Data Processing
**pandas** - Data manipulation
**numpy** - Numerical operations
**scikit-learn** - Additional ML utilities

### Deployment
**Docker** - Containerization
**Uvicorn** - ASGI web server
**Prometheus** - Metrics export

### BERTrend's Embedding Architecture (Recommended)
**Remote Embedding Server** - Separate FastAPI service (provided by BERTrend)
- Location: `bertrend/services/embedding_server/`
- Handles embedding generation with in-memory caching
- Supports multiple clients with authentication
- Rate limiting built-in

**Alternative:** Local embeddings with in-memory dict cache (simpler, single-process only)

**Note:** BERTrend recommends deploying a separate embedding server rather than generating embeddings locally in each API instance. This centralizes the GPU/model and provides natural caching across multiple API workers.

## API Specification

### Endpoint 1: Extract Techniques (Batch)

**POST /extract/techniques**

```python
# Request
{
  "papers": [
    {
      "id": "paper_001",
      "title": "Multi-Modal RAG with Vision APIs",
      "abstract": "We present a novel approach to retrieval-augmented generation...",
      "date": "2025-10-15",
      "url": "https://arxiv.org/abs/2025.12345"
    },
    // ... up to 100 papers
  ],
  "options": {
    "min_cluster_size": 5,        // HDBSCAN parameter
    "confidence_threshold": 0.6,   // Minimum confidence for technique assignment
    "max_techniques_per_paper": 5 // Limit techniques per paper
  }
}

# Response
{
  "papers": [
    {
      "id": "paper_001",
      "title": "Multi-Modal RAG with Vision APIs",
      "abstract": "We present a novel approach...",
      "date": "2025-10-15",
      "url": "https://arxiv.org/abs/2025.12345",
      "techniques": ["RAG", "multi-modal", "vision"],
      "technique_scores": {
        "RAG": 0.92,
        "multi-modal": 0.87,
        "vision": 0.81
      },
      "topic_id": 7,
      "topic_keywords": ["retrieval", "augmented", "generation", "multi-modal", "vision"]
    }
  ],
  "metadata": {
    "total_papers": 100,
    "papers_processed": 98,
    "papers_failed": 2,
    "unique_techniques_found": 42,
    "topics_discovered": 15,
    "processing_time_seconds": 47.3
  }
}
```

### Endpoint 2: Get Technique Taxonomy

**GET /techniques/taxonomy**

```python
# Response
{
  "techniques": [
    {
      "name": "RAG",
      "full_name": "Retrieval-Augmented Generation",
      "category": "Architecture Patterns",
      "aliases": ["retrieval augmented", "retrieval-aug"],
      "related": ["semantic search", "vector database"],
      "paper_count": 156,
      "first_seen": "2024-03-15",
      "trend": "emerging"
    },
    {
      "name": "function-calling",
      "full_name": "Function Calling APIs",
      "category": "Tool Integration",
      "aliases": ["tool use", "function use", "tool calling"],
      "related": ["agent systems", "API integration"],
      "paper_count": 89,
      "first_seen": "2024-01-20",
      "trend": "maturing"
    }
    // ... all techniques
  ],
  "categories": [
    "Architecture Patterns",
    "Training Methods",
    "Tool Integration",
    "Evaluation Methods",
    "Model Types"
  ]
}
```

### Endpoint 3: Single Paper Extraction (Fast)

**POST /extract/techniques/single**

```python
# Request
{
  "title": "Multi-Modal RAG with Vision APIs",
  "abstract": "We present a novel approach...",
  "full_text": "Introduction: Retrieval-augmented generation..." // optional
}

# Response
{
  "techniques": ["RAG", "multi-modal", "vision"],
  "technique_scores": {
    "RAG": 0.92,
    "multi-modal": 0.87,
    "vision": 0.81
  },
  "processing_time_ms": 1847
}
```

### Endpoint 4: Retrain Topics (Admin)

**POST /admin/retrain**

```python
# Request
{
  "corpus": [/* all papers */],
  "retrain_strategy": "incremental" // or "full"
}

# Response
{
  "status": "retraining",
  "job_id": "retrain_abc123",
  "estimated_time_seconds": 300
}
```

## Core Components

### 1. Text Preprocessing (`app/preprocessing/`)

**File: `app/preprocessing/text_cleaner.py`**

```python
class TextCleaner:
    def clean_paper_text(self, paper: RawPaper) -> str:
        """
        Combine and clean paper text for embedding.
        
        Priority order:
        1. Title (always include)
        2. Abstract (if available)
        3. Full text first 1000 chars (if available)
        """
        parts = [paper.title]
        
        if paper.abstract:
            # Remove common abstract prefixes
            abstract = self._remove_abstract_noise(paper.abstract)
            parts.append(abstract)
        
        if paper.full_text:
            # Take first 1000 chars (introduction usually most informative)
            intro = paper.full_text[:1000]
            parts.append(intro)
        
        combined = " ".join(parts)
        
        # Clean noise
        combined = self._remove_urls(combined)
        combined = self._remove_citations(combined)  # [1], [Smith et al.]
        combined = self._remove_latex(combined)      # $\alpha$, \cite{}
        combined = self._normalize_whitespace(combined)
        
        return combined
```

### 2. BERTrend Service (`app/services/`)

**File: `app/services/bertrand_topic_service.py`**

**BERTrend Reference Implementation:**
See: `bertrend/BERTrend.py` for core methods like:
- `train_topic_models()` - Train topics on grouped data
- `calculate_signal_popularity()` - Compute topic popularity metrics
- `classify_signals()` - Classify topics as weak/strong signals
- `save_model()` / `restore_model()` - Model persistence

**Embedding Service Reference:**
See: `bertrend/services/embedding_service.py` for:
- `EmbeddingService(local=True)` - Local embedding setup
- `embed(texts)` - Generate document embeddings
- Remote embedding server example: `bertrend/services/embedding_server/`

```python
from bertrend import BERTrend
from bertrend.BERTopicModel import BERTopicModel
from bertrend.services.embedding_service import EmbeddingService
import pandas as pd

class BERTrendTopicService:
    def __init__(self, use_remote_embeddings: bool = True):
        # Initialize embedding service
        # BERTrend recommends remote embedding server for production
        if use_remote_embeddings:
            self.embedding_service = EmbeddingService(
                local=False,
                url=os.getenv("EMBEDDING_SERVER_URL", "http://localhost:8765"),
                client_id=os.getenv("EMBEDDING_CLIENT_ID", "bertrend_client"),
                client_secret=os.getenv("EMBEDDING_CLIENT_SECRET")
            )
        else:
            # Local embeddings (for development/testing)
            self.embedding_service = EmbeddingService(
                local=True,
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        
        # Initialize BERTrend with custom configuration
        # Reference: bertrend/config/bertrend_default_config.toml for all options
        # Reference: bertrend/config/bertopic_default_config.toml for BERTopic params
        topic_config = {
            "global": {"language": "English"},
            "bertopic_model": {
                "top_n_words": 10,
                "representation_model": ["KeyBERTInspired"]
            },
            "hdbscan_model": {
                "min_cluster_size": 5,
                "min_samples": 3
            },
            "umap_model": {
                "n_neighbors": 10,
                "n_components": 5
            }
        }
        
        self.bertrend = BERTrend(
            topic_model=BERTopicModel(config=topic_config)
        )
        
        # No local cache needed - remote embedding server handles caching
    
    async def extract_topics(
        self, 
        papers: List[RawPaper],
        min_cluster_size: int = 5
    ) -> TopicResults:
        """
        Extract topics from papers using BERTrend.
        
        Returns:
        - topics: List of discovered topics
        - paper_assignments: Which topic each paper belongs to
        - topic_keywords: Keywords for each topic
        """
        # 1. Prepare documents
        documents = [self._prepare_document(p) for p in papers]
        timestamps = [p.date for p in papers]
        
        # 2. Generate embeddings (with caching)
        embeddings = await self._get_embeddings(documents)
        
        # 3. Prepare grouped data (by time period if needed)
        df = pd.DataFrame({
            'text': documents,
            'timestamp': pd.to_datetime(timestamps),
            'paper_id': [p.id for p in papers]
        })
        
        # For batch processing, treat as single time period
        grouped_data = {pd.Timestamp.now(): df}
        
        # 4. Train topic model
        self.bertrend.train_topic_models(
            grouped_data=grouped_data,
            embeddings=embeddings,
            embedding_model=self.embedding_service.embedding_model_name,
            save_topic_models=False  # Don't persist for single batch
        )
        
        # 5. Extract results
        topic_model = self.bertrend.last_topic_model
        topics = topic_model.get_topics()
        doc_info = topic_model.get_document_info(documents)
        
        return TopicResults(
            topics=topics,
            paper_assignments=doc_info['Topic'].tolist(),
            topic_keywords=self._extract_keywords(topics),
            topic_model=topic_model
        )
    
    async def _get_embeddings(self, documents: List[str]) -> np.ndarray:
        """
        Get embeddings from remote server (recommended) or local.
        Remote server handles caching automatically.
        """
        embeddings, _, _ = self.embedding_service.embed(documents)
        return embeddings
    
    def _extract_keywords(self, topics: dict) -> Dict[int, List[str]]:
        """Extract top keywords for each topic."""
        keywords = {}
        for topic_id, words in topics.items():
            if topic_id == -1:  # Skip outlier topic
                continue
            # words is list of (word, score) tuples
            keywords[topic_id] = [w[0] for w in words[:10]]
        return keywords
```

### 3. Technique Mapping Service (`app/services/`)

**File: `app/services/technique_mapper.py`**

```python
from openai import AsyncOpenAI

class TechniqueMapper:
    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        
        # Load or initialize technique taxonomy
        self.taxonomy = self._load_taxonomy()
    
    async def map_topics_to_techniques(
        self,
        topic_keywords: Dict[int, List[str]],
        confidence_threshold: float = 0.6
    ) -> Dict[int, List[TechniqueMatch]]:
        """
        Map discovered topics to standardized technique names.
        
        Uses:
        1. Exact matching against known taxonomy
        2. LLM validation for ambiguous cases
        3. Confidence scoring
        """
        mappings = {}
        
        for topic_id, keywords in topic_keywords.items():
            # Try exact matching first (fast)
            exact_matches = self._find_exact_matches(keywords)
            
            if exact_matches:
                mappings[topic_id] = exact_matches
            else:
                # Use LLM for semantic mapping
                llm_matches = await self._llm_map_topic(keywords)
                
                # Filter by confidence
                mappings[topic_id] = [
                    m for m in llm_matches 
                    if m.confidence >= confidence_threshold
                ]
        
        return mappings
    
    def _find_exact_matches(
        self, 
        keywords: List[str]
    ) -> List[TechniqueMatch]:
        """Fast exact matching against taxonomy."""
        matches = []
        
        for technique in self.taxonomy:
            # Check if any keyword matches technique or aliases
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                if (keyword_lower == technique['name'].lower() or
                    keyword_lower in [a.lower() for a in technique['aliases']]):
                    
                    matches.append(TechniqueMatch(
                        name=technique['name'],
                        confidence=1.0,
                        match_type="exact"
                    ))
                    break
        
        return matches
    
    async def _llm_map_topic(
        self, 
        keywords: List[str]
    ) -> List[TechniqueMatch]:
        """Use LLM to map topic keywords to techniques."""
        
        # Create prompt with taxonomy context
        prompt = f"""You are an AI research expert. Map these topic keywords to standardized AI technique names.

Topic Keywords: {', '.join(keywords)}

Known Techniques:
{self._format_taxonomy_for_prompt()}

Instructions:
1. Identify which known techniques best match these keywords
2. Assign confidence score 0-1 for each match
3. Only include techniques with confidence >= 0.6
4. Return as JSON array

Output format:
[
  {{"technique": "RAG", "confidence": 0.92, "reasoning": "Keywords mention retrieval and generation"}},
  {{"technique": "multi-modal", "confidence": 0.85, "reasoning": "Mentions vision and text"}}
]

Return ONLY the JSON array, no other text."""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap for this task
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Low temp for consistency
            max_tokens=500
        )
        
        # Parse response
        try:
            matches_json = json.loads(response.choices[0].message.content)
            return [
                TechniqueMatch(
                    name=m['technique'],
                    confidence=m['confidence'],
                    match_type="llm",
                    reasoning=m.get('reasoning')
                )
                for m in matches_json
            ]
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {response.choices[0].message.content}")
            return []
    
    def _load_taxonomy(self) -> List[dict]:
        """Load technique taxonomy from file or database."""
        # Initial taxonomy (can be expanded)
        return [
            {
                "name": "RAG",
                "full_name": "Retrieval-Augmented Generation",
                "aliases": ["retrieval augmented", "retrieval-aug", "rag system"],
                "category": "Architecture Patterns"
            },
            {
                "name": "function-calling",
                "full_name": "Function Calling APIs",
                "aliases": ["tool use", "function use", "tool calling", "api calling"],
                "category": "Tool Integration"
            },
            {
                "name": "multi-modal",
                "full_name": "Multi-Modal Learning",
                "aliases": ["multimodal", "multi modal", "cross-modal"],
                "category": "Model Types"
            },
            {
                "name": "fine-tuning",
                "full_name": "Model Fine-Tuning",
                "aliases": ["finetuning", "fine tune", "instruction tuning"],
                "category": "Training Methods"
            },
            {
                "name": "prompt-engineering",
                "full_name": "Prompt Engineering",
                "aliases": ["prompting", "prompt design", "prompt optimization"],
                "category": "Interaction Methods"
            },
            # ... add more techniques
        ]
    
    def _format_taxonomy_for_prompt(self) -> str:
        """Format taxonomy for LLM prompt."""
        lines = []
        for tech in self.taxonomy[:20]:  # Limit to top 20 to save tokens
            aliases_str = ', '.join(tech['aliases'][:3])
            lines.append(f"- {tech['name']} ({tech['full_name']}): {aliases_str}")
        return '\n'.join(lines)
```

### 4. Enrichment Service (`app/services/`)

**File: `app/services/paper_enrichment_service.py`**

```python
class PaperEnrichmentService:
    def __init__(
        self,
        topic_service: BERTrendTopicService,
        mapper: TechniqueMapper
    ):
        self.topic_service = topic_service
        self.mapper = mapper
    
    async def enrich_papers(
        self,
        papers: List[RawPaper],
        options: ExtractionOptions
    ) -> EnrichedPapers:
        """
        Complete pipeline: raw papers → enriched papers with techniques.
        """
        # 1. Extract topics using BERTrend
        logger.info(f"Extracting topics from {len(papers)} papers")
        topic_results = await self.topic_service.extract_topics(
            papers,
            min_cluster_size=options.min_cluster_size
        )
        
        # 2. Map topics to techniques
        logger.info(f"Mapping {len(topic_results.topics)} topics to techniques")
        technique_mappings = await self.mapper.map_topics_to_techniques(
            topic_results.topic_keywords,
            confidence_threshold=options.confidence_threshold
        )
        
        # 3. Assign techniques to papers
        logger.info("Assigning techniques to papers")
        enriched = []
        for i, paper in enumerate(papers):
            topic_id = topic_results.paper_assignments[i]
            
            if topic_id == -1:  # Outlier
                techniques = []
                scores = {}
            else:
                # Get techniques for this topic
                matches = technique_mappings.get(topic_id, [])
                
                # Sort by confidence, limit to max_techniques_per_paper
                matches = sorted(matches, key=lambda m: m.confidence, reverse=True)
                matches = matches[:options.max_techniques_per_paper]
                
                techniques = [m.name for m in matches]
                scores = {m.name: m.confidence for m in matches}
            
            enriched.append(EnrichedPaper(
                id=paper.id,
                title=paper.title,
                abstract=paper.abstract,
                date=paper.date,
                url=paper.url,
                techniques=techniques,
                technique_scores=scores,
                topic_id=topic_id,
                topic_keywords=topic_results.topic_keywords.get(topic_id, [])
            ))
        
        return EnrichedPapers(
            papers=enriched,
            metadata=ExtractionMetadata(
                total_papers=len(papers),
                papers_processed=len([p for p in enriched if p.techniques]),
                papers_failed=len([p for p in enriched if not p.techniques]),
                unique_techniques_found=len(set(t for p in enriched for t in p.techniques)),
                topics_discovered=len(topic_results.topics)
            )
        )
```

### 5. API Routes (`app/api/`)

**File: `app/api/routes.py`**

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.requests import ExtractRequest, ExtractionOptions
from app.models.responses import EnrichedPapers
from app.services.paper_enrichment_service import PaperEnrichmentService

router = APIRouter()

@router.post("/extract/techniques", response_model=EnrichedPapers)
async def extract_techniques(request: ExtractRequest):
    """
    Extract techniques from batch of papers.
    
    Processing time: ~60s for 100 papers
    """
    if len(request.papers) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 papers per request"
        )
    
    # Get services from dependency injection
    enrichment_service = get_enrichment_service()
    
    try:
        result = await enrichment_service.enrich_papers(
            request.papers,
            request.options or ExtractionOptions()
        )
        return result
    
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )

@router.post("/extract/techniques/single")
async def extract_single(paper: SinglePaperRequest):
    """
    Fast single-paper extraction.
    
    Processing time: ~2s
    """
    enrichment_service = get_enrichment_service()
    
    # Convert to batch format
    raw_paper = RawPaper(
        id="single",
        title=paper.title,
        abstract=paper.abstract,
        full_text=paper.full_text,
        date=datetime.now()
    )
    
    result = await enrichment_service.enrich_papers(
        [raw_paper],
        ExtractionOptions()
    )
    
    if not result.papers:
        raise HTTPException(status_code=500, detail="Extraction failed")
    
    enriched = result.papers[0]
    return {
        "techniques": enriched.techniques,
        "technique_scores": enriched.technique_scores,
        "processing_time_ms": result.metadata.processing_time_ms
    }

@router.get("/techniques/taxonomy")
async def get_taxonomy():
    """Return current technique taxonomy."""
    mapper = get_technique_mapper()
    return {
        "techniques": mapper.taxonomy,
        "categories": list(set(t['category'] for t in mapper.taxonomy))
    }
```

## Data Models

```python
# app/models/requests.py

class RawPaper(BaseModel):
    id: str
    title: str
    abstract: Optional[str] = None
    full_text: Optional[str] = None
    date: datetime
    url: Optional[str] = None

class ExtractionOptions(BaseModel):
    min_cluster_size: int = 5
    confidence_threshold: float = 0.6
    max_techniques_per_paper: int = 5

class ExtractRequest(BaseModel):
    papers: List[RawPaper]
    options: Optional[ExtractionOptions] = None

# app/models/responses.py

class EnrichedPaper(BaseModel):
    id: str
    title: str
    abstract: Optional[str]
    date: datetime
    url: Optional[str]
    techniques: List[str]
    technique_scores: Dict[str, float]
    topic_id: int
    topic_keywords: List[str]

class ExtractionMetadata(BaseModel):
    total_papers: int
    papers_processed: int
    papers_failed: int
    unique_techniques_found: int
    topics_discovered: int
    processing_time_seconds: float

class EnrichedPapers(BaseModel):
    papers: List[EnrichedPaper]
    metadata: ExtractionMetadata
```

## Deployment

### Two-Service Architecture (Recommended)

**Service 1: BERTrend Extraction API** (Port 8001)
- FastAPI service for technique extraction
- Connects to embedding server
- Multiple instances can run (horizontal scaling)

**Service 2: Embedding Server** (Port 8765)
- BERTrend's built-in embedding service
- Handles all embedding generation + caching
- Single instance with GPU (recommended)

### Embedding Server Setup

BERTrend provides a ready-to-use embedding server at `bertrend/services/embedding_server/`.

**Quick Start:**
```bash
# Install BERTrend
pip install bertrend

# Set environment variables
export BERTREND_SECRET_KEY=your_secret_key
export DEFAULT_RATE_LIMIT=100
export DEFAULT_RATE_WINDOW=3600

# Run embedding server
python -m bertrend.services.embedding_server.main --port 8765
```

**Configuration:**
The server uses `bertrend/config/services_default_config.toml`:
```toml
[embedding_service]
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embedding_dtype = "float32"
port = 8765

[rate_limiting]
default_rate_limit = 100  # requests per window
default_rate_window = 3600  # 1 hour in seconds
```

**Authentication:**
Clients connect with credentials:
```python
EmbeddingService(
    local=False,
    url="http://embedding-server:8765",
    client_id="bertrend_extraction",
    client_secret="your_secret_key"
)
```

### Docker Configuration

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download sentence-transformers model at build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy application
COPY app/ ./app/

# Expose port
EXPOSE 8001

# Run with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
bertrend==0.1.0
sentence-transformers==2.2.2
bertopic==0.16.0
umap-learn==0.5.5
hdbscan==0.8.33
pandas==2.1.3
numpy==1.26.2
openai==1.3.7
prometheus-client==0.19.0
structlog==23.2.0
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  # Main BERTrend extraction service
  bertrend-service:
    build: .
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - EMBEDDING_SERVER_URL=http://embedding-server:8765
      - EMBEDDING_CLIENT_ID=bertrend_extraction
      - EMBEDDING_CLIENT_SECRET=${EMBEDDING_SECRET}
      - LOG_LEVEL=info
    volumes:
      - ./models:/app/models  # Persist trained models
    depends_on:
      - embedding-server
  
  # BERTrend's embedding server (from bertrend/services/embedding_server/)
  embedding-server:
    build:
      context: .
      dockerfile: Dockerfile.embedding
    ports:
      - "8765:8765"
    environment:
      - BERTREND_SECRET_KEY=${EMBEDDING_SECRET}
      - DEFAULT_RATE_LIMIT=100
      - DEFAULT_RATE_WINDOW=3600
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]  # Optional: GPU for faster embeddings
```

**Dockerfile.embedding:** (for embedding server)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install BERTrend
RUN pip install bertrend sentence-transformers

# Download model at build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Run embedding server
CMD ["python", "-m", "bertrend.services.embedding_server.main"]
```

## Testing Strategy

### Unit Tests

```python
# tests/test_technique_mapper.py

@pytest.mark.asyncio
async def test_exact_matching():
    mapper = TechniqueMapper(api_key="test")
    
    keywords = ["retrieval", "augmented", "generation", "rag"]
    matches = mapper._find_exact_matches(keywords)
    
    assert len(matches) == 1
    assert matches[0].name == "RAG"
    assert matches[0].confidence == 1.0

@pytest.mark.asyncio
async def test_llm_mapping():
    mapper = TechniqueMapper(api_key=os.getenv("OPENAI_API_KEY"))
    
    keywords = ["vision", "language", "multimodal", "image", "text"]
    matches = await mapper._llm_map_topic(keywords)
    
    assert len(matches) > 0
    assert any(m.name == "multi-modal" for m in matches)
```

### Integration Tests

```python
# tests/test_enrichment_pipeline.py

@pytest.mark.asyncio
async def test_full_enrichment_pipeline():
    papers = [
        RawPaper(
            id="test_001",
            title="Multi-Modal RAG with Vision APIs",
            abstract="We present a novel retrieval-augmented generation system...",
            date=datetime.now()
        )
    ]
    
    service = PaperEnrichmentService(topic_service, mapper)
    result = await service.enrich_papers(papers, ExtractionOptions())
    
    assert len(result.papers) == 1
    enriched = result.papers[0]
    
    assert "RAG" in enriched.techniques
    assert "multi-modal" in enriched.techniques
    assert enriched.technique_scores["RAG"] > 0.6
```

## Performance Optimization

### 1. Remote Embedding Server (BERTrend's Approach)

**Benefits:**
- Centralized caching (server handles it internally)
- GPU resource sharing across multiple API workers
- Scales horizontally (multiple extraction services → one embedding server)

**Configuration:**
```python
# In your extraction service
embedding_service = EmbeddingService(
    local=False,
    url="http://embedding-server:8765",
    client_id="bertrend_extraction",
    client_secret=os.getenv("EMBEDDING_SECRET")
)
```

### 2. Batch Processing
```python
# Process papers in optimal batch sizes
OPTIMAL_BATCH_SIZE = 50  # Sweet spot for GPU utilization

async def process_large_corpus(papers: List[RawPaper]):
    results = []
    for batch in chunks(papers, OPTIMAL_BATCH_SIZE):
        batch_result = await enrichment_service.enrich_papers(batch)
        results.extend(batch_result.papers)
    return results
```

### 3. Model Persistence
```python
# Save trained topic models for reuse
bertrend.save_model(models_path="./models/topic_models")

# Later, restore instead of retraining
bertrend = BERTrend.restore_model(models_path="./models/topic_models")
```

## Cost Analysis

### LLM Costs (GPT-4o-mini)

**Per paper:**
- Prompt: ~200 tokens (taxonomy + keywords)
- Response: ~100 tokens (JSON with techniques)
- Cost: $0.00003 per paper

**Monthly costs (10,000 papers/month):**
- Total: $0.30/month

**Very cheap! Most cost is compute, not LLM.**

### Compute Costs (Two-Service Architecture)

**Extraction Service (CPU-only):**
- AWS t3.medium: $30/month
- Handles API requests, topic clustering, technique mapping
- Can run multiple instances for load balancing

**Embedding Server (GPU recommended):**
- AWS g4dn.xlarge: $400/month (with GPU)
- Handles all embedding generation
- Single instance serves multiple extraction services
- Includes in-memory caching

**Alternative (CPU-only, both services):**
- AWS t3.large (2 services): $60/month total
- Slower embeddings (~5x slower)
- Suitable for <5K papers/month

**Total Monthly Cost:**
- With GPU: ~$430/month (extraction $30 + embeddings $400)
- CPU-only: ~$60/month (slower but works)

## Implementation Timeline

### Week 1: Core BERTrend Integration
- Set up BERTrend topic extraction
- Implement embedding service
- Build topic clustering pipeline

### Week 2: Technique Mapping
- Build technique taxonomy
- Implement exact matching
- Integrate LLM for semantic mapping

### Week 3: API & Testing
- FastAPI endpoints
- Unit tests (>85% coverage)
- Integration tests

### Week 4: Optimization & Deployment
- Caching implementation
- Docker packaging
- Production deployment

## Appendix: BERTrend Implementation Reference

### Key BERTrend Files to Study

**Core Classes:**
1. **`bertrend/BERTrend.py`** - Main orchestration class
   - `train_topic_models(grouped_data, embeddings, embedding_model)` - Train on time-sliced data
   - `merge_models_with(other_bertrend, timestamp)` - Merge topics across time
   - `calculate_signal_popularity(decay_factor, decay_power)` - Compute popularity metrics
   - `classify_signals(window_size, current_date)` - Classify as noise/weak/strong
   - `save_model(models_path)` / `restore_model(models_path)` - Persistence

2. **`bertrend/BERTopicModel.py`** - BERTopic wrapper
   - `fit(docs, embeddings, embedding_model)` - Train topic model
   - `get_topics()` - Get topic-keyword mappings
   - `get_document_info(docs)` - Get topic assignments per document
   - `get_topic_info()` - Get topic metadata

3. **`bertrend/services/embedding_service.py`** - Document embedding
   - `EmbeddingService(local=True, model_name="sentence-transformers/...")` - Initialize
   - `embed(texts, verbose=True)` - Generate embeddings + token info
   - Supports both local and remote embedding servers

**Data Utilities:**
4. **`bertrend/utils/data_loading.py`**
   - `load_data(selected_file, language)` - Load and clean CSV/JSON/Parquet
   - `split_data(df, min_chars, split_by_paragraph)` - Split long documents
   - Required columns: `text`, `timestamp`

**Configuration:**
5. **`bertrend/config/bertrend_default_config.toml`**
   ```toml
   granularity = 7  # Days per time slice
   min_similarity = 0.8  # Topic merge threshold
   decay_factor = 0.01  # Popularity decay rate
   decay_power = 2  # Exponential decay
   signal_classif_lower_bound = 15  # Weak signal threshold (percentile)
   signal_classif_upper_bound = 80  # Strong signal threshold (percentile)
   ```

6. **`bertrend/config/bertopic_default_config.toml`**
   ```toml
   [global]
   language = "English"
   
   [bertopic_model]
   top_n_words = 10
   representation_model = ["KeyBERTInspired"]
   
   [hdbscan_model]
   min_cluster_size = 15
   min_samples = 10
   
   [umap_model]
   n_neighbors = 15
   n_components = 5
   
   [vectorizer_model]
   ngram_range = [1, 2]
   ```

### Example Usage Patterns from BERTrend

**Pattern 1: Basic Topic Extraction**
```python
# From: bertrend/demos/weak_signals/app.py (simplified)
from bertrend import BERTrend
from bertrend.BERTopicModel import BERTopicModel
from bertrend.services.embedding_service import EmbeddingService

# Initialize
embedding_service = EmbeddingService(local=True, model_name="all-MiniLM-L6-v2")
bertrend = BERTrend(topic_model=BERTopicModel())

# Prepare data
df['grouped_timestamp'] = pd.to_datetime(df['timestamp']).dt.to_period('7D').dt.to_timestamp()
grouped_data = {ts: group for ts, group in df.groupby('grouped_timestamp')}

# Embed
embeddings, _, _ = embedding_service.embed(df['text'].tolist())

# Train
bertrend.train_topic_models(
    grouped_data=grouped_data,
    embeddings=embeddings,
    embedding_model=embedding_service.embedding_model_name
)

# Get results
topic_model = bertrend.last_topic_model
topics = topic_model.get_topics()
doc_info = topic_model.get_document_info(df['text'].tolist())
```

**Pattern 2: Incremental Training**
```python
# From: bertrend/BERTrend.py - train_new_data()
from bertrend.BERTrend import train_new_data

# For new data arriving
updated_bertrend = train_new_data(
    reference_timestamp=pd.Timestamp("2024-02-01"),
    new_data=new_papers_df,  # Must have 'text' and 'timestamp' columns
    bertrend_models_path=Path("./models"),
    embedding_service=embedding_service,
    granularity=7,
    language="English"
)
```

**Pattern 3: Signal Classification**
```python
# From: getting_started/bertrend_quickstart.ipynb
bertrend.calculate_signal_popularity(decay_factor=0.01, decay_power=2)

noise_df, weak_signals_df, strong_signals_df = bertrend.classify_signals(
    window_size=30,
    current_date=pd.Timestamp("2024-01-15")
)

# weak_signals_df contains: Topic, Representation, Latest_Popularity, etc.
for idx, signal in weak_signals_df.iterrows():
    topic_id = signal['Topic']
    keywords = signal['Representation']
    popularity = signal['Latest_Popularity']
```

**Pattern 4: Model Persistence**
```python
# Save trained model
bertrend.save_model(models_path=Path("./cache/models"))

# Restore later
restored = BERTrend.restore_model(models_path=Path("./cache/models"))

# Restore specific time period
topic_model = BERTrend.restore_topic_model(
    period=pd.Timestamp("2024-01-15"),
    models_path=Path("./cache/models")
)
```

### Common Configuration Patterns

**For Technique Extraction (Our Use Case):**
```python
# Optimize for speed and small clusters
config = {
    "global": {"language": "English"},
    "bertopic_model": {
        "top_n_words": 10,  # Keywords per topic
        "representation_model": ["KeyBERTInspired"]
    },
    "hdbscan_model": {
        "min_cluster_size": 5,  # Lower = more granular topics
        "min_samples": 3        # Lower = more sensitive
    },
    "umap_model": {
        "n_neighbors": 10,      # Lower = local structure
        "n_components": 5       # Dimensionality
    }
}
```

### BERTrend vs Our Implementation

**What we use from BERTrend:**
- ✅ Embedding generation (sentence-transformers)
- ✅ Topic clustering (BERTopic/HDBSCAN)
- ✅ Topic keyword extraction
- ✅ Configuration system

**What we DON'T use from BERTrend:**
- ❌ Time-series topic merging (we process batches)
- ❌ Signal classification (we do our own 4-pass detection)
- ❌ Popularity metrics (we use acceleration/variance)
- ❌ Streamlit demos (we build FastAPI service)

**Our additions:**
- ✅ Technique taxonomy mapping
- ✅ LLM-based validation (GPT-4o-mini)
- ✅ Constitution filtering
- ✅ Integration with deterministic analyzer

### Environment Setup Reference

**Required environment variables (from BERTrend):**
```bash
# From .env
BERTREND_BASE_DIR=/path/to/bertrend/data
OPENAI_API_KEY=sk-...
OPENAI_DEFAULT_MODEL=gpt-4o-mini
CUDA_VISIBLE_DEVICES=0  # Optional: for GPU
```

**BERTrend's directory structure:**
```
$BERTREND_BASE_DIR/
├── data/          # Input datasets
├── cache/
│   ├── models/    # Saved topic models
│   └── embeddings/  # Cached embeddings
└── logs/          # Application logs
```

### Troubleshooting Common Issues

**Issue 1: HDBSCAN finds no clusters**
- **Cause:** `min_cluster_size` too high for dataset
- **Solution:** Lower to 3-5 for small datasets
- **Reference:** `bertrend/config/bertopic_default_config.toml`

**Issue 2: Topics too granular/fragmented**
- **Cause:** `min_cluster_size` too low
- **Solution:** Increase to 10-15
- **Reference:** BERTopic documentation

**Issue 3: Embeddings slow without GPU**
- **Cause:** Local embedding on CPU
- **Solution:** Use smaller model like "all-MiniLM-L6-v2"
- **Reference:** `bertrend/services/embedding_service.py`

**Issue 4: Out of memory during embedding**
- **Cause:** Batch too large
- **Solution:** Process in smaller batches
- **Code:** See chunking in `embedding_service.embed()`

---

## Success Criteria

**Must Have:**
✅ Extracts techniques with >85% precision
✅ Processes 100 papers in <60 seconds
✅ API returns valid enriched papers
✅ Handles edge cases (no abstract, outliers)
✅ Test coverage >85%

**Should Have:**
- Redis caching for embeddings
- Incremental topic model updates
- Technique taxonomy management UI

**Nice to Have:**
- GPU acceleration
- Real-time streaming extraction
- A/B testing for mapping strategies

---

**Next Step:** Ready to start implementation? Let me know and I'll begin building the actual Python code!