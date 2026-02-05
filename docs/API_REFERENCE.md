# API Reference
## SecureZen AI-powered Threat Intelligence System

Detailed documentation for the SecureZen FastAPI endpoints.

---

## Authentication

### POST `/api/auth/register`
Register a new user account.
- **Body**: `{"email": "...", "password": "...", "full_name": "..."}`
- **Response**: `{"access_token": "...", "user": {...}}`

### POST `/api/auth/login`
Authenticate a user and receive a JWT token.
- **Body**: `{"email": "...", "password": "..."}`
- **Response**: `{"access_token": "...", "user": {...}}`

---

## Intelligence & Analysis

### POST `/api/analyze-ioc`
Trigger a full CrewAI neural investigation for a specific Indicator of Compromise (IOC).
- **Body**: `{"ioc": "1.2.3.4"}`
- **Response**: `{"analysis": "Markdown Analysis Result...", "ioc": "1.2.3.4"}`

### POST `/api/ai/explain-alert`
Get a simplified, AI-powered explanation of a technical security log.
- **Body**: `{"message": "Raw log data..."}`
- **Response**: `{"explanation": "...", "severity": "...", "action": "..."}`

---

## Dashboard Data

### GET `/api/dashboard-stats`
Retrieve comprehensive metrics for the SOC dashboard, including threat funnels and trends.
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Response**: `{"stats": {...}, "alerts": [...], "alert_trends": [...]}`

### GET `/api/cve-stats`
Get a summary of vulnerability intelligence.
- **Response**: `{"total": 123, "critical": 10, ...}`

---

## Semantic Search (RAG)

### POST `/api/mitre/search`
Perform a vector-based semantic search for MITRE ATT&CK techniques.
- **Body**: `{"message": "Query string..."}`
- **Response**: `{"results": [{"technique_id": "...", "document": "..."}]}`

---

**Author**: PRAVEENKUMAR
**Last Updated**: 2026-02-05
