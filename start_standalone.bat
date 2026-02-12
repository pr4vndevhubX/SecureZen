@echo off
echo Starting SecureZen Standalone (LogAI Focused)...
set SECUREZEN_MODE=standalone
start cmd /k "uv run python core/securezen/syslog/server.py"
cd frontend
start cmd /k "npm run dev -- --mode standalone"
echo Standalone mode starting on port 5000 (Backend) and React Dev Server.
