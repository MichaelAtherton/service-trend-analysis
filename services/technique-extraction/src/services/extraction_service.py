"""
Main Extraction Orchestration Service
Coordinates the end-to-end technique extraction pipeline
"""
import logging
import time
import re
from typing import List, Dict, Any
from uuid import UUID, uuid4

from ..preprocessing.academic import clean_academic, should_split_document
from ..services.embedding_client import EmbeddingClient
from ..services.bertrend_service import BERTrendService
from ..services.technique_mapper import TechniqueMapper
from ..utils.logging import log_extraction_operation

logger = logging.getLogger(__name__)


class ExtractionService:
    """
    Orchestrates the complete extraction pipeline:
    1. Preprocess text (academic.py)
    2. Get embeddings (embedding_client.py)
    3. Cluster topics (bertrend_service.py)
    4. Map techniques (technique_mapper.py)
    5. Extract text snippets (FR-010)
    6. Return EnrichedPaper
    """
    
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        technique_mapper: TechniqueMapper
    ):
        """
        Initialize extraction service
        
        Args:
            embedding_client: Client for embedding server
            technique_mapper: Technique mapping service
        """
        self.embedding_client = embedding_client
        self.bertrend_service = BERTrendService(embedding_client)
        self.technique_mapper = technique_mapper
    
    async def extract_techniques_sync(
        self,
        paper_id: str,
        title: str,
        text: str,
        source_type: str = "academic"
    ) -> Dict[str, Any]:
        """
        Extract techniques from a single paper (synchronous processing)
        
        Args:
            paper_id: Unique paper identifier
            title: Paper title
            text: Full paper text
            source_type: Content source type (academic/blog/press_release/podcast/social)
            
        Returns:
            EnrichedPaper dictionary with extracted techniques
        """
        request_id = uuid4()
        start_time = time.time()
        
        try:
            # Phase 1: Preprocess
            logger.info(f"Starting extraction for paper_id={paper_id}")
            log_extraction_operation(
                logger, "INFO", "Starting extraction",
                request_id=request_id, paper_id=paper_id,
                source_type=source_type, phase="preprocess"
            )
            
            cleaned_text = clean_academic(text)
            
            if should_split_document(cleaned_text):
                logger.warning(f"Document {paper_id} >50k words, needs splitting")
                # TODO: Implement BERTrend split_data() for large documents
            
            # Phase 2: Embed
            log_extraction_operation(
                logger, "INFO", "Embedding text",
                request_id=request_id, paper_id=paper_id,
                phase="embed"
            )
            
            # Split into paragraphs for embedding
            paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]
            if not paragraphs:
                paragraphs = [cleaned_text]
            
            # Phase 3: Cluster topics
            log_extraction_operation(
                logger, "INFO", "Clustering topics",
                request_id=request_id, paper_id=paper_id,
                phase="cluster"
            )
            
            topics = await self.bertrend_service.cluster_topics(paragraphs)
            
            # Phase 4: Map techniques
            log_extraction_operation(
                logger, "INFO", "Mapping techniques",
                request_id=request_id, paper_id=paper_id,
                phase="map"
            )
            
            techniques = self.technique_mapper.map_topics_to_techniques(
                topics, cleaned_text, source_type
            )
            
            # Phase 5: Extract text snippets (T017a - FR-010)
            for technique in techniques:
                technique["text_snippets"] = self._extract_text_snippets(
                    cleaned_text,
                    technique["technique_name"],
                    max_snippets=3
                )
            
            # Calculate metrics
            duration_ms = (time.time() - start_time) * 1000
            confidences = [t["confidence"] for t in techniques]
            
            # Calculate expected accuracy (T018a - FR-016)
            expected_accuracy = self._calculate_expected_accuracy(source_type)
            
            # Log completion
            log_extraction_operation(
                logger, "INFO", "Extraction complete",
                request_id=request_id, paper_id=paper_id,
                source_type=source_type, duration_ms=duration_ms,
                technique_count=len(techniques),
                confidence_avg=sum(confidences) / len(confidences) if confidences else 0.0,
                confidence_min=min(confidences) if confidences else 0.0,
                confidence_max=max(confidences) if confidences else 0.0
            )
            
            return {
                "paper_id": paper_id,
                "title": title,
                "source_type": source_type,
                "techniques": techniques,
                "expected_accuracy": expected_accuracy,
                "processing_duration_ms": round(duration_ms, 2),
                "total_techniques_found": len(techniques),
                "confidence_distribution": {
                    "avg": round(sum(confidences) / len(confidences), 3) if confidences else 0.0,
                    "min": round(min(confidences), 3) if confidences else 0.0,
                    "max": round(max(confidences), 3) if confidences else 0.0,
                }
            }
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            log_extraction_operation(
                logger, "ERROR", f"Extraction failed: {str(e)}",
                request_id=request_id, paper_id=paper_id,
                source_type=source_type, duration_ms=duration_ms,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            raise
    
    @staticmethod
    def _extract_text_snippets(
        text: str,
        technique_name: str,
        max_snippets: int = 3,
        context_window: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Extract text snippets showing where technique is mentioned (T017a - FR-010)
        
        Args:
            text: Full text
            technique_name: Technique to find
            max_snippets: Maximum snippets to return
            context_window: Characters before/after mention (default 25 for 50-char total)
            
        Returns:
            List of snippet dictionaries:
                {
                    "snippet": str (50 chars),
                    "start_char": int,
                    "end_char": int
                }
        """
        snippets = []
        text_lower = text.lower()
        technique_lower = technique_name.lower()
        
        # Find all occurrences
        start = 0
        while len(snippets) < max_snippets:
            pos = text_lower.find(technique_lower, start)
            if pos == -1:
                break
            
            # Extract context window
            snippet_start = max(0, pos - context_window)
            snippet_end = min(len(text), pos + len(technique_name) + context_window)
            snippet_text = text[snippet_start:snippet_end]
            
            # Clean up snippet
            snippet_text = snippet_text.strip()
            if len(snippet_text) > 100:  # Limit to reasonable length
                snippet_text = snippet_text[:100] + "..."
            
            snippets.append({
                "snippet": snippet_text,
                "start_char": snippet_start,
                "end_char": snippet_end
            })
            
            start = pos + len(technique_name)
        
        return snippets
    
    @staticmethod
    def _calculate_expected_accuracy(source_type: str) -> float:
        """
        Calculate expected accuracy based on source type (T018a - FR-016)
        
        Args:
            source_type: Content source type
            
        Returns:
            Expected accuracy (0.0-1.0)
        """
        accuracy_map = {
            "academic": 0.95,
            "blog": 0.90,
            "press_release": 0.85,
            "podcast": 0.80,
            "social": 0.70,
        }
        return accuracy_map.get(source_type, 0.85)  # Default to 0.85

