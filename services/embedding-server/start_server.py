#!/usr/bin/env python3
"""
BERTrend Embedding Server Launcher
Starts the FastAPI embedding service on port 8765 for remote semantic embeddings
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_embedding_server():
    """Launch FastAPI embedding service"""
    try:
        import uvicorn
        
        # Configuration
        port = int(os.getenv("EMBEDDING_SERVER_PORT", "8765"))
        host = os.getenv("EMBEDDING_SERVER_HOST", "0.0.0.0")
        log_level = os.getenv("LOG_LEVEL", "info").lower()
        
        logger.info(f"Starting BERTrend embedding server on {host}:{port}")
        logger.info(f"Log level: {log_level}")
        
        # Start FastAPI server using uvicorn
        uvicorn.run(
            "app:app",  # Import path to FastAPI app
            host=host,
            port=port,
            log_level=log_level,
            reload=False,  # Disable reload for production
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"Failed to import required packages: {e}")
        logger.error("Make sure dependencies are installed: pip install fastapi uvicorn sentence-transformers")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start embedding server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_embedding_server()

