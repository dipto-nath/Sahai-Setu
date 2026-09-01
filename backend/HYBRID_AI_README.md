# SahaiSetu - Hybrid AI Backend (SIH26093)

## AI-Assisted Multimodal Stress and Vulnerability Assessment Platform

This backend implements a **genuine hybrid AI architecture** combining local processing with Gemini API contextual analysis.

## Architecture Flow

```
USER INPUT
   |
   +-- TEXT --+
              |
   +-- VOICE --+
              |
              v
   AUDIO PREPROCESSING
              |
              v
   AUDIO QUALITY CHECK
              |
              v
   SPEECH-TO-TEXT (local)
              |
              v
   TRANSCRIPT
              |
   +----------+----------+
   |          |          |
   v          v          v
LOCAL NLP  GEMINI API  LOCAL AUDIO
FEATURES   CONTEXT     FEATURES
   |          |          |
   +----------+----------+
              |
              v
   FEATURE NORMALIZATION (0.0-1.0)
              |
              v
   MULTIMODAL FUSION ENGINE
   (configurable weights)
              |
              v
   STRESS VULNERABILITY INDEX (SVI)
   0-100, calculated by backend logic
              |
              v
   RISK CLASSIFICATION
   LOW / MODERATE / HIGH / CRITICAL
              |
              v
   CONFIDENCE CALCULATION
              |
              v
   RECOMMENDATION ENGINE
   (rule-based, transparent)
              |
              v
   AUTHORIZED HUMAN REVIEW
              |
              v
   FINAL REVIEW STATUS
```

## Critical Principles

This system is an **AI-assisted decision-support prototype**. It does NOT:

- Diagnose mental illness
- Claim that a user definitely has depression, PTSD, or any medical condition
- Treat voice characteristics alone as proof of psychological state
- Allow Gemini to make the final case decision
- Allow AI to replace authorized human professionals

## Module Structure

### ML Components (`app/ml/`)

- **`text_features.py`** - Local NLP feature extraction
  - Multilingual (English, Bengali, Hindi)
  - Configurable regex patterns
  - Extracts: fear, distress, threat, isolation, urgency, repetition

- **`audio_features.py`** - Local audio feature extraction (librosa)
  - Speaking rate, pause duration, pitch variation
  - Energy variation, voice activity ratio
  - Audio quality score (SNR estimate)
  - **NOT diagnostic** - supporting signals only

- **`normalization.py`** - Cross-source feature normalization
  - All features converted to 0.0-1.0 scale
  - Calculates input quality metrics

- **`fusion.py`** - Multimodal fusion engine
  - Configurable weights (voice: 40/35/25, text-only: 50/50/0)
  - Loads from `config/model_weights.json`

- **`svi_engine.py`** - Stress Vulnerability Index (0-100)
  - **Backend logic, NOT Gemini**
  - Configurable risk thresholds
  - Loads from `config/risk_thresholds.json`

- **`confidence_engine.py`** - Confidence calculation
  - Independent from risk
  - Considers completeness, agreement, quality

### Services (`app/services/`)

- **`gemini_service.py`** - Gemini API integration
  - **Data minimization layer** (removes emails, phones, IDs)
  - **Pydantic validation** of responses
  - Mock fallback for demo mode
  - Only analyzes contextual categories, not final decisions

- **`audio_service.py`** - Audio preprocessing & validation

- **`recommendation_service.py`** - Rule-based recommendations
  - Transparent rules
  - Does NOT dispatch emergency services
  - All recommendations require human review

- **`hybrid_assessment_service.py`** - Main orchestrator
  - Ties all components together
  - `assess_text()` and `assess_voice()` methods

## API Endpoints

### SIH26093 Spec Endpoints (Root Path)

- `POST /assessment/text` - Text-based AI-Assisted Assessment
- `POST /assessment/voice` - Voice-based AI-Assisted Assessment
- `POST /cases` - Create case
- `GET /cases` - List cases
- `POST /review/{case_id}` - Human review
- `GET /review/{case_id}` - Get reviews
- `GET /dashboard/overview` - Dashboard
- `GET /dashboard/priority-cases` - Priority cases
- `GET /analytics/risk-distribution` - Analytics
- `GET /analytics/case-volume` - Case volume
- `GET /analytics/language-distribution` - Languages
- `GET /analytics/ai-vs-human` - AI vs Human

### API Path Endpoints (v1 compatibility)

- `POST /api/assessment/text`
- `POST /api/assessment/voice`
- `GET /api/auth/login`
- `GET /api/cases/...`

## Configuration Files

- `app/config/model_weights.json` - Fusion weights
- `app/config/risk_thresholds.json` - SVI thresholds

## Environment Variables

```
GEMINI_API_KEY=...        # Gemini API key (keep on backend)
DATABASE_URL=...          # PostgreSQL URL
JWT_SECRET=...            # JWT signing key
DEMO_MODE=true|false      # Use mock services if no API key
```

## Running

```bash
source .venv/bin/activate
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for OpenAPI documentation.

## Demo Mode

When `DEMO_MODE=true` or no `GEMINI_API_KEY` is set:
- Gemini calls fall back to mock responses
- Audio processing uses fallback values
- All processing continues without crashing

## Human-in-the-Loop

The system preserves both AI and human assessments:
- AI: `ai_risk_level`, `svi_score`, `confidence`
- Human: `human_risk_level`, `notes`, `decision`

Final decisions reflect authorized human review.
