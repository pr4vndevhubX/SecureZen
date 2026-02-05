# System Architecture
## SecureZen AI-powered Threat Intelligence Platform

Comprehensive technical design and architectural documentation.

---

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Design Principles](#design-principles)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Agent Orchestration](#agent-orchestration)
6. [Security Framework](#security-framework)

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
│              CREWAI ORCHESTRATION LAYER                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Autonomous Agent Swarms (10 Specialized Roles)           │  │
│  │  • External Recon → Internal Correlation → AI Insight     │  │
│  │  • Sequential Reasoning & Context Passing                 │  │
│  └───────────────────────────────────────────────────────────┘  │
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

The central nervous system of SecureZen. It handles:
- **Authentication**: JWT-based secure access for SOC analysts.
- **Alert Ingestion**: Receiving telemetry from Wazuh agents.
- **Dynamic Dashboarding**: Calculating real-time stats (Threat Funnel, Alert Trends).
- **Crew Triggering**: Orchestrating the CrewAI "kickoff" process for critical IOCs.

### RAG Service (Port 8001)
**Technology**: ChromaDB + Sentence Transformers

Provides semantic search capabilities for security frameworks:
- **Vector Storage**: Stores embeddings of the MITRE ATT&CK knowledge base.
- **Semantic Retrieval**: Allows agents to find TTPs based on natural language descriptions of behavior.

---

## Data Flow

### 1. Alert Triage Flow
1. **Event**: A security event occurs on an endpoint.
2. **Detection**: Wazuh manager triggers a webhook to `SecureZen`.
3. **Filtering**: `app.py` assesses the rule level.
4. **Intelligence Enrichment**: 
   - Level 8+: AI generates a simplified explanation.
   - Level 10+: Full CrewAI investigation is triggered automatically.

### 2. Investigation Swarm Flow
1. **Coordinator Agent** validates the target IOC (IP/Domain).
2. **Intelligence Agents** (VT, AbuseIPDB, Yeti) gather global reputation data.
3. **Internal Data Agents** (SIEM Historian) query Wazuh for local correlation.
4. **Context Agent** maps findings to MITRE ATT&CK via RAG.
5. **Correlation Agent** synthesizes a weighted risk score and verdict.
6. **Report Agent** compiles a Markdown report, subsequently converted to PDF.

---

## Agent Orchestration

SecureZen uses a **Sequential Process** via CrewAI:
- **Consistency**: Ensures data flows logically from raw collection to technical analysis to final reporting.
- **Memory**: Common task context allows the "Correlation Analyst" to see every detail discovered by the "VirusTotal Specialist" or "SIEM Historian".

---

**Author**: PRAVEENKUMAR
**Last Updated**: 2026-02-05
