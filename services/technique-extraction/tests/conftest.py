"""
pytest configuration and shared fixtures for MVP testing suite.

This module provides session-scoped fixtures for:
- Test fixtures directory access
- Sample paper metadata loading
- Sample paper content loading
- API client instances
- Cost tracking for OpenAI API usage
"""

import json
import os
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def metadata(fixtures_dir: Path) -> dict[str, Any]:
    """Load and return sample paper metadata from metadata.json."""
    metadata_path = fixtures_dir / "metadata.json"
    if not metadata_path.exists():
        pytest.skip(f"Metadata file not found: {metadata_path}")
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def sample_papers(fixtures_dir: Path, metadata: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    Load all sample papers and return as dict mapping paper_id to paper data.
    
    Returns:
        dict: {
            "paper_001": {
                "metadata": {...},  # from metadata.json
                "text": "...",      # from paper file
            },
            ...
        }
    """
    papers = {}
    
    for paper_meta in metadata.get("papers", []):
        paper_id = paper_meta["paper_id"]
        file_path = fixtures_dir / paper_meta["file_path"]
        
        if not file_path.exists():
            pytest.skip(f"Paper file not found: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        papers[paper_id] = {
            "metadata": paper_meta,
            "text": text,
        }
    
    return papers


@pytest.fixture
def openai_api_key() -> str:
    """
    Return OpenAI API key from environment.
    
    Skip tests if OPENAI_API_KEY is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    return api_key


@pytest.fixture
def extraction_service_url() -> str:
    """Return the extraction service URL from environment or default."""
    return os.getenv("EXTRACTION_SERVICE_URL", "http://localhost:8000")


@pytest.fixture
def embedding_server_url() -> str:
    """Return the embedding server URL from environment or default."""
    return os.getenv("EMBEDDING_SERVER_URL", "http://localhost:8765")


# Cost tracking fixture (T024)
@pytest.fixture(scope="session")
def cost_tracker():
    """
    Session-scoped cost tracker for OpenAI API usage.
    
    Tracks API calls and costs across entire test suite execution.
    Prints summary at end of session.
    """
    from tests.utils.cost_tracker import CostTracker
    from datetime import datetime
    
    tracker = CostTracker(
        suite_run_id=f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    yield tracker
    
    # Print summary at end of session
    if tracker.total_calls > 0:
        tracker.print_summary()


# Paper-specific fixtures for targeted test access (T026)
@pytest.fixture
def rag_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return RAG paper (paper_001) for targeted testing."""
    return sample_papers.get("paper_001", {})


@pytest.fixture
def rlhf_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return RLHF paper (paper_002) for targeted testing."""
    return sample_papers.get("paper_002", {})


@pytest.fixture
def finetuning_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return fine-tuning paper (paper_003) for targeted testing."""
    return sample_papers.get("paper_003", {})


@pytest.fixture
def transformers_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return transformers paper (paper_004) for targeted testing."""
    return sample_papers.get("paper_004", {})


@pytest.fixture
def diffusion_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return diffusion paper (paper_005) for targeted testing."""
    return sample_papers.get("paper_005", {})


@pytest.fixture
def multimodal_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return multi-modal paper (paper_006) for targeted testing."""
    return sample_papers.get("paper_006", {})


@pytest.fixture
def quantization_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return quantization paper (paper_007) for targeted testing."""
    return sample_papers.get("paper_007", {})


@pytest.fixture
def prompting_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return prompt engineering paper (paper_008) for targeted testing."""
    return sample_papers.get("paper_008", {})


@pytest.fixture
def evaluation_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return evaluation paper (paper_009) for targeted testing."""
    return sample_papers.get("paper_009", {})


@pytest.fixture
def agents_paper(sample_papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return AI agents paper (paper_010) for targeted testing."""
    return sample_papers.get("paper_010", {})

