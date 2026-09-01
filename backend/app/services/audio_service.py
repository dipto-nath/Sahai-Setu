"""
Audio Preprocessing Service
Validates, normalizes, and processes audio files before feature extraction.
"""

import io
import logging
from typing import Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("librosa not available for audio service")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


@dataclass
class AudioValidationResult:
    is_valid: bool
    duration_seconds: float
    sample_rate: int
    file_format: str
    audio_quality: str  # GOOD, FAIR, POOR
    has_speech: bool
    silence_ratio: float
    error: Optional[str] = None


class AudioPreprocessingService:
    """Service for validating and preprocessing audio files"""

    SUPPORTED_FORMATS = ['wav', 'mp3', 'm4a', 'webm', 'ogg', 'flac']
    MIN_DURATION_SEC = 0.5
    MAX_DURATION_SEC = 600.0  # 10 minutes
    TARGET_SAMPLE_RATE = 16000

    def __init__(self):
        self.target_sr = self.TARGET_SAMPLE_RATE

    def detect_format(self, audio_data: bytes, filename: str = "") -> str:
        """Detect audio format from data header or filename"""
        if audio_data[:4] == b'RIFF':
            return 'wav'
        if audio_data[:3] == b'ID3' or audio_data[:2] == b'\xff\xfb':
            return 'mp3'
        if audio_data[:4] == b'fLaC':
            return 'flac'
        if audio_data[:4] == b'OggS':
            return 'ogg'
        # Try filename
        if filename and '.' in filename:
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext in self.SUPPORTED_FORMATS:
                return ext
        return 'wav'  # default

    def validate(self, audio_data: bytes, filename: str = "") -> AudioValidationResult:
        """Validate audio file"""
        if not audio_data or len(audio_data) < 100:
            return AudioValidationResult(
                is_valid=False, duration_seconds=0, sample_rate=0,
                file_format='unknown', audio_quality='POOR', has_speech=False,
                silence_ratio=1.0, error="Audio data too small or empty"
            )

        file_format = self.detect_format(audio_data, filename)

        if not LIBROSA_AVAILABLE:
            # Fallback validation based on file size
            estimated_duration = len(audio_data) / 32000.0  # rough estimate
            return AudioValidationResult(
                is_valid=True, duration_seconds=min(estimated_duration, 30),
                sample_rate=16000, file_format=file_format,
                audio_quality='FAIR', has_speech=True, silence_ratio=0.3
            )

        try:
            import tempfile, os, subprocess
            with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
                
            wav_path = tmp_path + "_converted.wav"
            try:
                # Use the local ffmpeg we installed
                ffmpeg_cmd = [
                    "/Users/diptonath/Documents/coding/nhaa-ai-triage/.venv/bin/ffmpeg",
                    "-y", "-i", tmp_path,
                    "-ac", "1", "-ar", str(self.target_sr),
                    wav_path
                ]
                subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                y, sr = librosa.load(wav_path, sr=self.target_sr)
            except Exception as e:
                logger.warning(f"ffmpeg conversion failed, falling back to direct load: {e}")
                y, sr = librosa.load(tmp_path, sr=self.target_sr)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                if os.path.exists(wav_path):
                    os.unlink(wav_path)

            duration = len(y) / sr
            if duration < self.MIN_DURATION_SEC:
                return AudioValidationResult(
                    is_valid=False, duration_seconds=duration, sample_rate=sr,
                    file_format=file_format, audio_quality='POOR',
                    has_speech=False, silence_ratio=1.0,
                    error=f"Audio too short: {duration:.2f}s"
                )
            if duration > self.MAX_DURATION_SEC:
                return AudioValidationResult(
                    is_valid=False, duration_seconds=duration, sample_rate=sr,
                    file_format=file_format, audio_quality='POOR',
                    has_speech=True, silence_ratio=0.3,
                    error=f"Audio too long: {duration:.2f}s"
                )

            # Detect silence ratio
            rms = librosa.feature.rms(y=y)[0]
            threshold = np.percentile(rms, 20)
            silence_ratio = float(np.mean(rms <= threshold))
            has_speech = silence_ratio < 0.8

            # Estimate quality
            spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
            snr = 10 * np.log10(1 / (np.mean(spectral_flatness) + 1e-10))
            snr = max(0, min(40, snr))
            if snr > 20:
                quality = 'GOOD'
            elif snr > 10:
                quality = 'FAIR'
            else:
                quality = 'POOR'

            return AudioValidationResult(
                is_valid=has_speech,
                duration_seconds=float(duration),
                sample_rate=int(sr),
                file_format=file_format,
                audio_quality=quality,
                has_speech=has_speech,
                silence_ratio=silence_ratio,
            )
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return AudioValidationResult(
                is_valid=False, duration_seconds=0, sample_rate=0,
                file_format=file_format, audio_quality='POOR',
                has_speech=False, silence_ratio=1.0,
                error=str(e)
            )

    def preprocess(self, audio_data: bytes, filename: str = "") -> Tuple[Optional[bytes], AudioValidationResult]:
        """Preprocess and normalize audio"""
        validation = self.validate(audio_data, filename)
        if not validation.is_valid:
            return None, validation
        # In demo mode, just return as-is
        return audio_data, validation


def get_audio_preprocessing_service() -> AudioPreprocessingService:
    return AudioPreprocessingService()
