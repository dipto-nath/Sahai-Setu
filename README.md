# SIH26093 - SahaiSetu AI Triage System

> **Smart India Hackathon 2025 - Problem ID: SIH26093**
> An AI-assisted decision support system for triaging distress cases in the National Health & Family Welfare Helpline (SahaiSetu 14443).
> **This is a prototype demonstration.**

---

## What This System Does

The SahaiSetu AI Triage System helps **authorized call center officers** prioritize and respond to incoming distress calls. The system:

1. **Receives** audio or text interactions from citizens (anonymized)
2. **Analyzes** them through multiple AI pipelines (speech, NLP, audio, SVI/fusion, recommendation)
3. **Scores** each case for social vulnerability indicators (SVI), risk, and confidence
4. **Recommends** appropriate next-step actions (counselling, legal, emergency, etc.)
5. **Surfaces** high-priority cases to officers for human review

### Recent Updates & Features
- **Gemini Live Call Analysis Integration**: Real-time evaluation using Gemini for deeper contextual insights.
- **Short-Text Emergency Bypass**: The NLP engine can now immediately prioritize ultra-short, urgent distress messages (like "I want to jump") bypassing normal length penalties.
- **Improved Platform Support**: Configured to run reliably on Mac OS environments using Python 3.9 (to resolve native extension build issues).
- **SQLite Database Support**: Simplified local development using SQLite.

### Important Disclaimers

- This is a **decision-support tool only** - it does NOT make final decisions about victims.
- All calls require **trained human officer review** before any real action.
- The system is designed for **Indian languages** (English, Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu).

---

## Architecture

```
+---------------------+      +----------------------+      +--------------------+
|  Victim Frontend    | ---> |   FastAPI Backend    | ---> |  SQLite Database   |
|  (Next.js, NextUI)  |      |   (Python 3.9)       |      |  (Local/File)      |
+---------------------+      +----------------------+      +--------------------+
                                       |
                                       v
                          +--------------------------+
                          |     AI Services          |
                          |  - Speech (Whisper)      |
                          |  - NLP (Indic models)    |
                          |  - LLM Context (Gemini)  |
                          |  - Fusion (SVI scoring)  |
                          |  - Recommendation        |
                          +--------------------------+
                                       ^
                                       |
                          +--------------------------+
                          |  Officer Dashboard       |
                          |  (Next.js, Tailwind)     |
                          +--------------------------+
```

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.9 (Recommended for Mac OS compatibility with dependency wheels)
- Node.js 18+

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env         # Edit as needed
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local      # Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### Database
The system uses **SQLite** by default (`nhaa_triage.db`). 
Tables are auto-created and populated with demo users on backend startup.

### Default Credentials
- Officer Login: `officer1` / `demo123`
- Counsellor: `counsellor1` / `demo123`
- Admin: `admin` / `demo123`

---

## Project Structure

```
nhaa-ai-triage/
|-- backend/                     # FastAPI backend service
|   |-- ai/                      # AI/ML modules
|   |   |-- recommendation/      # Recommendation engine
|   |   `-- speech/              # Speech services
|   |-- app/                     # API Logic
|   |   |-- main.py              # Application entry point
|   |   |-- config.py            # Configuration
|   |   |-- database/            # DB connection & session
|   |   |-- models/              # SQLAlchemy models
|   |   |-- schemas/             # Pydantic schemas
|   |   |-- api/                 # API routes
|   |   |-- services/            # Business logic
|   |   |-- ml/                  # Machine Learning pipelines (Text, Audio, SVI)
|   |   `-- security/            # Auth, JWT, RBAC
|   |-- requirements.txt
|
|-- frontend/                    # Next.js frontend (officer + victim)
|   |-- src/
|   |   |-- app/                 # App router pages
|   |   |   |-- victim/          # Victim-facing pages
|   |   |   `-- officer/         # Officer dashboard
|   |   |-- components/          # Shared UI components
|   |   |-- context/             # React context (auth, etc.)
|   |-- package.json
|
|-- docker-compose.yml
|-- .env.example
`-- README.md
```

---

## AI Pipeline Integration

The AI services utilize a hybrid approach consisting of local heuristics and LLMs.

### Modules

| Module | Implementation |
|--------|----------------|
| `speech/` | Translates audio to text using configured APIs. |
| `nlp/` | Regular expressions and keyword heuristics for extreme distress signals (e.g. self-harm). |
| `gemini_service` | LLM-based analysis providing deep contextual insights on abuse/threats. |
| `svi/` | Calculated metrics combining NLP signals, audio cues, and LLM assessments. |
| `fusion/` | Late-fusion merging multiple sources with confidence bounds. |
| `recommendation/` | Deterministic logic creating explicit action pathways based on SVI and distress markers. |

---

## Security & Privacy

- All case data is **anonymized** at the point of capture (no PII is stored)
- Case IDs are random anonymous identifiers (e.g., `CASE-20240121-A1B2C3`)
- All API access is JWT-authenticated with role-based access control (RBAC)

### Roles
- `VICTIM` - Citizens submitting cases (limited access)
- `COUNSELLOR` - Can review and add notes
- `LEGAL_OFFICER` - Legal-related actions
- `AUTHORIZED_STAFF` - Standard officer role
- `ADMIN` - Full system access

---

## Important Notes

**This system is NOT a substitute for professional judgment or emergency services.**

If you or someone you know is in immediate danger, please contact local emergency services (112 in India) or the National Commission for Women helpline (181), Childline (1098), or the National Mental Health Helpline (08046110007).
