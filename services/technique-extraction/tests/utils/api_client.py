"""
API client helper for calling the extraction service during tests.

Provides async functions for:
- Calling extraction endpoint
- Handling retries for transient failures
- Managing rate limits
"""

import asyncio
from typing import Any

import httpx


class ExtractionAPIClient:
    """Async HTTP client for interacting with the AI Technique Extraction Service."""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the extraction service (e.g., "http://localhost:8000")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
    
    async def health_check(self) -> dict[str, Any]:
        """
        Call the health check endpoint.
        
        Returns:
            dict: Health check response
        
        Raises:
            httpx.HTTPStatusError: If response status is not 2xx
        """
        response = await self.client.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()
        return response.json()
    
    async def extract_techniques(
        self,
        papers: list[dict[str, Any]],
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> list[dict[str, Any]]:
        """
        Call the extraction endpoint with retry logic.
        
        Args:
            papers: List of paper objects with paper_id, title, text, source_type
            max_retries: Maximum number of retry attempts for retriable errors
            retry_delay: Base delay between retries (exponential backoff)
        
        Returns:
            list: List of enriched paper dictionaries
        
        Raises:
            httpx.HTTPStatusError: If response status is not 2xx after retries
        """
        payload = papers  # API expects a list directly, not wrapped in {"papers": ...}
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/extract/techniques",
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                # Retry on 5xx errors or 429 (rate limit)
                if e.response.status_code >= 500 or e.response.status_code == 429:
                    if attempt < max_retries:
                        wait_time = retry_delay * (2 ** attempt)
                        await asyncio.sleep(wait_time)
                        continue
                raise
            
            except httpx.TimeoutException:
                # Retry on timeout
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)
                    await asyncio.sleep(wait_time)
                    continue
                raise
        
        # Should not reach here, but for type checker
        raise RuntimeError("Unexpected code path in extract_techniques")
    
    async def extract_single_paper(
        self,
        paper_id: str,
        title: str,
        text: str,
        source_type: str = "academic",
    ) -> dict[str, Any]:
        """
        Extract techniques from a single paper.
        
        Args:
            paper_id: Unique paper identifier
            title: Paper title
            text: Paper text content
            source_type: Source type (academic, blog, press_release, etc.)
        
        Returns:
            dict: Single enriched paper result
        """
        papers = [
            {
                "paper_id": paper_id,
                "title": title,
                "text": text,
                "source_type": source_type,
            }
        ]
        
        # API returns a list of EnrichedPaper objects directly
        response = await self.extract_techniques(papers)
        
        if not response or not isinstance(response, list):
            raise ValueError(f"Unexpected response format for paper {paper_id}")
        
        if not response:
            raise ValueError(f"No results returned for paper {paper_id}")
        
        return response[0]

