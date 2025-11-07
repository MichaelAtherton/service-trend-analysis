"""
BERTrend Service Wrapper
Manages topic clustering using BERTrend's neural topic modeling
"""
import logging
import numpy as np
from typing import List, Dict, Any, Optional

from bertrend.BERTopicModel import BERTopicModel

from ..services.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)


class BERTrendService:
    """
    Wrapper for BERTrend topic modeling
    
    Uses UMAP for dimensionality reduction, HDBSCAN for clustering,
    and C-TF-IDF for keyword extraction to identify granular topics
    """
    
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        min_cluster_size: int = 5,
        min_samples: int = 3,
        umap_n_neighbors: int = 10,
        umap_n_components: int = 5,
    ):
        """
        Initialize BERTrend service
        
        Args:
            embedding_client: Client for getting embeddings from server
            min_cluster_size: Minimum cluster size for HDBSCAN (granular topics)
            min_samples: Minimum samples for HDBSCAN core points
            umap_n_neighbors: UMAP neighbors parameter
            umap_n_components: UMAP output dimensions
        """
        self.embedding_client = embedding_client
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.umap_n_neighbors = umap_n_neighbors
        self.umap_n_components = umap_n_components
    
    async def cluster_topics(
        self,
        texts: List[str],
        n_topics: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Cluster texts into topics using BERTrend's UMAP + HDBSCAN + C-TF-IDF pipeline
        
        Args:
            texts: List of text segments to cluster (paragraphs from papers)
            n_topics: Target number of topics (optional, auto-detected if None)
            
        Returns:
            List of topic dictionaries with structure:
                {
                    "topic_id": int,
                    "keywords": List[str],  # Multi-word phrases from C-TF-IDF
                    "documents": List[int],  # Document indices
                    "score": float  # Topic coherence score
                }
        """
        try:
            logger.info(f"Clustering {len(texts)} texts into topics using BERTrend")
            
            # Get embeddings from remote server
            embeddings_list = await self.embedding_client.embed_texts(texts)
            embeddings = np.array(embeddings_list)
            
            logger.debug(f"Embeddings shape: {embeddings.shape}")
            
            # Check if we have enough data for clustering
            min_docs_needed = max(self.min_cluster_size * 2, self.umap_n_components + 1)
            
            if len(texts) < min_docs_needed:
                logger.warning(
                    f"Only {len(texts)} paragraphs, using fallback extraction "
                    f"(BERTrend requires {min_docs_needed}+ for proper clustering)"
                )
                return self._fallback_extraction(texts, embeddings)
            
            # Create BERTrend configuration optimized for technique extraction
            config = self._create_bertrend_config(len(texts))
            
            # Initialize and fit BERTopic model
            logger.debug("Initializing BERTopicModel with custom config")
            topic_model = BERTopicModel(config=config)
            
            logger.debug("Fitting BERTopic model")
            result = topic_model.fit(texts, embeddings)
            
            # Extract topics with keywords
            topics = self._extract_topics_from_model(result, texts)
            
            logger.info(f"BERTrend identified {len(topics)} topics")
            return topics
            
        except Exception as e:
            logger.error(f"Topic clustering failed: {e}", exc_info=True)
            # Fallback to simple extraction on error
            logger.warning("Falling back to simple extraction due to clustering error")
            try:
                embeddings_list = await self.embedding_client.embed_texts(texts)
                embeddings = np.array(embeddings_list)
                return self._fallback_extraction(texts, embeddings)
            except Exception as fallback_error:
                logger.error(f"Fallback extraction also failed: {fallback_error}")
                raise
    
    def _create_bertrend_config(self, n_docs: int) -> Dict[str, Any]:
        """
        Create BERTrend configuration optimized for AI technique extraction
        
        Args:
            n_docs: Number of documents (used to tune parameters)
            
        Returns:
            Configuration dictionary for BERTopicModel
        """
        # Adjust parameters based on dataset size
        min_cluster_size = min(self.min_cluster_size, max(3, n_docs // 20))
        min_samples = min(self.min_samples, max(2, n_docs // 50))
        n_neighbors = min(self.umap_n_neighbors, n_docs - 1)
        
        return {
            "global": {
                "language": "English"  # AI papers are in English
            },
            "umap_model": {
                "n_neighbors": n_neighbors,
                "n_components": self.umap_n_components,
                "min_dist": 0.0,
                "metric": "cosine",
                "random_state": 42
            },
            "hdbscan_model": {
                "min_cluster_size": min_cluster_size,
                "min_samples": min_samples,
                "metric": "euclidean",
                "cluster_selection_method": "eom",
                "prediction_data": True
            },
            "vectorizer_model": {
                "ngram_range": [1, 4],  # Capture multi-word techniques (e.g., "Low-Rank Adaptation")
                "stop_words": None,  # Don't remove words (techniques may include common words)
                "min_df": 1  # Include rare terms (some techniques appear once)
            },
            "bertopic_model": {
                "top_n_words": 10,
                "verbose": False,
                "zeroshot_topic_list": [],
                "zeroshot_min_similarity": 0
            },
            "ctfidf_model": {
                "bm25_weighting": False,
                "reduce_frequent_words": True
            }
        }
    
    def _extract_topics_from_model(
        self,
        result,
        texts: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract topics and keywords from fitted BERTopicModel
        
        Args:
            result: BERTopicModelOutput from BERTopicModel.fit()
            texts: Original text documents
            
        Returns:
            List of topic dictionaries with multi-word keywords
        """
        topics = []
        topic_model = result.topic_model
        topic_assignments = result.topics
        
        # Get topic information
        try:
            topic_info = topic_model.get_topic_info()
            topic_keywords = topic_model.get_topics()
            
            # Process each topic (skip outlier topic -1)
            for topic_id in topic_info['Topic'].unique():
                if topic_id == -1:
                    continue  # Skip outliers
                
                # Get keywords for this topic (C-TF-IDF extracts multi-word phrases)
                if topic_id in topic_keywords:
                    word_scores = topic_keywords[topic_id]
                    # Extract top keywords (includes multi-word phrases!)
                    keywords = [word for word, score in word_scores[:10]]
                    
                    # Get documents belonging to this topic
                    doc_indices = [
                        i for i, assigned_topic in enumerate(topic_assignments)
                        if assigned_topic == topic_id
                    ]
                    
                    # Calculate topic coherence score (average of top word scores)
                    avg_score = np.mean([score for word, score in word_scores[:5]])
                    
                    topics.append({
                        "topic_id": topic_id,
                        "keywords": keywords,
                        "documents": doc_indices,
                        "score": float(avg_score)
                    })
            
            logger.debug(f"Extracted {len(topics)} non-outlier topics")
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}", exc_info=True)
            # Return empty list on error
            return []
        
        return topics
    
    def _fallback_extraction(
        self,
        texts: List[str],
        embeddings: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Fallback extraction for small datasets (< min_docs_needed)
        
        Uses simple n-gram extraction without clustering
        
        Args:
            texts: List of text paragraphs
            embeddings: Text embeddings (unused in fallback)
            
        Returns:
            List of topic dictionaries with n-gram keywords
        """
        import re
        from collections import Counter
        
        logger.info("Using fallback n-gram extraction (no clustering)")
        
        # Extract all n-grams (1-4 words) from all texts
        all_ngrams = []
        
        for text in texts:
            # Clean text
            text_clean = re.sub(r'[^\w\s-]', ' ', text.lower())
            words = text_clean.split()
            
            # Extract n-grams (1 to 4 words)
            for n in range(1, 5):
                for i in range(len(words) - n + 1):
                    ngram = ' '.join(words[i:i+n])
                    # Filter: must be longer than 3 chars and not all stopwords
                    if len(ngram) > 3 and not all(w in {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'of', 'in', 'on', 'at', 'to', 'for'} for w in words[i:i+n]):
                        all_ngrams.append(ngram)
        
        # Count n-gram frequency
        ngram_counts = Counter(all_ngrams)
        
        # Get top n-grams
        top_ngrams = [ngram for ngram, count in ngram_counts.most_common(30)]
        
        # Create a single "topic" with all top n-grams as keywords
        # (technique mapper will match these against taxonomy)
        topics = [{
            "topic_id": 0,
            "keywords": top_ngrams,
            "documents": list(range(len(texts))),
            "score": 0.5
        }]
        
        logger.debug(f"Fallback extracted {len(top_ngrams)} n-grams as keywords")
        
        return topics
    
    def get_topic_keywords(self, topics: List[Dict[str, Any]]) -> Dict[int, List[str]]:
        """
        Extract keywords for each topic
        
        Args:
            topics: List of topic dictionaries
            
        Returns:
            Mapping of topic_id -> keywords
        """
        return {
            topic["topic_id"]: topic["keywords"]
            for topic in topics
        }

