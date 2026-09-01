"""
Local NLP Feature Extraction Module
Extracts configurable prototype features from text for stress/vulnerability assessment.
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging
import math

logger = logging.getLogger(__name__)


# Default feature patterns for multilingual support
FEAR_PATTERNS = {
    "en": [r"\b(afraid|scared|terrified|frightened|fear|panic|horror|terror|terrorized|petrified|dread|fearful)\b",
           r"\b(threaten|threat|danger|unsafe|harm|hurt|peril|hiding|atrocity)\b"],
    "bn": [r"ভয়|আতঙ্ক|ত্রস্ত|ভীত|ডর|ভয়|ভয়ংকর|নিরাপদ|বিপদ|লুকিয়ে|লিঞ্চিং|হিংসা|হামলা|গালি|অস্পৃশ্যতা|অত্যাচার"],
    "hi": [r"डर|भय|आतंक|भयभीत|घबराहट|खतरा|डरा|दहशत|खौफ|सहमा|असुरक्षित|छिपा|लिंचिंग|हिंसा|हमला|गाली|छुआछूत|अत्याचार"],
}

DISTRESS_PATTERNS = {
    "en": [r"\b(distress|suffering|pain|agony|anguish|despair|trauma|unconscious|bleeding|blood|sos|injured|collapsed|fracture|broken|beaten|assaulted|tortured|lynched|hospitalized|icu)\b",
           r"\b(help|helpless|hopeless|desperate|save me|emergency|crying|weeping|refused)\b"],
    "bn": [r"ব্যথা|কষ্ট|বেদনা|দুঃখ|নিরাশা|বাঁচাও|সাহায্য|বিপদ|মারা|আহত|রক্তপাত|অচেতন|জ্ঞান|লুটিয়ে|হাড়|মারধর|আক্রান্ত|নির্যাতন|লিঞ্চ|হাসপাতাল|আইসিইউ|ট্রমা|অসহায়|নিরুপায়|অস্বীকার"],
    "hi": [r"पीड़ा|कष्ट|वेदना|दुःख|निराशा|मदद|मदित|बचाओ|तकलीफ|दर्द|फंस|पस|घायल|खून|बेहोश|होश|गिरा|हड्डी|फ्रैक्चर|मारपीट|पीटा|हमला|प्रताड़ित|यातना|लिंचिंग|अस्पताल|आईसीयू|आघात|बेबस|लाचार|एफआईआर|मना"],
}

THREAT_PATTERNS = {
    "en": [r"\b(threat|threaten|intimidat|coerc|blackmail|extort|abduct|kidnap|armed|attack|mob|violence|lynch|confinement|captive|boycott|eviction)\b",
           r"\b(harm|hurt|kill|murder|abuse|assault|shoot|slur|rods|weapons|destroyed|fire)\b"],
    "bn": [r"ধমকি|ভয়াদলন|জবরদস্তি|খুন|হত্যা|মেরে|গুলি|অত্যাচার|হুমকি|অস্ত্র|সশস্ত্র|হিংস্র|জনতা|লিঞ্চ|অপহরণ|আটক|বন্দি|বয়কট|উচ্ছেদ|দখল|নষ্ট|পুড়িয়ে|বাধা"],
    "hi": [r"धमकी|भयादोहन|जबरदस्ती|खून|हत्या|मार|गोली|खत्म|मर|मढ़|जान|हथियार|भीड़|हिंसा|लिंचिंग|अगवा|अपहरण|बंधक|बहिष्कार|बेदखली|कब्जा|नष्ट|जला|गवाह"],
}

ISOLATION_PATTERNS = {
    "en": [r"\b(alone|isolated|isolating|lonely|abandoned|stranded|trapped|confined|detained|surrounded|cornered|ostracized|evicted|displaced)\b",
           r"\b(no one|nobody|no support|no help|no friends|cut off|boycott|locked)\b"],
    "bn": [r"একা|একাকী|পরিত্যক্ত|উপেক্ষিত|আটকে|বন্দী|কেউ নেই|বিচ্ছিন্ন|আটক|হেফাজতে|ঘিরে|বয়কট|একঘরে|তাড়িয়ে|উচ্ছেদ|বাস্তুচ্যুত"],
    "hi": [r"अकेला|एकाकी|परित्यक्त|उपेक्षित|अकेली|कोई नहीं|फंस|कैद|अलग-थलग|कट गया|बंधक|हिरासत|घेर|बहिष्कार|बहिष्कृत|निकाल|बेदखल|विस्थापित"],
}

URGENCY_PATTERNS = {
    "en": [r"\b(urgent|immediately|right now|asap|emergency|quick|dispatch|intervention|ambulance|critical)\b",
           r"\b(cannot wait|can't wait|no time|running out|fast|sos|rescue|police|protection)\b"],
    "bn": [r"অবিলম্বে|তৎক্ষণাৎ|এখনই|জরুরি|তাড়াতাড়ি|শীগগির|জলদি|পুলিশ|অ্যাম্বুলেন্স|সংকটজনক|প্রাণঘাতী|উদ্ধার|হস্তক্ষেপ|অপহরণ"],
    "hi": [r"तुरंत|अभी|जरूरी|इमरजेंसी|जल्दी|फौरन|तेजी|पुलिस|एम्बुलेंस|गंभीर|जानलेवा|बचाव|हस्तक्षेप|अपहरण"],
}

REPETITION_PATTERNS = {
    "en": [r"\b(help help|please please|urgent urgent|now now)\b",
           r"(.)\1{2,}"],
    "bn": [r"সাহায্য সাহায্য|জরুরি জরুরি|বাঁচাও বাঁচাও|তাড়াতাড়ি তাড়াতাড়ি"],
    "hi": [r"मदद मदद|जरूरी जरूरी|बचाओ बचाओ|जल्दी जल्दी|मदित मदित"],
}


@dataclass
class TextFeatureConfig:
    fear_patterns: Dict[str, List[str]] = field(default_factory=lambda: FEAR_PATTERNS)
    distress_patterns: Dict[str, List[str]] = field(default_factory=lambda: DISTRESS_PATTERNS)
    threat_patterns: Dict[str, List[str]] = field(default_factory=lambda: THREAT_PATTERNS)
    isolation_patterns: Dict[str, List[str]] = field(default_factory=lambda: ISOLATION_PATTERNS)
    urgency_patterns: Dict[str, List[str]] = field(default_factory=lambda: URGENCY_PATTERNS)
    repetition_patterns: Dict[str, List[str]] = field(default_factory=lambda: REPETITION_PATTERNS)
    supported_languages: List[str] = field(default_factory=lambda: ["en", "bn", "hi"])
    max_score: float = 1.0
    min_score: float = 0.0


@dataclass
class TextFeatures:
    fear_signal: float = 0.0
    distress_signal: float = 0.0
    threat_context_signal: float = 0.0
    isolation_signal: float = 0.0
    urgency_signal: float = 0.0
    repetition_score: float = 0.0
    text_length: int = 0
    language: str = "en"
    language_confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fear_signal": round(self.fear_signal, 4),
            "distress_signal": round(self.distress_signal, 4),
            "threat_context_signal": round(self.threat_context_signal, 4),
            "isolation_signal": round(self.isolation_signal, 4),
            "urgency_signal": round(self.urgency_signal, 4),
            "repetition_score": round(self.repetition_score, 4),
            "text_length": self.text_length,
            "language": self.language,
            "language_confidence": round(self.language_confidence, 4),
        }


class TextFeatureExtractor:
    def __init__(self, config: Optional[TextFeatureConfig] = None):
        self.config = config or TextFeatureConfig()
        self._compiled = {}
        self._compile()

    def _compile(self):
        for lang in self.config.supported_languages:
            self._compiled[lang] = {
                "fear": [re.compile(p, re.IGNORECASE) for p in self.config.fear_patterns.get(lang, [])],
                "distress": [re.compile(p, re.IGNORECASE) for p in self.config.distress_patterns.get(lang, [])],
                "threat": [re.compile(p, re.IGNORECASE) for p in self.config.threat_patterns.get(lang, [])],
                "isolation": [re.compile(p, re.IGNORECASE) for p in self.config.isolation_patterns.get(lang, [])],
                "urgency": [re.compile(p, re.IGNORECASE) for p in self.config.urgency_patterns.get(lang, [])],
                "repetition": [re.compile(p, re.IGNORECASE) for p in self.config.repetition_patterns.get(lang, [])],
            }

    def _count_matches(self, text: str, patterns) -> int:
        return sum(len(p.findall(text)) for p in patterns)

    def _calculate_signal(self, text: str, patterns, text_length: int, max_expected: int = 5) -> float:
        if not patterns or text_length == 0:
            return 0.0
        matches = self._count_matches(text, patterns)
        words = max(text_length / 5, 1)
        normalized = (matches / words) * 100
        score = math.log1p(normalized) / math.log1p(max_expected)
        return min(max(score, self.config.min_score), self.config.max_score)

    def _calculate_repetition(self, text: str, lang: str) -> float:
        patterns = self._compiled.get(lang, {}).get("repetition", [])
        if not patterns:
            return 0.0
        matches = self._count_matches(text, patterns)
        return min(matches * 0.3, 1.0)

    def extract(self, text: str, language: str = "en", language_confidence: float = 0.0) -> TextFeatures:
        if not text or not text.strip():
            return TextFeatures(language=language, language_confidence=language_confidence)
        text = text.strip()
        text_length = len(text)
        lang = language if language in self.config.supported_languages else "en"
        patterns = self._compiled.get(lang, self._compiled["en"])
        return TextFeatures(
            fear_signal=self._calculate_signal(text, patterns["fear"], text_length),
            distress_signal=self._calculate_signal(text, patterns["distress"], text_length),
            threat_context_signal=self._calculate_signal(text, patterns["threat"], text_length),
            isolation_signal=self._calculate_signal(text, patterns["isolation"], text_length),
            urgency_signal=self._calculate_signal(text, patterns["urgency"], text_length),
            repetition_score=self._calculate_repetition(text, lang),
            text_length=text_length,
            language=language,
            language_confidence=language_confidence,
        )


def get_text_feature_extractor(config=None):
    return TextFeatureExtractor(config)
