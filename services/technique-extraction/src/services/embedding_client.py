"""
Async Embedding Client
Wrapper for BERTrend embedding server with retry logic
"""
import asyncio
import logging
from typing import List, Optional

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Async client for BERTrend embedding server with exponential backoff retry"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Initialize embedding client
        
        Args:
            base_url: Embedding server URL (defaults to settings)
            client_id: Client ID for authentication
            client_secret: Client secret for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for Tier 2 errors
        """
        self.base_url = base_url or settings.EMBEDDING_SERVER_URL
        self.client_id = client_id or settings.EMBEDDING_CLIENT_ID
        self.client_secret = client_secret or settings.EMBEDDING_CLIENT_SECRET
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            headers={
                "X-Client-ID": self.client_id,
                "X-Client-Secret": self.client_secret,
            },
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed list of texts using BERTrend embedding server
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each is a list of floats)
            
        Raises:
            httpx.HTTPError: On non-retriable errors (Tier 3)
            TimeoutError: After max retries exhausted
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Embedding {len(texts)} texts (attempt {attempt + 1}/{self.max_retries})")
                
                response = await self._client.post(
                    "/embed",
                    json={"texts": texts},
                )
                
                # Tier 3: Non-retriable errors (auth failures, bad request)
                if response.status_code in [400, 401, 403]:
                    logger.error(f"Non-retriable error: {response.status_code}")
                    response.raise_for_status()
                
                # Tier 2: Retriable errors (server errors)
                if response.status_code >= 500:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(
                            f"Server error {response.status_code}, "
                            f"retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Failed after {self.max_retries} attempts")
                        response.raise_for_status()
                
                response.raise_for_status()
                result = response.json()
                return result.get("embeddings", [])
                
            except httpx.TimeoutException:
                # Tier 2: Retriable timeout errors
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Timeout, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Timeout after {self.max_retries} attempts")
                    raise TimeoutError(f"Embedding server timeout after {self.max_retries} attempts")
            
            except httpx.HTTPError as e:
                # Tier 3: Non-retriable HTTP errors
                logger.error(f"HTTP error: {e}")
                raise
        
        raise RuntimeError("Unexpected retry loop exit")

