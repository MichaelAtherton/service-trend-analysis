"""
Pydantic Request/Response Models
Defines API data structures with validation and OpenAPI documentation
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class TextSnippet(BaseModel):
    """Text snippet showing where technique was mentioned"""
    snippet: str = Field(
        description="50-character context window around technique mention",
        example="...uses retrieval-augmented generation (RAG) to enhance..."
    )
    start_char: int = Field(
        description="Starting character position in original text",
        example=1234
    )
    end_char: int = Field(
        description="Ending character position in original text",
        example=1284
    )


class TechniqueMatch(BaseModel):
    """Extracted AI technique with confidence and context"""
    technique_name: str = Field(
        description="Standardized technique name from taxonomy",
        example="Retrieval-Augmented Generation"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0) based on source quality and frequency",
        example=0.87
    )
    context_type: Literal["production", "research", "tutorial", "criticism", "general"] = Field(
        description="Context in which technique is mentioned",
        example="production"
    )
    newly_discovered: bool = Field(
        description="True if technique is not in canonical taxonomy (requires manual review)",
        example=False
    )
    text_snippets: List[TextSnippet] = Field(
        default_factory=list,
        description="Up to 3 text snippets showing where technique is mentioned",
        max_length=3
    )


class Paper(BaseModel):
    """Input paper for technique extraction"""
    paper_id: str = Field(
        description="Unique identifier for this paper/content item",
        example="arxiv_2024_12345"
    )
    title: str = Field(
        description="Paper or article title",
        example="Advances in Retrieval-Augmented Generation for Question Answering"
    )
    text: str = Field(
        description="Full text content (abstracts, body, etc.)",
        example="Abstract: This paper presents novel approaches to RAG systems..."
    )
    source_type: Literal["academic", "blog", "press_release", "podcast", "social"] = Field(
        default="academic",
        description="Content source type (affects confidence scoring)",
        example="academic"
    )
    
    @field_validator("text")
    @classmethod
    def validate_text_length(cls, v: str) -> str:
        """Ensure text is not empty and has reasonable length"""
        if not v or not v.strip():
            raise ValueError("text cannot be empty")
        if len(v.strip()) < 50:
            raise ValueError("text must be at least 50 characters")
        return v


class ConfidenceDistribution(BaseModel):
    """Statistical distribution of confidence scores"""
    avg: float = Field(
        description="Average confidence across all techniques",
        example=0.85
    )
    min: float = Field(
        description="Minimum confidence score",
        example=0.65
    )
    max: float = Field(
        description="Maximum confidence score",
        example=0.95
    )


class EnrichedPaper(BaseModel):
    """Output paper with extracted techniques and metadata"""
    paper_id: str = Field(
        description="Original paper identifier",
        example="arxiv_2024_12345"
    )
    title: str = Field(
        description="Paper title",
        example="Advances in Retrieval-Augmented Generation for Question Answering"
    )
    source_type: str = Field(
        description="Content source type",
        example="academic"
    )
    techniques: List[TechniqueMatch] = Field(
        description="List of extracted techniques (up to 5 per paper)",
        max_length=5
    )
    expected_accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="Expected extraction accuracy based on source type (academic=0.95, blog=0.90, press=0.85, podcast=0.80, social=0.70)",
        example=0.95
    )
    processing_duration_ms: float = Field(
        description="Total processing time in milliseconds",
        example=8543.21
    )
    total_techniques_found: int = Field(
        description="Total number of techniques extracted",
        example=3
    )
    confidence_distribution: ConfidenceDistribution = Field(
        description="Statistical distribution of confidence scores"
    )


class BatchExtractionRequest(BaseModel):
    """Request to extract techniques from multiple papers"""
    papers: List[Paper] = Field(
        description="List of papers to process",
        min_length=1,
        max_length=100
    )
    
    @field_validator("papers")
    @classmethod
    def validate_batch_size(cls, v: List[Paper]) -> List[Paper]:
        """Enforce batch size limits"""
        if len(v) > 100:
            raise ValueError("Batch size cannot exceed 100 papers")
        return v


class BatchExtractionResponse(BaseModel):
    """Response with extraction results for multiple papers"""
    job_id: str = Field(
        description="Unique job identifier for async tracking",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        description="Current job status",
        example="completed"
    )
    total_papers: int = Field(
        description="Total number of papers in batch",
        example=10
    )
    processed_papers: int = Field(
        description="Number of papers successfully processed",
        example=9
    )
    failed_papers: int = Field(
        description="Number of papers that failed processing",
        example=1
    )
    results: List[EnrichedPaper] = Field(
        default_factory=list,
        description="List of enriched papers with extracted techniques"
    )


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        description="Service health status",
        example="healthy"
    )
    version: str = Field(
        description="Application version",
        example="0.1.0"
    )
    timestamp: str = Field(
        description="Current ISO 8601 timestamp",
        example="2025-11-03T12:34:56.789Z"
    )
    service: str = Field(
        description="Service identifier",
        example="ai-technique-extraction"
    )


class ErrorResponse(BaseModel):
    """Error response structure"""
    error_type: str = Field(
        description="Error classification (validation_error, processing_error, timeout_error)",
        example="validation_error"
    )
    error_message: str = Field(
        description="Human-readable error message",
        example="Invalid paper format: text field is required"
    )
    paper_id: Optional[str] = Field(
        default=None,
        description="Paper ID if error is specific to one paper",
        example="arxiv_2024_12345"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request UUID for traceability",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

