"""
Utility Functions
"""
import uuid
from datetime import datetime
from typing import Optional
import hashlib


def generate_case_id() -> str:
    """Generate an anonymous case ID in format CASE-YYYY-XXXXXX"""
    year = datetime.now().year
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"CASE-{year}-{unique_part}"


def hash_content(content: str) -> str:
    """Create a hash of content for deduplication"""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def validate_language_code(language: str) -> bool:
    """Validate language code"""
    supported = {"en", "hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", "or", "as"}
    return language.lower() in supported


def get_supported_languages() -> dict:
    """Get supported languages with display names"""
    return {
        "en": "English",
        "hi": "Hindi (हिंदी)",
        "bn": "Bengali (বাংলা)",
        "ta": "Tamil (தமிழ்)",
        "te": "Telugu (తెలుగు)",
        "mr": "Marathi (मराठी)",
        "gu": "Gujarati (ગુજરાતી)",
        "kn": "Kannada (ಕನ್ನಡ)",
        "ml": "Malayalam (മലയാളം)",
        "pa": "Punjabi (ਪੰਜਾਬੀ)",
        "or": "Odia (ଓଡ଼ିଆ)",
        "as": "Assamese (অসমীয়া)",
    }


def format_svi_score(score: int) -> str:
    """Format SVI score for display"""
    return f"{score}/100"


def get_risk_level_from_svi(svi: int) -> str:
    """Get risk level from SVI score (prototype thresholds)"""
    from app.config import settings
    
    if svi <= settings.svi_threshold_low:
        return "LOW"
    elif svi <= settings.svi_threshold_moderate:
        return "MODERATE"
    elif svi <= settings.svi_threshold_high:
        return "HIGH"
    else:
        return "CRITICAL"


def sanitize_text(text: str, max_length: int = 5000) -> str:
    """Sanitize text input"""
    if not text:
        return ""
    # Remove control characters
    sanitized = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")
    return sanitized[:max_length]


def calculate_confidence_level(confidence: float) -> str:
    """Get confidence level description"""
    from app.config import settings
    
    if confidence >= settings.confidence_threshold_high:
        return "HIGH"
    elif confidence >= settings.confidence_threshold_low:
        return "MODERATE"
    else:
        return "LOW"


def is_demo_mode() -> bool:
    """Check if demo mode is enabled"""
    from app.config import settings
    return settings.demo_mode