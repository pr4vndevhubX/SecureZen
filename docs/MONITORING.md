# Monitoring & Observability
## SecureZen AI-powered Threat Intelligence System

Detailed guide for monitoring the health and performance of the SecureZen platform.

---

## Health Checks

SecureZen provides a heartbeat endpoint to verify the API and database connectivity.

**Endpoint**: `GET /`
**Response**:
```json
{
  "status": "active",
  "service": "AI SOC Backend"
}
```

---

## Log Management

### Backend Logs
Logs are output directly to the console by default. For production visibility, redirect stdout to a file:
```bash
python app.py >> logs/backend.log 2>&1
```

### CrewAI Execution Logs
Individual agent thoughts and tool outputs can be captured by setting `verbose: true` in `config/agents.yaml`. These are invaluable for debugging "Reasoning Loops" or tool failures.

---

## Performance Monitoring

### Investigation Latency
Average investigation time ranges from **60 - 150 seconds** depending on:
- Complexity of the input.
- LLM provider latency (Groq vs OpenAI).
- Network response time of VT/AbuseIPDB.

### Memory Usage
- **RAG Service**: Requires ~2GB RAM for ChromaDB indexing (with default embeddings).
- **LLM Context**: The `app.py` context window is optimized to keep memory per-request low.

---

## Future Observability Integrations

SecureZen is designed to support future metrics exporting:
- **Prometheus**: Export `/metrics` for alert volume and agent success rates.
- **Grafana**: Pre-built dashboard for visualizing the "SOC Threat Funnel".
- **Loki**: Aggregated logging for multi-service debugging.

---

**Author**: PRAVEENKUMAR
**Last Updated**: 2026-02-05
