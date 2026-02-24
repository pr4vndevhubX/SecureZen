All notable changes to the SecureZen project will be documented in this file.

## [2.0.0] - 2026-02-24

### Added
- **Interactive LogAI Control Panel**: Implemented a comprehensive dataset management UI in the `standalone_app` dashboard, allowing users to select datasets, trigger analysis, and track progress in real-time.
- **On-Demand Analysis API**: Developed new backend endpoints (`/api/logai/datasets`, `/api/logai/run-analysis`, `/api/logai/analysis-status`) supporting background thread execution of the ML pipeline.
- **Enhanced Sidebar Navigation**: Unified the LogAI features under a dedicated "Log Analysis" sidebar entry for improved discoverability.

### Fixed
- **Python 3.11 Engine Compatibility**: Resolved a critical "mutable default" error in the `logai` core library by patching `data_model.py` to use `default_factory` for pandas DataFrames.
- **Dynamic Dataset Path Resolution**: Fixed hardcoded absolute paths in `ingest_datasets.py`, enabling reliable log scanning across different environments.
- **LogAI Dashboard Connectivity**: Successfully wired the React frontend to live backend metrics, replacing placeholders with real pattern counts and anomaly timelines.

## [1.9.0] - 2026-02-19

### Added
- **High-Performance ML Ingestion**: Refactored the `standalone_app` syslog pipeline to achieve 10x–50x speed gains through singleton model initialization and direct in-memory execution.
- **Dependency Hardening**: Integrated `salesforce-merlion` and `nltk` into the project's core virtual environment for robust ML-based anomaly detection.

### Fixed
- **Dashboard Data Sync**: Restored real-time alert counts and trend charts by resolving port 5000 conflicts and ensuring the backend server correctly serves database content.
- **UI Baseline Alignment**: Removed legacy hardcoded dates from `MitreCharts.jsx`, ensuring the dashboard reflects actual analysis timestamps.
- **Path Resolution Hardening**: Fixed `ModuleNotFoundError` issues in the optimized pipeline by standardizing absolute path detection for `AlertStorage` and local libraries.

## [1.8.0] - 2026-02-17

### Added
- **CrewAI Autonomous enrichment**: Integrated multi-agent enrichment engine into both product tiers.
- **Automated Syslog Enrichment**: `standalone_app` now triggers CrewAI investigation for external IPs detected in suspicious logs.
- **Global Character Sanitization**: Implemented automated non-ASCII character removal across the codebase to resolve Windows `charmap` encoding errors.

### Fixed
- **App Root Resolution**: Fixed recursive path detection for configuration files (`agents.yaml`, `tasks.yaml`) across modular app tiers.
- **Kickoff Variable Mismatch**: Standardized `ip_addresses` template variable between Crew definitions and YAML configs.
- **Database Standardization**: Aligned all standalone components to use `syslog_alerts.db` for threat intelligence persistence.

## [1.7.0] - 2026-02-16

### Added
- **Detached Application Architecture**: Physical separation of `standalone_app/` and `siem_overlay/` with zero root-level logic.
- **Concurrent LFS Resolver**: Optimized batch-wise log extraction using `ThreadPoolExecutor`.
- **Robust Path Detection**: Dynamic `sys.path` injection in all entry points for true application isolation.

### Changed
- Refactored `start_standalone.bat` and `start_overlay.bat` for new directory structure.
- Renamed `logai_pipeline.py` to `securezen_neural_pipeline.py` in standalone mode.

### Removed
- Root-level `core/`, `features/`, and `services/` folders (Full migration to apps).

## [1.6.0] - 2026-02-13

### Added
- **Redis-based Syslog Buffer**: Enhanced ingestion reliability using a `securezen_raw_syslog` queue.
- **LogAI Deep Integration**: Implemented Drain parsing and Isolation Forest anomaly detection for standalone mode.
- **Hybrid AI Classification**: Multistage severity assessment (ML + Rules + Gemini Reasoning).
- **Isolated Syslog Alerts DB**: Standalone mode now uses `data/syslog_alerts.db` for complete data isolation.

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
