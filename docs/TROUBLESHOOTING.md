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

## Dashboard Visualization Issues

### CVE Radar Chart is Flat (Empty)
- **Cause**: No alerts in the database match the specific CVE keywords (e.g., "dark web", "ssl").
- **Fix**: Check your `alerts` table. The chart relies on matching `rule_description` against specific keywords defined in `utils/database.py`. You can inject test alerts to verify functionality.

### Kill Chain Filter Mismatch
- **Issue**: Clicking a phase (e.g., "Reconnaissance") shows no events in the list.
- **Cause**: The alert's `killChainPhase` property might not match the chart's category.
- **Fix**: Ensure `App.jsx` and `MitreEvents.jsx` are synchronized. The `getKillChainPhase` function in App.jsx determines the tag, and the Event component filters by it.

---

## AI Copilot (SecureZen) Issues

### Copilot Reports "0 Alerts" when Dashboard shows thousands
- **Cause**: Time range mismatch. Dashboards often show historical data, while the Copilot defaults to a strictly recent window. If documentation suggests there are alerts but the bot says 0, the data is likely older than the bot's threshold.
- **Fix**: Run `test/inject_critical_alerts.py` to seed the database with current-timestamp events. SecureZen is designed to prioritize real-time truth over historical bulk.

### "I'm having trouble connecting to my AI brain"
- **Cause**: This is usually a Logic Error in the `CopilotService`.
- **Fix**: Check `services/copilot_service.py`. Ensure the `intent_prompt` is defined inside the `process_message` method. Verify that the LLM API (Groq/OpenAI) hasn't hit a rate limit.

### Missing IP Extraction in Logs
- **Issue**: Webhook receives alerts but logs say "No IPs extracted".
- **Fix**: Check the `full_alert` structure from Wazuh. The regex inside `webhook.py` or `CopilotService` may need adjustment for your specific log format (e.g., JSON vs. Syslog).

---

## Build & Dependencies

### Missing UI Components (e.g., Lucide Icons)
- **Fix**: Run `npm install lucide-react` in the `frontend` directory. If using Vite, clear the cache with `rm -rf node_modules/.vite` and restart the dashboard.

---

**Author**: PRAVEENKUMAR / KRYA SOLUTIONS PRIVATE LIMITED
**Last Updated**: 2026-02-09
