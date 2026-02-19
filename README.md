# SecureZen AI-Powered Threat Intelligence System
## Autonomous Security Operations Platform with Multi-Agent Intelligence (v1.9.0)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Executive Summary

**SecureZen** is an advanced threat intelligence and autonomous SOC platform that leverages **LogAI** for deep analysis of raw **Syslog** streams. It automates the investigation of security alerts and indicators of compromise (IOCs) using a swarm of specialized AI agents. By combining large language models (LLMs), internal RAG systems for MITRE ATT&CK mapping, and external threat feeds, SecureZen provides context-aware security intelligence with a modular architecture that supports both raw log analysis and optional SIEM integrations like Wazuh.

### Key Capabilities

- **Neural Agent Swarm**: 10 specialized AI agents working collaboratively to investigate threats.
- **SecureZen Analyst**: Conversational SOC Copilot for natural language log searching, severity breakdowns, and forensic triage.
- **Conversational Memory**: Supports multi-turn investigations by remembering session context (Powered by AURA).
- **Deep Threat Intel Integration**: Native connectors for VirusTotal, AbuseIPDB, and Yeti.
- **Autonomous Alert Triage**: Automated severity assessment and prioritization using neural logic.
- **MITRE ATT&CK Enrichment**: Mapping behaviors to techniques via internal Knowledge Base.
- **Interactive SOC Dashboard**: Real-time visualization of threats, trends, and automated analysis results.
- **Interactive Kill Chain Filtering**: Filter alerts dynamically by clicking on Attack Phases.
- **Dynamic CVE Radar Chart**: Real-time correlation of SIEM alerts with Vulnerability metrics.
- **Professional Reporting**: Automated generation of comprehensive PDF investigation reports.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [Service Components](#service-components)
4. [CrewAI Agent System](#crewai-agent-system)
5. [Integration Workflow](#integration-workflow)
6. [API Endpoints](#api-endpoints)
7. [Documentation](#documentation)
8. [Development Roadmap](#development-roadmap)

---

## Quick Start

### Prerequisites

- **Operating System**: Linux (Ubuntu 20.04+ recommended) or Windows with WSL2
- **Python**: 3.11+ 
- **Database**: SQLite3 (included)
- **External APIs**: VirusTotal, AbuseIPDB, and Groq (for LLM orchestration)

### 5-Minute Setup

```bash
# 1. Clone repository
git clone <your-repository-url>
cd SecureZen

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Set VIRUSTOTAL_API_KEY, ABUSEIPDB_API_KEY, GROQ_API_KEY, JWT_SECRET_KEY

# 5. Start the Product Tier you need:

# OPTION A: Standalone Raw Log Intelligence
cd standalone_app
../start_standalone.bat

# OPTION B: SIEM Overlay AI SOC
cd siem_overlay
../start_overlay.bat
```

### Which version to use?

| Product Version | Run Command | Use Case |
| :--- | :--- | :--- |
| **Standalone** | `start_standalone.bat` | Clients with raw syslogs; focus on LogAI clustering. |
| **SIEM Overlay** | `start_overlay.bat` | Clients with Wazuh; focus on Agentic investigations. |

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL SYSLOG SOURCES                        │
│                (Servers, Firewalls, Application Logs)                │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              SYSLOG LISTENER & REDIS BUFFER (Port 5140)              │
│                 "Shock Absorber" Ingestion Layer                     │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                DETACHED APPLICATION ARCHITECTURE                     │
│  ├─────────────────────────────────┐ ├───────────────────────────────┤ │
│  │   [standalone_app/]             │ │    [siem_overlay/]            │ │
│  │  • syslog_alerts.db             │ │  • wazuh_alerts.db            │ │
│  │  • Neural Pipeline (LogAI)      │ │  • CrewAI Agent Swarm         │ │
│  │  • Syslog Ingestion             │ │  • Wazuh Webhook & Tools      │ │
│  └─────────────────────────────────┘ └───────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   MICROSERVICES LAYER                                │
│  ├─────────────────────────────────────────────────────────────────┤ │
│  │  RAG Service (8001)     Auth Service          Database (SQLite)   │ │
│  │  • MITRE ATT&CK KB      • JWT Authentication  • Alert Persistence │ │
│  │  • Semantic Search      • RBAC                • Investigation Logs│ │
│  └─────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                CREWAI NEURAL INVESTIGATION LAYER                     │
├─────────────────────────────────────────────────────────────────────┤
│  10 Specialized Agents:                                              │
│  1. Coordinator         6. SIEM Historian                            │
│  2. VirusTotal Spec     7. Alert Triage Analyst                      │
│  3. AbuseIPDB Analyst   8. MITRE Context Analyst                     │
│  4. Yeti Analyst        9. Correlation Analyst                       │
│  5. ML Classifier      10. Report Generator                          │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
                    ┌────────────────────┐
                    │   PDF Report       │
                    │   Generated        │
                    └────────────────────┘
```

---

## CrewAI Agent System

SecureZen utilizes a sequential workflow of **10 specialized agents**:

1.  **Coordinator**: Orchestrates the investigation and validates input.
2.  **VirusTotal Specialist**: Queries external reputation feeds.
3.  **AbuseIPDB Analyst**: Checks community abuse reports and ISP data.
4.  **Internal Intel Analyst**: Contextualizes threats using the Yeti platform.
5.  **SIEM Historian**: Digs into Wazuh logs for internal correlation.
6.  **ML Traffic Classifier**: Analyzes network behavior patterns.
7.  **Alert Triage Analyst**: Assigns neural priority levels (P1-P5).
8.  **MITRE ATT&CK Analyst**: Maps behaviors to the ATT&CK framework via RAG.
9.  **Correlation Analyst**: Synthesizes all data into a final threat verdict.
10. **Report Generator**: Produces the professional investigation PDF.

---

## API Endpoints

### AI SOC Backend (Port 5000)

```
POST /api/auth/login       - User authentication
POST /api/analyze-ioc      - Trigger neural investigation
GET  /api/dashboard-stats  - Retrieve SOC metrics
POST /api/ai/explain-alert - AI-powered alert simplified explanation
POST /api/mitre/search     - Semantic search across ATT&CK KB
```

---

## Documentation

Detailed documentation is available in the `docs/` directory:

1.  **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and data flow.
2.  **[INSTALLATION.md](docs/INSTALLATION.md)** - Comprehensive setup guide.
3.  **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Guide for contributors.
4.  **[MONITORING.md](docs/MONITORING.md)** - Observability and metrics.
5.  **[SYSLOG_PIPELINE.md](standalone_app/features/syslog_analysis/syslog_pipeline.md)** - Detailed Syslog-AI architecture.
6.  **[CHANGELOG.md](docs/CHANGELOG.md)** - Recent updates and version history.

---

## 📅 Version 1.9.0 Update (Feb 19, 2026)

### 🏎️ High-Speed ML Ingestion (10x–50x Boost)
SecureZen standalone mode now features a highly optimized neural pipeline for bulk log ingestion.

- **Singleton Model Initialization**: Analyzers (LogParser, AnomalyDetector) now initialize once per session instead of once per file, eliminating redundant mathematical overhead.
- **In-Memory Sequential Processing**: Switched from multi-process callouts to direct in-memory execution, drastically reducing OS-level context switching.
- **Dependency Hardening**: Standardized the environment with `merlion` and `nltk` to ensure the "Neural Brain" is fully functional out-of-the-box.
- **Dashboard Synchronization**: Fixed critical port conflicts and hardcoded UI mock-ups; the dashboard now displays high-fidelity real-time truth.

---

---

---

## 📅 Version 1.8.0 Update (Feb 17, 2026)

### 🧠 Autonomous Threat Enrichment Integration
SecureZen now features deep integration of the CrewAI multi-agent engine across all product tiers.

- **Automated Standalone Enrichment**: The `optimized_pipeline.py` now automatically triggers the `IPIntelligenceCrew` for any unique external IPs detected during log processing.
- **Background Intelligence Threads**: Enrichment investigations run in non-blocking background threads, ensuring the high-speed syslog pipeline remains responsive.
- **Windows Stability Hardened**: Successfully resolved critical Windows-specific bugs, including `charmap` encoding errors (via global non-ASCII sanitization) and path resolution issues.
- **Data Persistence Standardized**: Enriched threat intelligence (reputation scores, MITRE context, and recommendations) is now consistently stored in `syslog_alerts.db`.

---

## 📅 Version 1.7.0 Update (Feb 16, 2026)

### 🚀 Complete Decoupling: Detached Multi-App Architecture
SecureZen has reached architectural maturity by physically separating into two independent, self-contained applications.

- **Physical Isolation**: Root-level `core/` and `features/` folders have been removed. All logic is now encapsulated within `standalone_app/` and `siem_overlay/`.
- **Zero-Dependency Imports**: Implemented robust `sys.path` detection across all entry points, allowing each app to resolve its local `utils/`, `services/`, and `tools/` independently.
- **Concurrent LFS Resolver**: Recreated and optimized `bulk_lfs_resolver.py` with **ThreadPoolExecutor** for high-speed, batch-wise extraction of log datasets from Git LFS pointers.
- **Unified Startup Optimization**: Refactored `.bat` scripts to handle the new directory traversal and renamed pipelines (`securezen_neural_pipeline.py`).
- **Database Autonomy**: Hardened the separation between `syslog_alerts.db` and `wazuh_alerts.db`, ensuring strictly zero cross-talk between product tiers.

---

## 📅 Version 1.6.0 Update (Feb 13, 2026)

---

## 📅 Version 1.5.0 Update (Feb 12, 2026)

### 🚀 Major Refactor: Multi-App Architecture 
SecureZen has been transformed from a hybrid single-app into a specialized **Multi-App platform**.

- **Dedicated Product Tiers**: Clean separation between `syslog` (LogAI) and `siem` (Wazuh/CrewAI) features.
- **Product Folders**: Specialized logic located in `core/securezen/syslog` and `core/securezen/siem`.
- **Shared Foundation**: Core logic extracted to `base_app.py` for high performance and consistency.
- **Build-Time Toggles**: React frontend now uses environment variables to physically toggle features.

### 🛠️ Key Improvements
- **Absolute Path Resolution**: Fixed recurring database errors by implementing robust absolute path resolution in all utility classes (`ThreatDatabase`, `UserDatabase`).
- **One-Click Startup**: Added `start_standalone.bat` and `start_overlay.bat` for immediate deployment of specific tiers.
- **Legacy Cleanup**: Removed over 500 lines of redundant hybrid code.

---

## Development Roadmap

- [x] Multi-Agent Core Orchestration
- [x] Wazuh SIEM Integration
- [x] MITRE ATT&CK RAG Implementation
- [ ] Multi-tenant Enterprise Support
- [ ] Automated Playbook Response (SOAR)
- [ ] Mobile App Security Views

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Contact

**Author**: PRAVEENKUMAR / KRYA SOLUTIONS PRIVATE LIMITED
**Project**: [SecureZen GitHub](https://github.com/pr4vndevhubX/SecureZen)

**Last Updated**: 2026-02-19
**Version**: 1.9.0
