"""
AI Technique Extraction Service
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .api import endpoints


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Log Level: {settings.LOG_LEVEL}")
    yield
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title="AI Technique Extraction Service",
    description="Automatically identifies AI techniques from multi-source text content using BERTrend semantic analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(endpoints.router, prefix="/api/v1")

