# API Reference

The SahaiSetu AI Triage System exposes a REST API via FastAPI. The OpenAPI/Swagger documentation is automatically generated and is available at:

- **Interactive docs (Swagger UI):** http://localhost:8000/docs
- **OpenAPI JSON schema:** http://localhost:8000/openapi.json
- **ReDoc:** http://localhost:8000/redoc

## Authentication

All API endpoints (except `/health` and `/`) require JWT authentication.

```http
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "officer1",
  "password": "demo123"
}
```

The response includes a JWT access token. Include it in subsequent requests:

```http
Authorization: Bearer <access_token>
```

## Endpoints

### Health
- `GET /health` - Service health check

### Authentication (`/api/auth`)
- `POST /api/auth/login` - Login and get access token
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

### Cases (`/api/cases`)
- `GET /api/cases/` - List cases (with filtering)
- `GET /api/cases/{id}` - Get case details
- `GET /api/cases/priority` - Get priority cases
- `POST /api/cases/{id}/assign` - Assign case to officer

### Analysis (`/api/analysis`)
- `POST /api/analysis/text` - Analyze text input
- `POST /api/analysis/audio` - Analyze audio file
- `GET /api/analysis/{case_id}` - Get analysis for a case

### Recommendations (`/api/recommendations`)
- `GET /api/recommendations/case/{case_id}` - Get recommendations for a case
- `GET /api/recommendations/types` - List recommendation types

### Reviews (`/api/reviews` - via cases)
- `POST /api/cases/{case_id}/review` - Add human review
- `GET /api/cases/{case_id}/reviews` - List reviews for a case

### Dashboard (`/api/dashboard`)
- `GET /api/dashboard/summary` - Get summary statistics
- `GET /api/dashboard/analytics` - Get analytics data
- `GET /api/dashboard/risk-distribution` - Get risk distribution

### Audit Log (`/api/audit-log`)
- `GET /api/audit-log/` - List audit log entries (admin only)

### Users (`/api/users`)
- `GET /api/users/me` - Get current user
- `GET /api/users/` - List users (admin only)

## Response Format

All API responses follow a consistent format:

```json
{
  "data": {...},
  "meta": {
    "timestamp": "2024-01-21T10:30:00Z",
    "request_id": "uuid"
  }
}
```

Errors follow RFC 7807:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Rate Limiting

API requests are rate-limited to 100 requests/minute per user.

## Demo Mode

When `DEMO_MODE=true` (default), the AI analysis endpoints return synthetic but realistic-looking results. This is intended for development and demonstration only.
