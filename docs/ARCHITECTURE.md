# System Architecture

This document describes the technical architecture of the SahaiSetu AI Triage System.

## High-Level Architecture

The system follows a **3-tier architecture** with clear separation of concerns:

```
+--------------------------------------------------+
|              Presentation Layer                  |
|  +----------------+    +-------------------+     |
|  |  Victim UI     |    |  Officer UI       |     |
|  |  (Next.js)     |    |  (Next.js)        |     |
|  +----------------+    +-------------------+     |
+--------------------------------------------------+
                       |
                       v (REST API over HTTPS)
+--------------------------------------------------+
|              Application Layer                   |
|  +--------------------------------------------+  |
|  |  FastAPI Backend (Python 3.11)             |  |
|  |  - Authentication (JWT + RBAC)             |  |
|  |  - Business Logic (Services)               |  |
|  |  - API Routes                               |  |
|  |  - Audit Logging                            |  |
|  +--------------------------------------------+  |
+--------------------------------------------------+
            |                          |
            v                          v
+---------------------+    +-------------------------+
|  AI/ML Layer        |    |  Data Layer             |
|  +---------------+  |    |  +-------------------+  |
|  | Speech (ASR)  |  |    |  | PostgreSQL 15     |  |
|  +---------------+  |    |  | - Cases           |  |
|  +---------------+  |    |  | - Assessments     |  |
|  | NLP           |  |    |  | - Recommendations |  |
|  +---------------+  |    |  | - Users           |  |
|  +---------------+  |    |  | - Audit Logs      |  |
|  | Audio         |  |    |  +-------------------+  |
|  +---------------+  |    +-------------------------+
|  +---------------+  |
|  | SVI / Fusion  |  |
|  +---------------+  |
|  +---------------+  |
|  | Recommendation|  |
|  +---------------+  |
+---------------------+
```

## Component Details

### Frontend (Next.js 14, React 18, TypeScript)

#### Pages
- `/` - Landing page (router)
- `/victim/*` - Victim-facing pages
  - `/victim/start` - New interaction setup
  - `/victim/input` - Input capture (text/audio)
  - `/victim/result` - AI assessment result
- `/officer/*` - Officer dashboard (auth required)
  - `/officer/dashboard` - Overview
  - `/officer/cases/priority` - Priority queue
  - `/officer/cases/[id]` - Case details
  - `/officer/analytics` - Analytics
  - `/officer/settings` - Settings

#### State Management
- **AuthContext** - User authentication state
- **Local component state** - Forms, modals
- **API service** - Centralized HTTP client (axios)

#### UI Components (in `components/ui/`)
- Card, Button, Input, Select, Textarea
- Badge (with risk/status variants)
- Modal, Table, ProgressSteps
- Charts (via Recharts)

### Backend (FastAPI, Python 3.11)

#### Module Structure (`backend/app/`)
```
app/
|-- main.py              # Application entry, route registration
|-- config.py            # Settings (Pydantic)
|-- database/            # DB engine, session, base
|-- models/              # SQLAlchemy ORM models
|   |-- base.py
|   |-- users.py
|   |-- cases.py
|   |-- assessments.py
|   |-- indicators.py
|   |-- interactions.py
|   |-- recommendations.py
|   |-- reviews.py
|   `-- audit_log.py
|-- schemas/             # Pydantic request/response schemas
|-- api/                 # API routes
|   |-- auth.py
|   |-- cases.py
|   |-- analysis.py
|   |-- recommendations.py
|   |-- dashboard.py
|   |-- audit_log.py
|   `-- users.py
|-- services/            # Business logic
|   |-- auth_service.py
|   |-- case_service.py
|   |-- analysis_service.py
|   `-- dashboard_service.py
|-- security/            # JWT, password hashing, RBAC
`-- utils/               # Helpers
```

#### Key Patterns
- **Async/await throughout** for high concurrency
- **Dependency injection** for DB sessions, current user
- **Service layer** for business logic (separation from API)
- **Schema validation** via Pydantic
- **Audit logging** via middleware/decorator

### AI/ML Layer (Python)

The `ai/` directory is a **standalone Python module** that can be developed and tested independently of the backend.

```
ai/
|-- audio/               # Audio feature extraction
|   |-- audio_service.py        # Real (librosa + prosody)
|   `-- demo_audio_service.py   # Demo (heuristic)
|-- speech/              # Speech-to-text
|   |-- speech_service.py       # Real (Whisper)
|   `-- demo_speech_service.py  # Demo (synthetic text)
|-- nlp/                 # NLP analysis
|   |-- nlp_service.py          # Real (IndicBERT)
|   `-- demo_nlp_service.py     # Demo (keyword-based)
|-- svi/                 # Social Vulnerability Index
|   `-- svi_service.py          # XGBoost / rule-based
|-- fusion/              # Multi-modal fusion
|   |-- fusion_service.py       # Late fusion
|   `-- demo_fusion_service.py
|-- recommendation/      # Recommendation engine
|   `-- recommendation_service.py
`-- evaluation/          # Offline eval scripts
```

#### Demo vs Real Mode
- **Demo mode** (`DEMO_MODE=true`): Uses rule-based, deterministic logic
- **Real mode** (`DEMO_MODE=false`): Loads ML models (Whisper, IndicBERT, XGBoost)

#### Data Flow (Real AI Pipeline)
1. **Audio input** -> Speech-to-text (Whisper) -> Transcribed text
2. **Text input** -> NLP (IndicBERT) -> Indicators (threat, fear, distress, etc.)
3. **Audio features** -> Audio analysis (librosa) -> Voice stress, prosody
4. **Context** -> SVI scoring -> Vulnerability score
5. **All signals** -> Fusion -> Final risk level + confidence
6. **Risk + indicators** -> Recommendation engine -> Actions

### Data Layer (PostgreSQL 15)

#### Core Tables
- `users` - Officers, counsellors, admins (RBAC)
- `cases` - Anonymized case records
- `interactions` - Text/audio inputs per case
- `assessments` - AI assessment results
- `indicators` - Detected indicators per assessment
- `recommendations` - Generated recommendations
- `reviews` - Human officer reviews
- `audit_logs` - All system actions

#### Schema Highlights
- UUID primary keys
- Foreign key relationships
- Indexes on frequently queried fields (anonymous_case_id, risk_level, status)
- Soft deletes where appropriate
- Timestamps (created_at, updated_at) on all records

## Security

### Authentication
- **JWT** (JSON Web Tokens) with 30-min expiry
- **Bcrypt** password hashing
- **Refresh tokens** for extended sessions

### Authorization (RBAC)
- 5 roles: VICTIM, COUNSELLOR, LEGAL_OFFICER, AUTHORIZED_STAFF, ADMIN
- Endpoint-level role checks via dependency injection
- Resource-level checks (officers can only see their assigned cases)

### Data Protection
- **No PII** stored - only anonymized case IDs
- **HTTPS only** in production
- **CORS** restricted to known origins
- **Rate limiting** to prevent abuse
- **Audit logging** of all sensitive operations

## Deployment

### Development
- Docker Compose with hot-reload
- Local database with sample data
- Demo AI services

### Production
- Containerized (Docker)
- Orchestration via Kubernetes / Docker Swarm
- Managed PostgreSQL (RDS, Cloud SQL, etc.)
- Real AI models served via separate inference service
- CDN for frontend assets
- Load balancer for backend
- Monitoring via Prometheus + Grafana
- Centralized logging (ELK stack)

## Scalability

The architecture is designed to scale horizontally:
- **Stateless backend** - Can run multiple instances behind a load balancer
- **Async I/O** - FastAPI handles thousands of concurrent connections
- **Database connection pooling** - For efficient DB access
- **Caching layer** (Redis) - For dashboard analytics
- **Queue system** (Celery / RabbitMQ) - For async AI inference

## Future Enhancements

- **Real-time call transcription** with live updates
- **Voice biometrics** for caller identification (with consent)
- **Predictive analytics** for resource allocation
- **Mobile app** for officers on the go
- **Integration** with existing helpline systems (14443, 181, 1098, etc.)
- **Multi-tenancy** for different states/departments
- **Advanced analytics** with ML-driven insights
