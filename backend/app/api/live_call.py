import json
import logging
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any

from ai.speech import get_speech_service
from app.services.gemini_service import get_gemini_service
from app.config import settings
from google.genai import types

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/live", tags=["Live Call"])

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

