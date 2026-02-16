@echo off
echo Starting SecureZen Standalone (LogAI Focused)...
set SECUREZEN_MODE=standalone
set SECUREZEN_DB_PATH=data/syslog_alerts.db

:: 1. Start Ingestion & Processing (Grouped in one window)
echo Starting Syslog Listener and Neural Pipeline...
start "SecureZen: Syslog Pipeline" cmd /k "cd standalone_app && uv run python features/syslog_analysis/syslog_listener.py & echo --- & uv run python features/syslog_analysis/securezen_neural_pipeline.py"

:: 2. Start Standalone Backend
start "SecureZen: Backend" cmd /k "cd standalone_app && uv run python main.py"

:: 3. Start Common Dashboard
cd frontend
start "SecureZen: Dashboard" cmd /k "npm run dev"

echo Standalone mode starting on port 5000 (Backend), UDP 5140 (Syslog), and React Dev Server.
