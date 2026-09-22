import json
import logging
import time
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List

from ai.speech import get_speech_service
from app.services.gemini_service import get_gemini_service
from app.config import settings
from google.genai import types

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/live", tags=["Live Call"])


def _compute_vocal_biomarkers(audio_bytes: bytes) -> Dict[str, Any]:
    """
    Process raw audio bytes with librosa and return a vocal_stress_score (0-100)
    plus human-readable biomarker_tags. Falls back gracefully if librosa is unavailable.
    """
    try:
        import librosa
        import tempfile, os

        if not audio_bytes or len(audio_bytes) < 500:
            return {"vocal_stress_score": 0, "biomarker_tags": [], "raw": {}}

        # Write bytes to a temp file so librosa can load it
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            y, sr = librosa.load(tmp_path, sr=16000, duration=4.0)
        finally:
            os.unlink(tmp_path)

        if len(y) < sr * 0.5:   # Less than 0.5s — not enough data
            return {"vocal_stress_score": 0, "biomarker_tags": [], "raw": {}}

        # --- Feature Extraction ---
        rms = librosa.feature.rms(y=y)[0]
        energy_mean = float(np.mean(rms))
        energy_std  = float(np.std(rms))

        try:
            f0, voiced_flag, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            voiced_f0 = f0[voiced_flag] if voiced_flag is not None else np.array([])
            pitch_mean = float(np.mean(voiced_f0)) if len(voiced_f0) > 0 else 150.0
            pitch_std  = float(np.std(voiced_f0))  if len(voiced_f0) > 0 else 15.0
        except Exception:
            pitch_mean, pitch_std = 150.0, 15.0

        # Speaking-rate proxy via onset detection
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, _  = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        speech_rate = float(tempo) * 1.5 if tempo > 0 else 150.0

        # Silence ratio (pauses)
        silence_threshold = np.percentile(rms, 20)
        is_speech = rms > silence_threshold
        silence_ratio = float(1.0 - np.mean(is_speech))

        # --- Stress Score (0-100) ---
        # Higher pitch_std  → panic / crying
        # Higher energy_std → sudden shouts or whimpers
        # Higher silence    → hiding / shock
        # Low energy_mean  → whispering
        pitch_stress   = min(1.0, pitch_std  / 80.0)
        energy_stress  = min(1.0, energy_std / 0.15)
        silence_stress = min(1.0, silence_ratio / 0.6)
        whisper_stress = max(0.0, 1.0 - (energy_mean / 0.05)) if energy_mean < 0.05 else 0.0

        raw_score = (pitch_stress * 0.35) + (energy_stress * 0.30) + \
                    (silence_stress * 0.20) + (whisper_stress * 0.15)
        vocal_stress_score = int(round(min(100, raw_score * 100)))

        # --- Biomarker Tags ---
        tags: List[str] = []

        if energy_mean < 0.015 and speech_rate < 100:
            tags.append("Whispering / Hiding")
        if pitch_std > 60:
            tags.append("Sudden Distress / Panic")
        if energy_std > 0.12 and pitch_std > 40:
            tags.append("Crying / Sobbing")
        if speech_rate > 220:
            tags.append("Hyperventilating / Rapid Speech")
        if silence_ratio > 0.55:
            tags.append("Prolonged Silence / Shock")
        if pitch_mean > 280 and pitch_std > 50:
            tags.append("Screaming / High Pitch Alert")
        if energy_std < 0.02 and speech_rate < 80:
            tags.append("Monotone / Dissociation")
        if not tags and vocal_stress_score < 25:
            tags.append("Calm / Stable")

        raw_features = {
            "pitch_mean": round(pitch_mean, 1),
            "pitch_std": round(pitch_std, 1),
            "energy_mean": round(energy_mean, 4),
            "energy_std": round(energy_std, 4),
            "speech_rate_bpm": round(speech_rate, 1),
            "silence_ratio": round(silence_ratio, 3),
        }

        return {
            "vocal_stress_score": vocal_stress_score,
            "biomarker_tags": tags,
            "raw": raw_features,
        }

    except Exception as e:
        logger.warning(f"Vocal biomarker extraction failed: {e}")
        return {"vocal_stress_score": 0, "biomarker_tags": [], "raw": {}}


@router.websocket("/audio-stream")
async def audio_biomarker_stream(websocket: WebSocket):
    """
    Accepts raw audio bytes from the browser (2-4 second WebM chunks),
    runs librosa analysis, and streams back JSON with vocal_stress_score
    and biomarker_tags in real-time.
    """
    await websocket.accept()
    logger.info("Vocal biomarker WebSocket connected")
    try:
        while True:
            audio_bytes = await websocket.receive_bytes()
            result = _compute_vocal_biomarkers(audio_bytes)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        logger.info("Vocal biomarker WebSocket disconnected")
    except Exception as e:
        logger.error(f"Vocal biomarker WebSocket error: {e}")


class LiveCallConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

manager = LiveCallConnectionManager()

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    speech_service = get_speech_service()
    gemini_service = get_gemini_service(api_key=settings.ai_api_key if not settings.demo_mode else None)
    
    # Store the latest cumulative transcript for each speaker
    transcripts_by_speaker: Dict[str, str] = {
        "Officer": "",
        "Victim": ""
    }
    
    last_gemini_call_time = 0.0
    
    try:
        while True:
            # Wait for JSON payload containing combined transcript from frontend
            payload_str = await websocket.receive_text()
            data_json = json.loads(payload_str)
            
            full_transcript = data_json.get("full_transcript", "")
            
            if len(full_transcript.strip()) < 5:
                continue
                
            current_time = time.time()
            if current_time - last_gemini_call_time < 5.0:
                # Throttle to avoid hitting the Gemini API rate limit (15 RPM free tier)
                continue
                
            last_gemini_call_time = current_time
            
            # 2. Get real-time guidance from Gemini
            # Since this is a specialized live prompt, we don't use the standard analyze method
            prompt = f"""
You are an expert socio-legal analysis AI assisting a crisis triage officer on a live call for the National Helpline Against Atrocities (SahaiSetu).
The caller may be a victim of atrocities under the SC/ST (Prevention of Atrocities) Act.

The following is the running transcript of the call so far:
"{full_transcript}"

Provide a real-time JSON response with the following strictly formatted fields:
{{
  "current_svi": <integer from 0 to 100 representing current stress/threat level, particularly focusing on caste-based threats, physical safety, or trauma>,
  "guidance": [
    "Summary: <1-sentence analysis of the victim's core situation>",
    "Care: <1-sentence instruction on how to emotionally stabilize and comfort the victim>",
    "Action: <1-sentence instruction on what the officer should specifically say or ask next>"
  ],
  "risk_detected": <boolean indicating if immediate threat or severe distress is present>
}}
"""
            try:
                # Use Gemini client directly if available
                if gemini_service.client:
                    logger.info(f"Calling Gemini API with model: {gemini_service.model_name}")
                    response = await gemini_service.client.aio.models.generate_content(
                        model=gemini_service.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    logger.info(f"Gemini response received: {response.text[:200] if response.text else 'empty'}")
                    ai_data = json.loads(response.text)
                else:
                    # Mock response for demo mode
                    ai_data = {
                        "current_svi": 30,
                        "guidance": ["Listen carefully to the caller", "Keep a calm tone"],
                        "risk_detected": False
                    }
            except Exception as e:
                logger.error(f"Live Gemini Error: {type(e).__name__}: {e}")
                # Fallback to simulated logic if API quota is exhausted or fails
                ai_data = {
                    "current_svi": 30,
                    "guidance": [
                        "Summary: Caller is expressing distress, awaiting further context.",
                        "Care: Acknowledge their feelings and maintain a supportive tone.",
                        "Action: Ask gentle clarifying questions to assess immediate safety."
                    ],
                    "risk_detected": False
                }
            
            # 3. Send SVI & Guidance back to frontend (without the transcript chunk)
            payload = {
                "svi": ai_data.get("current_svi", 50),
                "guidance": ai_data.get("guidance", []),
                "risk_detected": ai_data.get("risk_detected", False)
            }
            await websocket.send_json(payload)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Live Call WebSocket disconnected")
    except Exception as e:
        logger.error(f"Live Call WebSocket Error: {e}")
        manager.disconnect(websocket)

