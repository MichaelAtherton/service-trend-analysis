"""
Structured JSON Logging Utility
Implements FR-019 logging requirements
"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from ..config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON with required fields
        
        Required fields per FR-019:
        - timestamp_iso8601
        - level
        - message
        - request_id (UUID)
        - paper_id
        - source_type
        - duration_ms
        - technique_count
        - confidence_avg, confidence_min, confidence_max
        - error_type, error_message (if failed)
        - job_id (if batch)
        - phase (preprocess/embed/cluster/map)
        
        Never logs: API keys, passwords, full paper text
        """
        log_obj = {
            "timestamp_iso8601": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add optional context fields
        if hasattr(record, "request_id"):
            log_obj["request_id"] = str(record.request_id)
        
        if hasattr(record, "paper_id"):
            log_obj["paper_id"] = record.paper_id
        
        if hasattr(record, "source_type"):
            log_obj["source_type"] = record.source_type
        
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        
        if hasattr(record, "technique_count"):
            log_obj["technique_count"] = record.technique_count
        
        if hasattr(record, "confidence_avg"):
            log_obj["confidence_avg"] = record.confidence_avg
        
        if hasattr(record, "confidence_min"):
            log_obj["confidence_min"] = record.confidence_min
        
        if hasattr(record, "confidence_max"):
            log_obj["confidence_max"] = record.confidence_max
        
        if hasattr(record, "error_type"):
            log_obj["error_type"] = record.error_type
        
        if hasattr(record, "error_message"):
            log_obj["error_message"] = record.error_message
        
        if hasattr(record, "job_id"):
            log_obj["job_id"] = str(record.job_id)
        
        if hasattr(record, "phase"):
            log_obj["phase"] = record.phase
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)


def setup_logging():
    """Configure application logging with JSON formatter"""
    # Get root logger
    logger = logging.getLogger()
    
    # Set level from config
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add JSON formatter handler
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger


def log_extraction_operation(
    logger: logging.Logger,
    level: str,
    message: str,
    request_id: Optional[UUID] = None,
    paper_id: Optional[str] = None,
    source_type: Optional[str] = None,
    duration_ms: Optional[float] = None,
    technique_count: Optional[int] = None,
    confidence_avg: Optional[float] = None,
    confidence_min: Optional[float] = None,
    confidence_max: Optional[float] = None,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
    job_id: Optional[UUID] = None,
    phase: Optional[str] = None,
    **kwargs,
):
    """
    Log an extraction operation with structured context
    
    Args:
        logger: Logger instance
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message
        request_id: Request UUID
        paper_id: Paper identifier
        source_type: Content source type (academic, blog, press_release, podcast, social)
        duration_ms: Operation duration in milliseconds
        technique_count: Number of techniques extracted
        confidence_avg: Average confidence score
        confidence_min: Minimum confidence score
        confidence_max: Maximum confidence score
        error_type: Error classification (if failed)
        error_message: Error description (if failed)
        job_id: Batch job UUID (if batch processing)
        phase: Processing phase (preprocess/embed/cluster/map)
        **kwargs: Additional context fields
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    extra = {}
    if request_id:
        extra["request_id"] = request_id
    if paper_id:
        extra["paper_id"] = paper_id
    if source_type:
        extra["source_type"] = source_type
    if duration_ms is not None:
        extra["duration_ms"] = duration_ms
    if technique_count is not None:
        extra["technique_count"] = technique_count
    if confidence_avg is not None:
        extra["confidence_avg"] = confidence_avg
    if confidence_min is not None:
        extra["confidence_min"] = confidence_min
    if confidence_max is not None:
        extra["confidence_max"] = confidence_max
    if error_type:
        extra["error_type"] = error_type
    if error_message:
        extra["error_message"] = error_message
    if job_id:
        extra["job_id"] = job_id
    if phase:
        extra["phase"] = phase
    
    # Add any additional kwargs
    extra.update(kwargs)
    
    logger.log(log_level, message, extra=extra)


# Initialize logging on module import
setup_logging()

