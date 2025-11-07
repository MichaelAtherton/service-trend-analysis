"""
FastAPI Embedding Server - Wrapper around BERTrend
Exposes BERTrend's embedding capabilities as a REST API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global embedding model (loaded at startup)
embedding_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global embedding_model
    
    # Startup: Load BERTrend embedding model
    logger.info("Loading BERTrend embedding model...")
    try:
        from sentence_transformers import SentenceTransformer
        
        # Use the same model that BERTrend uses internally
        # BERTrend typically uses 'all-MiniLM-L6-v2' or similar
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        embedding_model = SentenceTransformer(model_name)
        logger.info(f"✅ Embedding model loaded: {model_name}")
        
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        raise
    
    yield
    
    # Shutdown: Cleanup
    logger.info("Shutting down embedding server...")


# Create FastAPI app
app = FastAPI(
    title="BERTrend Embedding Service",
    description="REST API for semantic embeddings using BERTrend's embedding model",
    version="0.1.0",
    lifespan=lifespan
)


# Request/Response Models
class EmbedRequest(BaseModel):
    """Request model for embedding generation"""
    texts: List[str] = Field(
        ...,
        description="List of texts to embed",
        example=["This paper discusses transformers", "BERT is a language model"]
    )
    normalize: bool = Field(
        default=True,
        description="Whether to normalize embeddings to unit length"
    )


class EmbedResponse(BaseModel):
    """Response model for embedding generation"""
    embeddings: List[List[float]] = Field(
        ...,
        description="List of embedding vectors (one per input text)"
    )
    model: str = Field(
        ...,
        description="Name of the embedding model used"
    )
    dimension: int = Field(
        ...,
        description="Dimensionality of each embedding vector"
    )


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., example="healthy")
    model_loaded: bool = Field(..., example=True)
    model_name: Optional[str] = Field(None, example="all-MiniLM-L6-v2")


# API Endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns 200 if service is ready, 503 if model not loaded
    """
    if embedding_model is None:
        raise HTTPException(
            status_code=503,
            detail="Embedding model not loaded"
        )
    
    return HealthResponse(
        status="healthy",
        model_loaded=True,
        model_name=embedding_model.get_sentence_embedding_dimension().__class__.__name__
    )


@app.post("/embed", response_model=EmbedResponse, tags=["Embeddings"])
async def generate_embeddings(request: EmbedRequest):
    """
    Generate embeddings for input texts
    
    - **texts**: List of text strings to embed (max 1000 texts per request)
    - **normalize**: Whether to normalize embeddings (recommended: True)
    
    Returns embedding vectors with shape (num_texts, embedding_dim)
    """
    if embedding_model is None:
        raise HTTPException(
            status_code=503,
            detail="Embedding model not loaded"
        )
    
    if not request.texts:
        raise HTTPException(
            status_code=400,
            detail="No texts provided"
        )
    
    if len(request.texts) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Maximum 1000 texts per request"
        )
    
    try:
        # Generate embeddings
        embeddings = embedding_model.encode(
            request.texts,
            normalize_embeddings=request.normalize,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Convert to list of lists for JSON serialization
        embeddings_list = embeddings.tolist()
        
        return EmbedResponse(
            embeddings=embeddings_list,
            model=embedding_model._model_card_text.split('\n')[0] if hasattr(embedding_model, '_model_card_text') else "sentence-transformers/all-MiniLM-L6-v2",
            dimension=len(embeddings_list[0])
        )
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Embedding generation failed: {str(e)}"
        )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service info"""
    return {
        "service": "BERTrend Embedding Service",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "embed": "/embed",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8765,
        log_level="info"
    )

