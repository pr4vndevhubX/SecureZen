# System Architecture
## SecureZen AI-powered Threat Intelligence Platform

Comprehensive technical design and architectural documentation.

---

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Design Principles](#design-principles)
3. [Component Architecture](#component-architecture)
4. [Modular Plugin System](#modular-plugin-system)
5. [Data Flow (Standalone vs Overlay)](#data-flow)
6. [Agent Orchestration](#agent-orchestration)
7. [Security Framework](#security-framework)

---

## Architectural Overview

### High-Level System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ AI SOC Dashboard│  │ Wazuh Console│  │ Reports (PDF)    │   │
│  │   (Frontend)    │  │ (Integration)│  │ (Generated)      │   │
│  └─────────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION & API LAYER                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │             AI SOC Platform Backend (Port 5000)            │  │
│  │  • FastAPI Enterprise API                                 │  │
│  │  • Smart Alert Routing                                    │  │
│  │  • JWT Authentication & User Management                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                   AI/ML SERVICES LAYER                           │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │ Alert Triage │  │   RAG Service   │  │  LLM Backend     │   │
│  │  (Neural)    │  │  (Port 8001)    │  │  (Groq/LLama)    │   │
│  │              │  │                 │  │                  │   │
│  │ • Severity   │  │ • ChromaDB      │  │ • Agent Logic    │   │
│  │ • Logic      │  │ • MITRE KB      │  │ • Reasoning      │   │
│  └──────────────┘  └─────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              INGESTION & BUFFERING LAYER                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  High-Performance Syslog Pipeline (Port 5140)             │  │
│  │  • UDP Ingestion ➔ Redis Buffer ➔ LogAI Worker Pipeline   │  │
│  │  • Preprocessing ➔ Drain Parsing ➔ ML Anomaly Detection   │  │
│  │  • Severity Escalation (Gemini reasoning) ➔ AlertStorage  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│              MODULAR FEATURE ARCHITECTURE                       │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ core/securezen   │  │ features/syslog │  │ features/wazuh │  │
│  │ • Brain & Crew   │  │ • LogAI Source  │  │ • SIEM Backup  │  │
│  │ • Dashboard API  │  │ • Neural Pipe   │  │ • Webhook In   │  │
│  └──────────────────┘  └─────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA & REPUTATION LAYER                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ VirusTotal │  │ AbuseIPDB  │  │   YETI     │  │  Wazuh   │  │
│  │    API     │  │    API     │  │ Platform   │  │  Events  │  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. Autonomous Intelligence
The system moves beyond simple rule-based detection to autonomous investigation. Agents reason about evidence and provide human-readable findings.

### 2. Micro-Orchestration
Each security task (IP checking, log searching, MITRE mapping) is handled by a specialized agent, ensuring high quality and modularity.

### 3. Context-Awareness (RAG)
SecureZen uses **Retrieval Augmented Generation** to provide specific MITRE ATT&CK context, ensuring AI agents are grounded in security domain knowledge.

### 4. Hybrid Data Integrity
Combines external reputation feeds (global view) with internal Wazuh SIEM telemetry (local view) for a 360-degree threat perspective.

---

## Component Architecture

### AI SOC Backend (Port 5000)
**Technology**: Python + FastAPI + SQLAlchemy/SQLite

The system uses a **Multi-App Entry Point** model for robust feature separation:
- **[base_app.py](file:///c:/Users/psuresh/OneDrive%20-%20KRYA%20SOLUTIONS%20PRIVATE%20LIMITED/Desktop/KYD/Agentic-ai-02/IP-alone-Crewai/ip-intel-crewai/core/securezen/base_app.py)**: The shared foundation containing authentication, middleware, and singleton database connections.
- **Dedicated Servers**: Specialized server files (`server_standalone.py`, `server_overlay.py`) that only load the required API routes for specific product tiers.

### RAG Service (Port 8001)
**Technology**: ChromaDB + Sentence Transformers

Provides semantic search capabilities for security frameworks:
- **Vector Storage**: Stores embeddings of the MITRE ATT&CK knowledge base.
- **Semantic Retrieval**: Allows agents to find TTPs based on natural language descriptions of behavior.

### SecureZen Analyst (Conversational NLU)
**Technology**: LLM-driven Intent Classification + Conversational Memory

A conversational interface that provides:
- **Natural Language Querying**: Translates user requests into SQL constraints for the Wazuh database.
- **Narrative Breakdowns**: Performs statistical analysis on alert clusters to provide human-readable summaries.
- **Forensic Detection**: Specific `ANALYZE` engine for triage of critical suspicious behaviors.

---

## Multi-App Architecture (Exclusive Product Tiers)

SecureZen is structured as a **Multi-App platform**, allowing for clean separation between raw log analysis and SIEM enhancement.

### 🛡️ 1. Standalone Raw Log Intelligence
- **Directory**: `standalone_app/`
- **Engine**: **SecureZen Neural Engine** (`securezen_neural_pipeline.py`).
- **Focus**: Real-time syslog anomaly detection and clustering.
- **Database**: `data/syslog_alerts.db`.

### 🧠 2. SIEM Overlay AI SOC
- **Directory**: `siem_overlay/`
- **Engine**: **CrewAI Agent Swarm** (`crew.py`).
- **Focus**: Agentic investigation of SIEM alerts and automated response.
- **Database**: `data/wazuh_alerts.db`.

### ⚛️ Build-Time Frontend Modularity
The React dashboard utilizes `VITE_SECUREZEN_MODE` environment variables to toggle UI features at build-time, ensuring that clients only receive the code for their purchased features.

---

## Data Flow

### 1. Alert Triage Flow (Syslog-LogAI)
1. **Event**: A raw syslog event occurs on a network device or server.
2. **Ingestion**: `syslog_listener.py` captures the UDP packet and pushes to Redis.
3. **Deep Analysis**: `logai_pipeline.py` consumes the log:
   - **Clean**: Normalizes text and removes noise.
   - **Parse**: Uses the **Drain** algorithm to extract templates and parameters.
   - **Detect**: Heuristic and ML-based anomaly detection identifies threats.
4. **Promotion**: High-score events are promoted to the `AlertStorage` database.
5. **Investigation**: CrewAI investigation is triggered for critical detections.

### 2. Investigation Swarm Flow
1. **Coordinator Agent** validates the target IOC (IP/Domain).
2. **Intelligence Agents** (VT, AbuseIPDB, Yeti) gather global reputation data.
3. **Internal Data Agents** (SIEM Historian) query alerts for local correlation.
4. **Context Agent** maps findings to MITRE ATT&CK via RAG.
5. **Correlation Agent** synthesizes a weighted risk score and verdict.
6. **Report Agent** compiles a Markdown report, subsequently converted to PDF.

---

## Agent Orchestration

SecureZen uses a **Sequential Process** via CrewAI:
- **Consistency**: Ensures data flows logically from raw collection to technical analysis to final reporting.
- **Memory**: Common task context allows the "Correlation Analyst" to see every detail discovered by the "VirusTotal Specialist" or "SIEM Historian".

---

**Author**: PRAVEENKUMAR / KRYA SOLUTIONS PRIVATE LIMITED
**Last Updated**: 2026-02-13
