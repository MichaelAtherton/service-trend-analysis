"""
Two-Stage Technique Mapper
Maps topic keywords to standardized technique names using:
1. Exact matching against taxonomy
2. LLM validation for ambiguous cases
"""
import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

import openai

from ..config import settings

logger = logging.getLogger(__name__)


class TechniqueMapper:
    """
    Maps extracted topics to standardized technique names
    
    Implements two-stage mapping:
    - Stage 1: Fast exact matching against taxonomy aliases
    - Stage 2: LLM validation (GPT-4o-mini) for ambiguous topics
    """
    
    def __init__(self, taxonomy_path: Optional[Path] = None):
        """
        Initialize technique mapper with taxonomy
        
        Args:
            taxonomy_path: Path to taxonomy.json file
        """
        if taxonomy_path is None:
            taxonomy_path = Path(__file__).parent.parent / "data" / "taxonomy.json"
        
        self.taxonomy = self._load_taxonomy(taxonomy_path)
        self.alias_map = self._build_alias_map()
        
        # Initialize OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
    
    def _load_taxonomy(self, path: Path) -> Dict[str, Dict[str, Any]]:
        """Load technique taxonomy from JSON"""
        with open(path) as f:
            return json.load(f)
    
    def _build_alias_map(self) -> Dict[str, str]:
        """
        Build normalized alias -> technique_name mapping
        
        Returns:
            Dictionary mapping normalized aliases to technique keys
        """
        alias_map = {}
        
        for tech_key, tech_data in self.taxonomy.items():
            # Add the key itself
            alias_map[self._normalize(tech_key)] = tech_key
            
            # Add full name
            alias_map[self._normalize(tech_data["full_name"])] = tech_key
            
            # Add all aliases
            for alias in tech_data.get("aliases", []):
                alias_map[self._normalize(alias)] = tech_key
        
        return alias_map
    
    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for matching (lowercase, no special chars)"""
        return re.sub(r'[^\w\s]', '', text.lower()).strip()
    
    def map_topics_to_techniques(
        self,
        topics: List[Dict[str, Any]],
        text: str,
        source_type: str = "academic"
    ) -> List[Dict[str, Any]]:
        """
        Map topic keywords to standardized techniques
        
        Args:
            topics: List of topic dictionaries from BERTrend
            text: Original text for context
            source_type: Content source type (for confidence multiplier)
            
        Returns:
            List of technique matches with structure:
                {
                    "technique_name": str,
                    "confidence": float,
                    "context_type": str,
                    "newly_discovered": bool,
                    "text_snippets": List[Dict]
                }
        """
        techniques = []
        
        for topic in topics:
            keywords = topic.get("keywords", [])
            
            # Stage 1: Exact matching
            matched = self._exact_match(keywords)
            
            if matched:
                tech_name, base_confidence = matched
                techniques.append({
                    "technique_name": tech_name,
                    "base_confidence": base_confidence,
                    "keywords": keywords,
                    "stage": "exact_match"
                })
            else:
                # Stage 2: LLM validation for ambiguous topics
                tech_name, llm_confidence = self._llm_validate(keywords)
                
                if tech_name:
                    techniques.append({
                        "technique_name": tech_name,
                        "base_confidence": llm_confidence,
                        "keywords": keywords,
                        "stage": "llm_validation"
                    })
        
        # Calculate final confidence scores with multipliers
        results = []
        for tech in techniques:
            tech_name = tech["technique_name"]
            base_conf = tech["base_confidence"]
            
            # Apply source multiplier (FR-008, plan.md confidence formula)
            source_multiplier = self._get_source_multiplier(source_type)
            
            # Calculate frequency in text (for frequency boost)
            frequency = self._count_technique_mentions(tech_name, text)
            frequency_boost = self._get_frequency_boost(frequency)
            
            # Final confidence
            final_confidence = base_conf * source_multiplier * frequency_boost
            final_confidence = min(final_confidence, 1.0)  # Cap at 1.0
            
            # Detect context type (T016a - FR-014)
            context_type = self._detect_context(text, tech_name)
            
            # Check if newly discovered (not in taxonomy)
            newly_discovered = tech_name not in self.taxonomy
            
            results.append({
                "technique_name": self.taxonomy.get(tech_name, {}).get("full_name", tech_name),
                "confidence": round(final_confidence, 3),
                "context_type": context_type,
                "newly_discovered": newly_discovered,
                "text_snippets": [],  # Populated by extraction_service (T017a)
            })
        
        # Deduplicate and return top 5
        seen = set()
        unique_results = []
        for result in sorted(results, key=lambda x: x["confidence"], reverse=True):
            if result["technique_name"] not in seen:
                seen.add(result["technique_name"])
                unique_results.append(result)
                if len(unique_results) >= 5:
                    break
        
        return unique_results
    
    def _exact_match(self, keywords: List[str]) -> Optional[Tuple[str, float]]:
        """
        Stage 1: Exact matching against taxonomy aliases
        
        Returns:
            Tuple of (technique_name, confidence=1.0) if matched, None otherwise
        """
        for keyword in keywords:
            normalized = self._normalize(keyword)
            if normalized in self.alias_map:
                tech_key = self.alias_map[normalized]
                return (tech_key, 1.0)
        
        return None
    
    def _llm_validate(self, keywords: List[str]) -> Tuple[Optional[str], float]:
        """
        Stage 2: LLM validation for ambiguous topics
        
        Args:
            keywords: Topic keywords from BERTrend
            
        Returns:
            Tuple of (technique_name, confidence) or (None, 0.0)
        """
        try:
            # Build prompt with taxonomy context
            tech_names = [
                self.taxonomy[k]["full_name"]
                for k in list(self.taxonomy.keys())[:20]  # Sample for context window
            ]
            
            prompt = f"""Topic keywords: {', '.join(keywords)}

Known AI techniques: {', '.join(tech_names)}

Map these keywords to the most relevant standardized technique name. If no clear match, return "unknown".

Return only JSON: {{"technique": "name", "confidence": 0.0-1.0}}"""
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI technique taxonomy expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic
                max_tokens=100,
            )
            
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            technique = result.get("technique")
            confidence = float(result.get("confidence", 0.0))
            
            if technique and technique != "unknown":
                # Find matching taxonomy key
                for key, data in self.taxonomy.items():
                    if data["full_name"].lower() == technique.lower():
                        return (key, confidence)
                
                # Newly discovered technique
                return (technique, confidence)
            
        except Exception as e:
            logger.error(f"LLM validation failed: {e}")
        
        return (None, 0.0)
    
    @staticmethod
    def _get_source_multiplier(source_type: str) -> float:
        """Get confidence multiplier based on source type (plan.md formula)"""
        multipliers = {
            "academic": 1.0,
            "blog": 0.95,
            "press_release": 0.90,
            "podcast": 0.85,
            "social": 0.80,
        }
        return multipliers.get(source_type, 1.0)
    
    def _count_technique_mentions(self, tech_name: str, text: str) -> int:
        """Count how many times technique is mentioned in text"""
        tech_data = self.taxonomy.get(tech_name, {})
        aliases = [tech_name, tech_data.get("full_name", "")] + tech_data.get("aliases", [])
        
        count = 0
        text_lower = text.lower()
        for alias in aliases:
            if alias:
                count += text_lower.count(alias.lower())
        
        return count
    
    @staticmethod
    def _get_frequency_boost(frequency: int) -> float:
        """Get confidence boost based on mention frequency (plan.md formula)"""
        if frequency == 1:
            return 1.0
        elif 2 <= frequency <= 4:
            return 1.1
        else:  # 5+
            return 1.2  # Capped at 1.2
    
    @staticmethod
    def _detect_context(text: str, tech_name: str) -> str:
        """
        Detect context type using keyword matching (T016a - FR-014)
        
        Returns:
            Context type: production/research/tutorial/criticism/general
        """
        text_lower = text.lower()
        
        # Context keyword patterns
        context_keywords = {
            "production": ["production", "deployed", "live", "released", "in use"],
            "research": ["study", "experiment", "investigate", "paper", "research"],
            "tutorial": ["tutorial", "guide", "how-to", "example", "walkthrough"],
            "criticism": ["failed", "problem", "issue", "limitation", "drawback"],
        }
        
        # Count matches for each context
        context_scores = {}
        for context, keywords in context_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                context_scores[context] = score
        
        # Return highest scoring context or 'general'
        if context_scores:
            return max(context_scores.items(), key=lambda x: x[1])[0]
        
        return "general"

