# SIH26093 - SahaiSetu AI Triage System

> **Smart India Hackathon 2025 - Problem ID: SIH26093**
> An AI-assisted decision support system for triaging distress cases in the National Health & Family Welfare Helpline (SahaiSetu 14443).
> **This is a prototype demonstration using synthetic data only.**

---

## What This System Does

The SahaiSetu AI Triage System helps **authorized call center officers** prioritize and respond to incoming distress calls. The system:

1. **Receives** audio or text interactions from citizens (anonymized)
2. **Analyzes** them through multiple AI pipelines (speech, NLP, audio, SVI/fusion, recommendation)
3. **Scores** each case for social vulnerability indicators (SVI), risk, and confidence
4. **Recommends** appropriate next-step actions (counselling, legal, emergency, etc.)
5. **Surfaces** high-priority cases to officers for human review

### Recent Updates
- **Gemini Live Call Analysis Integration**: Real-time evaluation using Gemini for deeper contextual insights.
- **Short-Text Emergency Bypass**: The NLP engine can now immediately prioritize ultra-short, urgent distress messages (like "I want to jump") bypassing normal length penalties.
- **Improved Platform Support**: Configured to run reliably on Mac OS environments using specific pre-compiled dependency wheels (Python 3.9).

### Important Disclaimers

- This is a **decision-support tool only** - it does NOT make final decisions about victims.
- All calls require **trained human officer review** before any real action.
- This prototype uses **synthetic data** - no real victim information is stored or processed.
- The AI is **rule-based and heuristic** in demo mode - not a clinical diagnosis.
- The system is designed for **Indian languages** (English, Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu).

---

## Architecture

```
+---------------------+      +----------------------+      +--------------------+
|  Victim Frontend    | ---> |   FastAPI Backend    | ---> |  PostgreSQL DB     |
|  (Next.js, NextUI)  |      |   (Python 3.11)      |      |  (15-alpine)       |
+---------------------+      +----------------------+      +--------------------+
                                       |
                                       v
                          +--------------------------+
                          |     AI Services          |
                          |  - Speech (Whisper)      |
                          |  - NLP (Indic models)    |
                          |  - Audio (Prosody)       |
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

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker 20.10+ and Docker Compose v2+
- 8GB RAM minimum (for AI services)
- Ports available: 3000, 5432, 8000

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nhaa-ai-triage
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   # Edit .env to change passwords and secrets
   ```

3. **Start the stack**
   ```bash
   docker compose up -d
   ```

4. **Access the system**
   - Victim Frontend: http://localhost:3000
   - Officer Dashboard: http://localhost:3000/officer
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Default demo credentials**
   - Officer Login: `officer1` / `demo123`
   - Counsellor: `counsellor1` / `demo123`
   - Admin: `admin` / `demo123`

### Stopping the stack
```bash
docker compose down              # Stop
docker compose down -v           # Stop and remove volumes (clean slate)
```

---

## Quick Start (Local Development)

### Backend

```bash
cd backend
python -m venv venv
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

### Database (Local)

Requires PostgreSQL 15+.

```bash
createdb nhaa_triage
createuser nhaa_user -P
```

Tables are auto-created on backend startup.

---

## Project Structure

```
nhaa-ai-triage/
|-- ai/                          # AI/ML pipeline (standalone Python module)
|   |-- audio/                   # Audio feature extraction (prosody, voice stress)
|   |-- speech/                  # Speech-to-text (Whisper / demo)
|   |-- nlp/                     # NLP analysis (IndicBERT / demo keyword)
|   |-- svi/                     # Social Vulnerability Index
|   |-- fusion/                  # Multi-modal fusion & risk scoring
|   |-- recommendation/          # Recommendation engine
|   `-- evaluation/              # Offline evaluation scripts
|
|-- backend/                     # FastAPI backend service
|   |-- app/
|   |   |-- main.py              # Application entry point
|   |   |-- config.py            # Configuration
|   |   |-- database/            # DB connection & session
|   |   |-- models/              # SQLAlchemy models
|   |   |-- schemas/             # Pydantic schemas
|   |   |-- api/                 # API routes
|   |   |-- services/            # Business logic
|   |   |-- security/            # Auth, JWT, RBAC
|   |   `-- utils/               # Helpers
|   |-- requirements.txt
|   `-- Dockerfile
|
|-- frontend/                    # Next.js frontend (officer + victim)
|   |-- src/
|   |   |-- app/                 # App router pages
|   |   |   |-- victim/          # Victim-facing pages
|   |   |   `-- officer/         # Officer dashboard
|   |   |-- components/          # Shared UI components
|   |   |-- services/            # API client
|   |   |-- context/             # React context (auth, etc.)
|   |   |-- types/               # TypeScript types
|   |   `-- lib/                 # Utility functions
|   |-- package.json
|   `-- Dockerfile
|
|-- docker-compose.yml
|-- .env.example
`-- README.md
```

---

## AI Pipeline (Demo Mode)

The AI services run in **demo mode** by default - using rule-based, deterministic logic that does NOT require GPU, model weights, or external API calls.

### Modules

| Module | Real Implementation | Demo Implementation |
|--------|---------------------|---------------------|
| `speech/` | OpenAI Whisper (small/medium) | Returns synthetic text |
| `nlp/` | IndicBERT / MuRIL multilingual | Keyword-based indicator detection |
| `audio/` | librosa + prosody features | Random heuristic scores |
| `svi/` | XGBoost regression on social factors | Weighted rule scoring |
| `fusion/` | Late-fusion with confidence | Weighted sum with thresholds |
| `recommendation/` | Rule engine + knowledge base | Static recommendation templates |

To switch from demo to real AI, set in `.env`:
```
DEMO_MODE=false
AI_PROVIDER=local           # or 'openai' / 'huggingface'
AI_API_KEY=...
NLP_MODEL_NAME=ai4bharat/indic-bert
SPEECH_MODEL_NAME=openai/whisper-small
```

---

## Security & Privacy

- All case data is **anonymized** at the point of capture (no PII is stored)
- Case IDs are random anonymous identifiers (e.g., `CASE-20240121-A1B2C3`)
- All API access is JWT-authenticated with role-based access control (RBAC)
- Audit logs record every system action
- Database credentials and JWT secrets must be set via environment variables

### Roles
- `VICTIM` - Citizens submitting cases (limited access)
- `COUNSELLOR` - Can review and add notes
- `LEGAL_OFFICER` - Legal-related actions
- `AUTHORIZED_STAFF` - Standard officer role
- `ADMIN` - Full system access

---

## Testing

```bash
# Backend
cd backend
pytest                          # All tests
pytest tests/test_api.py        # Specific test file
pytest --cov=app                # With coverage

# Frontend
cd frontend
npm test
npm run test:coverage
```

---

## Documentation

- [API Reference](http://localhost:8000/docs) - OpenAPI/Swagger UI (when running)
- See `docs/` directory for additional documentation
- See `ai/` module READMEs for AI service details

---

## License

This project is for educational/demonstration purposes as part of Smart India Hackathon 2025.

## Acknowledgments

- **SIH 2025** for the problem statement
- **SahaiSetu (14443)** for the use case context
- **AI4Bharat** for Indic language model inspiration
- All open-source contributors and libraries used in this project

---

## Important Notes

**This system is NOT a substitute for professional judgment or emergency services.**

If you or someone you know is in immediate danger, please contact local emergency services (112 in India) or the National Commission for Women helpline (181), Childline (1098), or the National Mental Health Helpline (08046110007).
