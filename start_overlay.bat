@echo off
echo Starting SecureZen SIEM Overlay Mode...

:: Start Webhook (Layer 1 Ingestion)
start cmd /k "uv run python features/wazuh_siem/webhook.py"

:: Start SIEM Backend (Layer 2 Processing)
start cmd /k "uv run python server_overlay.py"

:: Start Common Dashboard
cd frontend
start cmd /k "npm run dev"

echo Overlay mode starting on port 5000 (Backend), 3030 (Webhook), and React Dev Server.
