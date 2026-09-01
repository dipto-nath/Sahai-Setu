"""
Application Configuration
Centralized configuration management using Pydantic Settings
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "SahaiSetu"
    app_version: str = "1.0.0"
    debug: bool = True
    demo_mode: bool = True
    
    # Database
    database_url: str = Field(default="postgresql://nhaa_user:nhaa_password@localhost:5432/nhaa_triage")
    
    # JWT Authentication
    jwt_secret: str = Field(default="your-super-secret-jwt-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    
    # AI Configuration
    ai_provider: str = "local"
    ai_api_key: Optional[str] = None
    nlp_model_name: str = "distilbert-base-uncased"
    speech_model_name: str = "medium"
    audio_model_name: str = "librosa"
    
    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:3001"])
    
    # Demo Settings
    seed_demo_data: bool = True
    
    # Audio Settings
    max_audio_size_mb: int = 25
    allowed_audio_types: List[str] = Field(default=["audio/wav", "audio/mp3", "audio/m4a", "audio/webm"])
    
    # SVI Weights (Prototype Parameters - NOT Clinically Validated)
    svi_weights_text: float = 0.30
    svi_weights_audio: float = 0.20
    svi_weights_threat: float = 0.25
    svi_weights_vulnerability: float = 0.25
    
    # Risk Thresholds (Prototype - NOT Clinically Validated)
    svi_threshold_low: int = 25
    svi_threshold_moderate: int = 50
    svi_threshold_high: int = 75
    svi_threshold_critical: int = 100
    
    # Confidence Thresholds
    confidence_threshold_high: float = 0.8
    confidence_threshold_low: float = 0.5
    min_text_length: int = 10
    min_audio_duration_seconds: float = 2.0
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()