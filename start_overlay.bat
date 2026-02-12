@echo off
echo Starting SecureZen Overlay (SIEM/Wazuh Focused)...
set SECUREZEN_MODE=overlay
start cmd /k "uv run python core/securezen/siem/server.py"
cd frontend
start cmd /k "npm run dev -- --mode overlay"
echo Overlay mode starting on port 5000 (Backend) and React Dev Server.
