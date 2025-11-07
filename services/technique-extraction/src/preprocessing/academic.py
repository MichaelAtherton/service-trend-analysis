"""
Academic Paper Preprocessing
Cleans and prepares academic papers for technique extraction
"""
import re
from typing import Optional


def clean_academic(text: str, max_length: Optional[int] = 50000) -> str:
    """
    Clean academic paper text by removing references, LaTeX, equations
    
    Args:
        text: Raw academic paper text
        max_length: Maximum text length (words) before splitting required
        
    Returns:
        Cleaned text ready for embedding
        
    Note:
        For texts >50,000 words, use BERTrend's split_data() for paragraph-based splitting
    """
    # Remove LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # Remove inline math expressions
    text = re.sub(r'\$.*?\$', '', text)
    text = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
    
    # Remove equation blocks
    text = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{align\}.*?\\end\{align\}', '', text, flags=re.DOTALL)
    
    # Remove reference section (common patterns)
    text = re.sub(
        r'(References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*\n.*',
        '',
        text,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Remove citation markers [1], (Smith et al., 2020), etc.
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\([A-Za-z]+\s+et\s+al\.,\s+\d{4}\)', '', text)
    
    # Remove special characters but preserve technical terms
    text = re.sub(r'[^\w\s\-\.\,\;\:\(\)\[\]\/]', '', text)
    
    # Normalize paragraph breaks FIRST (preserve double newlines)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    # Remove excessive whitespace WITHIN paragraphs (but preserve paragraph breaks)
    # Split by paragraph, clean each, rejoin
    paragraphs = text.split('\n\n')
    cleaned_paragraphs = [re.sub(r'\s+', ' ', p.strip()) for p in paragraphs if p.strip()]
    text = '\n\n'.join(cleaned_paragraphs)
    
    return text.strip()


def extract_abstract_and_body(text: str) -> tuple[str, str]:
    """
    Separate abstract from body for weighted processing
    
    Args:
        text: Full academic paper text
        
    Returns:
        Tuple of (abstract, body) text
    """
    # Common abstract section patterns
    abstract_patterns = [
        r'Abstract[\s\n]+(.*?)(?=\n\s*(?:Introduction|1\.|Keywords))',
        r'ABSTRACT[\s\n]+(.*?)(?=\n\s*(?:INTRODUCTION|1\.|KEYWORDS))',
    ]
    
    abstract = ""
    body = text
    
    for pattern in abstract_patterns:
        match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
        if match:
            abstract = match.group(1).strip()
            body = text[match.end():].strip()
            break
    
    return abstract, body


def should_split_document(text: str, word_threshold: int = 50000) -> bool:
    """
    Determine if document needs splitting for BERTrend processing
    
    Args:
        text: Document text
        word_threshold: Maximum words before splitting required
        
    Returns:
        True if document exceeds threshold and needs splitting
    """
    word_count = len(text.split())
    return word_count > word_threshold

