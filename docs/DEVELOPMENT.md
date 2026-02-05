# Development Guide
## SecureZen AI-powered Threat Intelligence System

Guide for developers and security engineers contributing to the SecureZen platform.

---

## Project Structure

```bash
SecureZen/
├── app.py                 # Main FastAPI Backend & Dashboard API
├── crew.py                # CrewAI Agent Orchestration & Logic
├── main.py                # CLI Entry Point for investigations
├── config/                # Agent & Task YAML configurations
│   ├── agents.yaml
│   └── tasks.yaml
├── services/
│   └── rag-service/       # MITRE ATT&CK Vector Search Service
├── tools/                 # Custom CrewAI Tools (VT, AbuseIPDB, Wazuh, etc.)
├── utils/                 # Shared utilities (DB, Auth, Connectors)
├── frontend/              # SOC Dashboard UI (Vite/React)
└── data/                  # Persistent storage (SQLite DBs)
```

---

## Adding New Intelligence Sources

To add a new reputation source (e.g., Shodan, Censys):

1.  **Create the Tool**: Add a new file in `tools/` using the `crewai.tools.BaseTool` class.
```python
from crewai.tools import BaseTool

class ShodanTool(BaseTool):
    name: str = "Shodan Query"
    description: str = "Detailed host information from Shodan"

    def _run(self, ip: str) -> str:
        # Implement Shodan API logic here
        return "Shodan Data..."
```

2.  **Define the Agent**: Update `config/agents.yaml` with a specialized agent role.
3.  **Define the Task**: Update `config/tasks.yaml`.
4.  **Register in Crew**: Import the tool and update the `IPIntelligenceCrew` class in `crew.py`.

---

## Working with the Neural Triage

The logic for automated alert triage resides in `app.py`. If you want to modify how alerts are prioritized or when a swarm investigation is triggered, look for the `/api/webhook` or `/api/dashboard-stats` logic.

### Modifying Triage Rules:
- **Low Severity (< 6)**: Logged to database, displayed on dashboard events.
- **Medium Severity (6 - 9)**: Triggered AI-assisted explanation (`/api/ai/explain-alert`).
- **Critical Severity (10+)**: Set a flag for immediate CrewAI investigation.

---

## Coding Standards

- **Type Hinting**: Use Python type hints for all functions.
- **Async/Await**: Use asynchronous database calls where possible (using `httpx` for external APIs).
- **Agent Backstories**: When updating `agents.yaml`, ensure the backstory provides enough context for the LLM to understand its professional role in a SOC.

---

## Testing

### Unit Tests
Run the test suite using pytest:
```bash
pytest test/
```

### Manual API Verification
Use the FastAPI Docs (Swagger UI) available at:
`http://localhost:5000/docs`

---

**Author**: PRAVEENKUMAR
**Last Updated**: 2026-02-05
