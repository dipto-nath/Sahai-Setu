"""
ML Module for SahaiSetu Backend
Hybrid AI processing components:
- text_features: Local NLP feature extraction
- audio_features: Local audio feature extraction
- normalization: Cross-source feature normalization
- fusion: Multimodal fusion engine
- svi_engine: Stress Vulnerability Index calculation
- confidence_engine: Confidence calculation
"""

from app.ml.text_features import (
    TextFeatureExtractor,
    TextFeatures,
    TextFeatureConfig,
    get_text_feature_extractor,
)
from app.ml.audio_features import (
    AudioFeatureExtractor,
    AudioFeatures,
    get_audio_feature_extractor,
)
from app.ml.normalization import (
    FeatureNormalizer,
    NormalizedFeatureSet,
    NormalizedTextFeatures,
    NormalizedContextFeatures,
    NormalizedAudioFeatures,
    InputQualityMetrics,
    get_feature_normalizer,
)
from app.ml.fusion import (
    FusionEngine,
    FusionResult,
    FusionWeights,
    get_fusion_engine,
)
from app.ml.svi_engine import (
    SVIEngine,
    SVIResult,
    RiskThresholds,
    get_svi_engine,
)
from app.ml.confidence_engine import (
    ConfidenceEngine,
    ConfidenceResult,
    ConfidenceFactors,
    get_confidence_engine,
)

__all__ = [
    "TextFeatureExtractor",
    "TextFeatures",
    "TextFeatureConfig",
    "get_text_feature_extractor",
    "AudioFeatureExtractor",
    "AudioFeatures",
    "get_audio_feature_extractor",
    "FeatureNormalizer",
    "NormalizedFeatureSet",
    "NormalizedTextFeatures",
    "NormalizedContextFeatures",
    "NormalizedAudioFeatures",
    "InputQualityMetrics",
    "get_feature_normalizer",
    "FusionEngine",
    "FusionResult",
    "FusionWeights",
    "get_fusion_engine",
    "SVIEngine",
    "SVIResult",
    "RiskThresholds",
    "get_svi_engine",
    "ConfidenceEngine",
    "ConfidenceResult",
    "ConfidenceFactors",
    "get_confidence_engine",
]
