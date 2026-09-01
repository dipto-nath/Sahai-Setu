"""
Gemini API Service
Multilingual contextual NLP analysis using Gemini.
Gemini ONLY analyzes contextual categories - does NOT make final decisions.

Data minimization:
- Strip unnecessary identifiers
- Use synthetic/de-identified data
- Only send cleaned text for analysis
"""

import json
import logging
import os
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

# Try to import google-genai, fallback to mock if not available
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-genai not available. Using mock Gemini service.")


class GeminiIndicatorSeverity(BaseModel):
    """Severity and confidence for a Gemini-detected indicator"""
    severity: str = Field(..., pattern="^(none|low|moderate|high|critical)$")
    confidence: float = Field(..., ge=0.0, le=1.0)


class GeminiResponse(BaseModel):
    """Validated Gemini response schema"""
    fear: GeminiIndicatorSeverity
    distress: GeminiIndicatorSeverity
    threat_context: GeminiIndicatorSeverity
    social_isolation: GeminiIndicatorSeverity
    vulnerability: GeminiIndicatorSeverity
    urgency: GeminiIndicatorSeverity
    human_review_recommended: bool
    is_prank_or_spam: bool
    explanation: str
    summary: str
    care: str
    action: str


@dataclass
class GeminiResult:
    """Result from Gemini contextual analysis"""
    success: bool
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    raw_text: str = ""
    is_mock: bool = False


class GeminiService:
    """
    Gemini API service for multilingual contextual NLP analysis.
    
    IMPORTANT: This service ONLY analyzes contextual categories.
    It does NOT:
    - Diagnose mental illness
    - Make final risk decisions
    - Replace human reviewers
    
    All analysis goes through Pydantic validation before being used.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.6-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model_name = model_name
        self.client = None
        if self.api_key and GEMINI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"GeminiService initialized with model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

    def _sanitize_text(self, text: str) -> str:
        """Remove potential identifiers from text (data minimization)"""
        if not text:
            return ""
        # Remove potential email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        # Remove phone numbers (basic patterns)
        text = re.sub(r'\b\d{10,}\b', '[PHONE]', text)
        # Remove ID-like patterns
        text = re.sub(r'\b[A-Z]{2,}\d{6,}\b', '[ID]', text)
        return text

    def _build_prompt(self, text: str, language: str) -> str:
        """Build structured prompt for Gemini"""
        sanitized = self._sanitize_text(text)
        return f"""You are an expert socio-legal analysis AI assisting the National Helpline Against Atrocities (SahaiSetu). 
Analyze the following victim statement specifically for indicators related to the Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act. 
This is a triage tool to identify immediate trauma, vulnerability, and legal urgency.

Language: {language}

Statement:
"{sanitized}"

Analyze for the following PREDEFINED contextual categories under the purview of SC/ST atrocities. Rate each on a 0.0-1.0 scale (confidence) and severity (none/low/moderate/high/critical).

Categories:
1. fear: Fear of reprisal, retaliation, or police inaction following an atrocity.
2. distress: Trauma stemming from caste-based violence, untouchability practices, sexual violence, or public humiliation.
3. threat_context: Threats to life, property destruction, forced displacement, land grabbing, or use of casteist slurs.
4. social_isolation: Imposition of social or economic boycotts, denial of access to public resources/water, or ostracization from the village.
5. vulnerability: Socio-economic vulnerability, illiteracy, lack of legal awareness, or systemic power imbalances.
6. urgency: Need for immediate police protection, medical assistance, or FIR registration under the PoA Act.
7. human_review_recommended: Whether a human officer must prioritize this case immediately.
8. is_prank_or_spam: CRITICAL FLAG — set to true if this statement is clearly a joke, prank, spam, test call, or non-emergency complaint rather than a genuine atrocity. Trivial complaints that mention "help" or "police" but are about a stolen chips packet, missing pizza, food delivery gone wrong, lost trivial items of negligible monetary value (e.g. "5 rs", "10 rupees"), a tiffin, a cycle, or a playful/humorous tone must be flagged. When in doubt, prefer false (treat as genuine).

Output strictly valid JSON with this exact schema:
{{
  "fear": {{"severity": "none|low|moderate|high|critical", "confidence": 0.0}},
  "distress": {{"severity": "none|low|moderate|high|critical", "confidence": 0.0}},
  "threat_context": {{"severity": "none|low|moderate|high|critical", "confidence": 0.0}},
  "social_isolation": {{"severity": "none|low|moderate|high|critical", "confidence": 0.0}},
  "vulnerability": {{"severity": "none|low|moderate|high|critical", "confidence": 0.0}},
  "urgency": {{"severity": "none|low|moderate|high|critical", "confidence": 0.0}},
  "human_review_recommended": true|false,
  "is_prank_or_spam": true|false,
  "explanation": "Brief explanation based only on detected communication and contextual indicators",
  "summary": "1-sentence summary of the victim's core situation",
  "care": "1-sentence psychological care instruction for the officer",
  "action": "1-sentence tactical action instruction for the officer"
}}

Return ONLY the JSON. No markdown, no backticks, no commentary."""

    def _parse_and_validate(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Parse and validate Gemini JSON response"""
        try:
            # Clean up potential markdown
            text = raw_text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            # Parse JSON
            data = json.loads(text)
            # Validate with Pydantic
            validated = GeminiResponse(**data)
            return validated.model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to parse/validate Gemini response: {e}")
            return None

    def _mock_response(self, text: str, language: str) -> Dict[str, Any]:
        """Generate a mock response for demo/fallback mode"""
        # Heuristic-based mock based on text content
        text_lower = text.lower() if text else ""
        fear_score = 0.0
        distress_score = 0.0
        threat_score = 0.0
        isolation_score = 0.0
        urgency_score = 0.0

        # Detect obvious prank/spam/junk complaints so the override path
        # works even when the real Gemini API is unavailable.
        is_prank = self._looks_like_prank(text_lower)

        # Simple keyword-based mock
        fear_words = ["afraid", "scared", "terrified", "fear", "ভয়", "डर"]
        distress_words = ["help", "desperate", "suffering", "সাহায্য", "मदद"]
        threat_words = ["threat", "kill", "harm", "weapon", "ধমকি", "धमकी"]
        isolation_words = ["alone", "no one", "isolated", "একা", "अकेला"]
        urgency_words = ["urgent", "immediately", "now", "এখনই", "अभी"]

        for word in fear_words:
            if word in text_lower:
                fear_score = max(fear_score, 0.7)
        for word in distress_words:
            if word in text_lower:
                distress_score = max(distress_score, 0.65)
        for word in threat_words:
            if word in text_lower:
                threat_score = max(threat_score, 0.8)
        for word in isolation_words:
            if word in text_lower:
                isolation_score = max(isolation_score, 0.6)
        for word in urgency_words:
            if word in text_lower:
                urgency_score = max(urgency_score, 0.7)

        def sev(score):
            if score >= 0.7:
                return "high"
            elif score >= 0.4:
                return "moderate"
            elif score > 0:
                return "low"
            return "none"

        fear_sev = sev(fear_score)
        dist_sev = sev(distress_score)
        threat_sev = sev(threat_score)
        iso_sev = sev(isolation_score)
        urg_sev = sev(urgency_score)

        return {
            "fear": {"severity": fear_sev, "confidence": min(1.0, fear_score or 0.1)},
            "distress": {"severity": dist_sev, "confidence": min(1.0, distress_score or 0.1)},
            "threat_context": {"severity": threat_sev, "confidence": min(1.0, threat_score or 0.1)},
            "social_isolation": {"severity": iso_sev, "confidence": min(1.0, isolation_score or 0.1)},
            "vulnerability": {"severity": "moderate", "confidence": 0.5},
            "urgency": {"severity": urg_sev, "confidence": min(1.0, urgency_score or 0.1)},
            "human_review_recommended": (threat_score > 0.6 or distress_score > 0.7) and not is_prank,
            "is_prank_or_spam": is_prank,
            "explanation": (
                "Mock analysis: input flagged as a non-emergency / prank / spam. "
                "SVI will be overridden to LOW. This is a prototype demo response, "
                "NOT validated clinical analysis."
            ) if is_prank else (
                "Mock analysis based on keyword heuristics. This is a prototype "
                "demo response, NOT validated clinical analysis."
            ),
            "summary": (
                "Caller statement appears to be a prank / non-emergency complaint."
                if is_prank else
                "Victim reported an incident requiring attention."
            ),
            "care": (
                "No trauma-support routing required; log and close if no other signals."
                if is_prank else
                "Listen carefully and validate the victim's experience."
            ),
            "action": (
                "Mark as prank/spam and do not allocate officer resources."
                if is_prank else
                "Ask for specific details regarding the incident and any immediate threats."
            ),
        }

    @staticmethod
    def _looks_like_prank(text_lower: str) -> bool:
        """
        Heuristic that mirrors the Local NLP fallback so the override works
        even in demo mode. Conservative on purpose: only obvious junk
        complaints are flagged.
        """
        if not text_lower:
            return False
        strong_prank_signals = [
            "stolen my chips",
            "stole my chips",
            "stole my packet",
            "stolen chips packet",
            "stolen chips",
            "stole my pizza",
            "missing pizza",
            "lorry here as soon as possible",
            "send a police lorry",
            "send a lorry",
            "this is a joke",
            "this is a prank",
            "just kidding",
            "testing the helpline",
            "test call",
            "wrong number",
            "pizza delivery",
            "swiggy",
            "zomato order",
            "missing my tiffin",
        ]
        for phrase in strong_prank_signals:
            if phrase in text_lower:
                return True
        trivial_money = re.search(
            r"\b(stolen|lost|missing)\b.*?\b([1-9]{0,2}\d?)\s*(rs|rupees|inr|₹)\b",
            text_lower,
        )
        police_kw = re.search(r"\b(police|cop|cops|lorry|pcr)\b", text_lower)
        if trivial_money and police_kw:
            atrocity_signals = [
                "caste", "sc/st", "sc st", "atrocity", "rape", "acid attack",
                "tribal", "dalit", "untouchability", "slur",
                "forced displacement",
            ]
            if not any(s in text_lower for s in atrocity_signals):
                return True
        return False

    async def analyze(self, text: str, language: str = "en") -> GeminiResult:
        """
        Analyze text for contextual indicators using Gemini.
        
        Args:
            text: Input text (will be sanitized)
            language: Language code
            
        Returns:
            GeminiResult with validated response or error
        """
        if not text or not text.strip():
            return GeminiResult(success=False, error="Empty text input")

        if not self.client:
            # Fallback to mock
            mock_resp = self._mock_response(text, language)
            return GeminiResult(
                success=True,
                response=mock_resp,
                raw_text=json.dumps(mock_resp),
                is_mock=True
            )

        try:
            prompt = self._build_prompt(text, language)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            raw_text = response.text.strip() if response.text else ""
            validated = self._parse_and_validate(raw_text)
            if validated is None:
                return GeminiResult(
                    success=False,
                    error="Invalid Gemini response - failed validation",
                    raw_text=raw_text
                )
            return GeminiResult(
                success=True,
                response=validated,
                raw_text=raw_text,
                is_mock=False
            )
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            # Fall back to mock on error (don't crash)
            mock_resp = self._mock_response(text, language)
            return GeminiResult(
                success=True,
                response=mock_resp,
                raw_text=json.dumps(mock_resp),
                is_mock=True,
                error=f"Gemini unavailable, using fallback: {str(e)}"
            )


def get_gemini_service(api_key: Optional[str] = None) -> GeminiService:
    """Get a Gemini service instance"""
    return GeminiService(api_key=api_key)
