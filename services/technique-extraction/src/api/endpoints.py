"""
API Endpoints for AI Technique Extraction Service
"""
import logging
from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, status, HTTPException, Depends

from .models import (
    Paper,
    EnrichedPaper,
    HealthCheckResponse,
    ErrorResponse,
    BatchExtractionRequest,
    BatchExtractionResponse,
)
from ..services.extraction_service import ExtractionService
from ..services.embedding_client import EmbeddingClient
from ..services.technique_mapper import TechniqueMapper
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependency injection for services
async def get_extraction_service() -> ExtractionService:
    """Create extraction service instance"""
    async with EmbeddingClient() as embedding_client:
        technique_mapper = TechniqueMapper()
        return ExtractionService(embedding_client, technique_mapper)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns service health status in <100ms (Railway requirement)",
    response_model=HealthCheckResponse,
)
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    
    Returns:
        HealthCheckResponse: Service health status
    """
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        service="ai-technique-extraction",
    )


@router.post(
    "/extract/techniques",
    status_code=status.HTTP_200_OK,
    summary="Extract AI Techniques from Papers",
    description="Synchronously extract AI techniques from academic papers and other content",
    response_model=List[EnrichedPaper],
    responses={
        200: {
            "description": "Successfully extracted techniques",
            "model": List[EnrichedPaper],
        },
        400: {
            "description": "Invalid request (malformed input, validation error)",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error (embedding timeout, processing failure)",
            "model": ErrorResponse,
        },
    },
)
async def extract_techniques(papers: List[Paper]):
    """
    Extract AI techniques from one or more papers
    
    Implements User Story 1 (US1) for academic papers
    
    Args:
        papers: List of papers to process (1-10 for synchronous processing)
        
    Returns:
        List of EnrichedPaper objects with extracted techniques
        
    Raises:
        HTTPException 400: Malformed input (Tier 3 error)
        HTTPException 500: Server error (Tier 2 error after retries)
    """
    request_id = uuid4()
    
    try:
        # Validate batch size for synchronous processing
        if len(papers) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_type": "validation_error",
                    "error_message": "Synchronous processing limited to 10 papers. Use batch endpoint for larger requests.",
                    "request_id": str(request_id),
                }
            )
        
        # Process each paper
        results = []
        
        async with EmbeddingClient() as embedding_client:
            technique_mapper = TechniqueMapper()
            extraction_service = ExtractionService(embedding_client, technique_mapper)
            
            for paper in papers:
                try:
                    # Tier 3: Malformed input validation
                    if not paper.text or len(paper.text.strip()) < 50:
                        logger.warning(f"Skipping paper {paper.paper_id}: text too short")
                        continue
                    
                    # Extract techniques
                    enriched = await extraction_service.extract_techniques_sync(
                        paper_id=paper.paper_id,
                        title=paper.title,
                        text=paper.text,
                        source_type=paper.source_type,
                    )
                    
                    results.append(EnrichedPaper(**enriched))
                    
                except TimeoutError as e:
                    # Tier 2: Timeout after retries
                    logger.error(f"Timeout for paper {paper.paper_id}: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "error_type": "timeout_error",
                            "error_message": f"Embedding server timeout after retries: {str(e)}",
                            "paper_id": paper.paper_id,
                            "request_id": str(request_id),
                        }
                    )
                
                except ValueError as e:
                    # Tier 3: Validation error
                    logger.error(f"Validation error for paper {paper.paper_id}: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error_type": "validation_error",
                            "error_message": str(e),
                            "paper_id": paper.paper_id,
                            "request_id": str(request_id),
                        }
                    )
                
                except Exception as e:
                    # Tier 2: Unexpected server error
                    logger.error(f"Processing error for paper {paper.paper_id}: {e}", exc_info=True)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "error_type": "processing_error",
                            "error_message": str(e),
                            "paper_id": paper.paper_id,
                            "request_id": str(request_id),
                        }
                    )
        
        # Tier 1: No techniques found - return empty list (not an error)
        if not results:
            logger.debug(f"No techniques found for request {request_id}")
        
        return results
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "internal_error",
                "error_message": "An unexpected error occurred",
                "request_id": str(request_id),
            }
        )

