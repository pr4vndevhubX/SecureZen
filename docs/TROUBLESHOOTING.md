# Troubleshooting Guide
## SecureZen AI-powered Threat Intelligence System

Common issues and remediation steps for the SecureZen platform.

---

## Connection Issues

### Backend unreachable (Connection Refused)
- **Check Ports**: Ensure `app.py` is running on port 5000.
- **Firewall**: Ensure the port is open if accessing from a different machine.
- **PID Check**: `lsof -i :5000` to see if another process is holding the port.

### RAG Service unreachable
- Ensure the RAG service is running in `services/rag-service/` on port 8001.
- Check that `chromadb` is initialized and the vector database files exist in the `data/` or service directory.

---

## Agent Failures

### "Agent Stopped due to Max Iterations"
- This usually happens when an agent gets stuck in a loop or cannot find a tool it needs.
- **Fix**: Check `config/agents.yaml` backstories. Ensure the agent has the correct tool assigned in `crew.py`.

### Empty Investigation Results
- If an investigation returns no data, check your API usage for VirusTotal or AbuseIPDB.
- Ensure the `ip_addresses` input is correctly passed to the crew kickoff.

---

## Database Issues

### User cannot login
- Check if the user exists: `python diag_auth.py` (if available) or check `auth.db`.
- Reset a user: `python reset_user.py`.

### Alerts not showing on dashboard
- Ensure the Wazuh webhook integration is active.
- Check `threat_intel.db` for the `alerts` table content.

---

**Author**: PRAVEENKUMAR
**Last Updated**: 2026-02-05
