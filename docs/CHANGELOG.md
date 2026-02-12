# Changelog

All notable changes to the SecureZen project will be documented in this file.

## [1.5.0] - 2026-02-12

### Added
- **Multi-App Architecture**: Dedicated folders and entry points for `syslog` and `siem` tiers.
- **Standalone Mode**: Dedicated server and dashboard for pre-SIEM LogAI analysis.
- **SIEM Overlay Mode**: Dedicated server and dashboard for Agentic SIEM investigations.
- **Shared Core**: `core/securezen/base_app.py` and `shared_dashboard.py` for logic reusability.
- **Startup Automation**: `start_standalone.bat` and `start_overlay.bat` scripts for deployment.
- **Frontend Build Modes**: Specialized `.env.standalone` and `.env.overlay` for React builds.

### Changed
- Refactored `ThreatDatabase`, `UserDatabase`, and `AlertStorage` to use **Absolute Path Resolution** based on project root.
- Updated `App.jsx` to support conditional feature rendering based on `VITE_SECUREZEN_MODE`.
- Migration of LogAI and SIEM logic into specialized subdirectories.

### Fixed
- Resolved `sqlite3.OperationalError` caused by relative path issues during backend initialization.

### Removed
- Legacy `app.py`, `dashboard.py`, and `plugins.py` (Hybrid mode cleanup).
- Redundant `app.js` and `main.py` entry points.
