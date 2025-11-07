"""
Application Settings and Configuration
Uses Pydantic BaseSettings for environment variable management
"""
import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""
    
    # Application Info
    APP_NAME: str = "AI Technique Extraction Service"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Server Configuration
    PORT: int = Field(default=8001, env="PORT")
    
    # Embedding Server
    EMBEDDING_SERVER_URL: str = Field(env="EMBEDDING_SERVER_URL")
    EMBEDDING_CLIENT_ID: str = Field(default="extraction-service", env="EMBEDDING_CLIENT_ID")
    EMBEDDING_CLIENT_SECRET: str = Field(env="EMBEDDING_CLIENT_SECRET")
    
    # OpenAI API
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")
    
    # Authentication & Security
    ALLOWED_API_KEYS: str = Field(env="ALLOWED_API_KEYS")  # Comma-separated
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT: int = Field(default=100, env="DEFAULT_RATE_LIMIT")  # batches/hour
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Technique Extraction
    CONFIDENCE_THRESHOLD: float = Field(default=0.6, env="CONFIDENCE_THRESHOLD")
    
    @property
    def allowed_api_keys_list(self) -> list[str]:
        """Parse comma-separated API keys into list"""
        return [key.strip() for key in self.ALLOWED_API_KEYS.split(",") if key.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

