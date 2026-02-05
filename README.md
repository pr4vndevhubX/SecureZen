# SecureZen AI-Powered Threat Intelligence System
## Autonomous Security Operations Platform with Multi-Agent Intelligence

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Executive Summary

**SecureZen** is an advanced threat intelligence and autonomous SOC platform that integrates **Wazuh SIEM** with the **CrewAI multi-agent framework**. It automates the investigation of security alerts and indicators of compromise (IOCs) using a swarm of specialized AI agents. By combining large language models (LLMs), internal RAG systems for MITRE ATT&CK mapping, and external threat feeds, SecureZen provides deep, context-aware security analysis with professional PDF reporting.

### Key Capabilities

- **Neural Agent Swarm**: 10 specialized AI agents working collaboratively to investigate threats.
- **Deep Threat Intel Integration**: Native connectors for VirusTotal, AbuseIPDB, and Yeti.
- **Autonomous Alert Triage**: Automated severity assessment and prioritization using neural logic.
- **MITRE ATT&CK Enrichment**: Semantic mapping of behaviors to techniques via internal Knowledge Base.
- **Wazuh SIEM Historian**: Correlation with historical internal logs and alerts.
- **Interactive SOC Dashboard**: Real-time visualization of threats, trends, and automated analysis results.
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
nano .env
# Required: VIRUSTOTAL_API_KEY, ABUSEIPDB_API_KEY, GROQ_API_KEY, JWT_SECRET_KEY

# 5. Start the backend services
# Start RAG service (ensure port 8001 is used)
cd services/rag-service && python main.py &

# Start main API (Port 5000)
cd ../..
python app.py
```

### First Investigation

```bash
# Trigger an investigation via CLI
python main.py
# Enter IP: 8.8.8.8
```

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       WAZUH SIEM (Alert Source)                      │
│                    Standard OSSEC/Wazuh Infrastructure               │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              INTEGRATION GATEWAY / WEBHOOK (Port 5000)               │
│                      AI SOC Platform Backend                         │
├─────────────────────────────────────────────────────────────────────┤
│  Routing & Triage Logic:                                             │
│  • Level < 6   → Low Priority / Dashboard Only                      │
│  • Level 8-9   → AI Explanation + Enrichment                        │
│  • Level 10+   → Neural Swarm Investigation Flagged                 │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   MICROSERVICES LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│  RAG Service (8001)     Auth Service          Database (SQLite)     │
│  • MITRE ATT&CK KB      • JWT Authentication  • Alert Persistence   │
│  • Semantic Search      • RBAC                • Investigation Logs  │
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

**Author**: PRAVEENKUMAR
**Project**: [SecureZen GitHub](https://github.com/pr4vndevhubX/SecureZen)

**Last Updated**: 2026-02-05
**Version**: 1.2.0
