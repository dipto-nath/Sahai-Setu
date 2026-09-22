# SIH26093 - SahaiSetu AI Triage System

> **Smart India Hackathon 2025 - Problem ID: SIH26093**
> An AI-assisted decision support system for triaging distress cases in the National Health & Family Welfare Helpline (14566).

---

## 📌 Project Overview

The SahaiSetu AI Triage System is a multimodal intelligence platform designed to assist **authorized call center officers** in prioritizing and responding to incoming distress calls. By combining local heuristic Natural Language Processing (NLP), speech analytics, and context-aware Large Language Models (LLMs), the platform quickly surfaces high-priority and critical cases for human review.

### Key Capabilities
1. **Multimodal Analysis**: Processes both text and audio interactions natively.
2. **Hybrid Intelligence**: Merges local regex/heuristic-based NLP engines (for sub-second emergency detection) with the **Google Gemini API** (for deep contextual analysis of abuse and threats).
3. **Live Call Analysis**: Real-time evaluation of ongoing calls to instantly trigger officer guidance.
4. **Social Vulnerability Index (SVI)**: A custom scoring algorithm that quantifies risk from 0-100 based on distress, fear, threat, and isolation indicators.
5. **Short-Text Emergency Bypass**: Bypasses normal NLP length penalties for ultra-short, critical cries for help (e.g., "I want to jump", "help me").

### Important Disclaimers
- This is a **decision-support tool only**—it does NOT make final decisions, diagnose medical conditions, or automatically dispatch emergency services.
- All high-risk classifications require **trained human officer review**.
- This system uses **synthetic data** and is currently in a prototype phase.

---

## 🏗️ Architecture & Tech Stack

### High-Level Flow
```
+---------------------+      +----------------------+      +--------------------+
|  Victim Frontend    | ---> |   FastAPI Backend    | ---> |  SQLite Database   |
|  (Next.js, React)   |      |   (Python 3.9)       |      |  (SQLAlchemy ORM)  |
+---------------------+      +----------------------+      +--------------------+
                                       |
                                       v
                          +--------------------------+
                          |     AI Pipelines         |
                          |  - Speech (Whisper)      |
                          |  - NLP (Indic Regex)     |
                          |  - LLM Context (Gemini)  |
                          |  - Fusion (SVI scoring)  |
                          |  - Recommendation Engine |
                          +--------------------------+
                                       ^
                                       |
                          +--------------------------+
                          |  Officer Dashboard       |
                          |  (Next.js, TailwindCSS)  |
                          +--------------------------+
```

### Technology Stack
- **Frontend**: Next.js 14, React 18, TailwindCSS, Recharts (for Analytics), Lucide React (Icons).
- **Backend**: FastAPI, Uvicorn, Python 3.9, Pydantic, SQLAlchemy.
- **Database**: SQLite (Local Dev) / PostgreSQL (Production ready).
- **AI/ML**: `google-genai` (Gemini API), Librosa (Audio features), Whisper (Speech-to-text).

---

## 🧠 The Hybrid AI Pipeline

Our AI assessment runs through a multi-stage pipeline:

1. **Local NLP Feature Extraction (`text_features.py`)**: 
   - Uses optimized, multilingual regular expressions to detect primary emotions (fear, distress, isolation, threat, urgency).
   - **Emergency Bypass**: Automatically waives length penalties if severe self-harm or imminent danger keywords are detected.
2. **LLM Contextual Analysis (`gemini_service.py`)**: 
   - Extracts deep context regarding systemic abuse, caste-based violence, or subtle threats that regex cannot catch. 
   - Returns strictly structured Pydantic schemas.
3. **Audio Preprocessing (`audio_features.py`)**: 
   - Analyzes prosody, pitch, and voice stress using Librosa.
4. **Multimodal Fusion Engine (`fusion.py` & `svi_engine.py`)**:
   - Normalizes signals from Text, Audio, and Context.
   - Calculates a final **Stress Vulnerability Index (SVI)** and generates a Risk Classification (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
5. **Recommendation Engine (`recommendation_service.py`)**:
   - Deterministic rule engine that attaches actionable steps (e.g., `OFFICER_GUIDANCE`, `LEGAL_SUPPORT`) to the case based on the SVI score and detected indicators.

---

## 🔒 Security, Privacy, and RBAC

- All case data is **anonymized** at the point of capture (e.g., `CASE-20240121-A1B2C3`).
- API access is strictly controlled using JWT-based Role-Based Access Control (RBAC).

**System Roles**:
- `VICTIM` - Citizens submitting anonymous or authenticated distress cases.
- `COUNSELLOR` - Mental health professionals who can review cases and add clinical notes.
- `LEGAL_OFFICER` - Specialists who can attach legal pathways and protection orders.
- `AUTHORIZED_STAFF` - Call center officers responsible for initial triage and live call monitoring.
- `ADMIN` - Full system oversight, audit log access, and user management.

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- **Python 3.9** (Required for pre-compiled Mac OS wheel compatibility with `pydantic-core`).
- **Node.js 18+**

### 1. Backend Setup

```bash
cd backend
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
```
Ensure you add your `GEMINI_API_KEY` to the backend `.env` file for the Live Call Analysis features to work.

```bash
# Start the backend server
uvicorn app.main:app --reload --port 8000
```
> The API Docs will be available at [http://localhost:8000/docs](http://localhost:8000/docs).
> The SQLite Database (`nhaa_triage.db`) will be automatically created and seeded on first startup.

### 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
```
Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` is set in `.env.local`.

```bash
# Start the frontend server
npm run dev
```
> The application will be available at [http://localhost:3000](http://localhost:3000).

### 3. Demo Credentials
Use these to log into the Officer Dashboard (`/login`):
- **Admin**: `admin@nhaa.local` / `admin123`
- **Officer**: `officer1@nhaa.local` / `demo123`
- **Counsellor**: `counsellor@nhaa.local` / `counsellor123`
- **Legal Officer**: `legal@nhaa.local` / `legal123`

---

## 📂 Project Structure

```
nhaa-ai-triage/
├── backend/                     
│   ├── ai/                      # Recommendation engine & ML inference bindings
│   ├── app/                     
│   │   ├── api/                 # FastAPI routes (auth, cases, live_call, analysis)
│   │   ├── database/            # SQLite Session configs
│   │   ├── ml/                  # Core feature extractors (Confidence, SVI, Fusion)
│   │   ├── models/              # SQLAlchemy Database Models
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # Business Logic (Gemini API, Hybrid Assessment)
│   │   └── config.py            # Global environment settings
│   ├── tests/                   # Pytest suite
│   └── requirements.txt
├── frontend/                    
│   ├── src/
│   │   ├── app/                 # Next.js App Router (Officer dashboard, Victim flows)
│   │   ├── components/          # Reusable Tailwind UI (Cards, Buttons, Navbars)
│   │   ├── context/             # React Context (Auth State)
│   │   └── lib/                 # Utilities and Axios API client
│   └── package.json
└── README.md
```

---

## ⚖️ License & Acknowledgments

This project is built for educational and demonstration purposes as part of the **Smart India Hackathon 2025**.

- **SIH 2025** for the problem statement (SIH26093).
- **SahaiSetu (14443)** for the use case context.
- **AI4Bharat** for Indic language model inspiration.

---

**⚠️ EMERGENCY NOTICE**
If you or someone you know is in immediate danger, please contact local emergency services (112 in India), the National Commission for Women helpline (181), Childline (1098), or the National Mental Health Helpline (08046110007). This platform is a prototype and cannot dispatch emergency services.
