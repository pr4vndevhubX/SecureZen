# Installation Guide
## SecureZen AI-Powered Threat Intelligence System

Complete instructions for setting up the SecureZen platform.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Setup](#local-setup)
3. [Environment Configuration](#environment-configuration)
4. [Service Deployment](#service-deployment)
5. [Wazuh Integration](#wazuh-integration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.11 or higher**: Required for CrewAI and Pydantic V2 support.
- **Git**: To clone the repository.
- **Docker**: Optional, for running the Redis buffer.
- **SQLite3**: For the default persistent database.
- **API Keys**:
  - [VirusTotal](https://www.virustotal.com/gui/join-us) (Free tier available)
  - [AbuseIPDB](https://www.abuseipdb.com/register) (Free tier available)
  - [Groq](https://console.groq.com/keys) (For fast LLM inference)

---

## Local Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd SecureZen
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / MacOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

**Required Variables**:

```bash
# External Intelligence
VIRUSTOTAL_API_KEY=your_vt_key
ABUSEIPDB_API_KEY=your_abuse_key
YETI_API_KEY=your_yeti_key (optional)

# LLM Configuration (Groq recommended)
GROQ_API_KEY=gsk_your_key
OPENAI_MODEL_NAME=llama-3.3-70b-versatile

# Authentication
JWT_SECRET_KEY=generate_a_random_string_for_production
```

---

## Service Deployment

SecureZen is now optimized for **One-Click Product Tier** deployment.

### 🚀 Simplified Execution (Recommended)

Choose your product tier and run the corresponding batch file from the **Project Root**:

| Mode | Command | Description |
| :---: | :--- | :--- |
| **Standalone** | `start_standalone.bat` | Starts the LogAI Backend and Standalone Dashboard. |
| **SIEM Overlay** | `start_overlay.bat` | Starts the SIEM-Integrated Backend and Overlay Dashboard. |

### 🧠 Advanced: Manual Service Start

If you need to start individual components manually:

**1. Shared Background Services**
```bash
# Terminal 1: Start the network listener (Port 5140)
uv run python services/syslog_listener.py

# Terminal 2: Start the LogAI Neural Pipeline (Deep Analysis)
uv run python services/syslog_preprocessor.py
```

**2. Product Backend Servers**
```bash
# Option A: Standalone Server
uv run python core/securezen/syslog/server.py

# Option B: SIEM Overlay Server
uv run python core/securezen/siem/server.py
```

**3. Frontend Dev Server**
```bash
cd frontend
# For Standalone Mode:
npm run dev -- --mode standalone
# For Overlay Mode:
npm run dev -- --mode overlay
```

### 4. Start Frontend Dashboard (Optional Development)
If you are developing the UI independently:
```bash
cd frontend
npm run dev
```

---

## Wazuh Integration

To connect SecureZen to your Wazuh environment:

1.  **Configure Wazuh Webhook**: Add a custom integration in your Wazuh `ossec.conf`:

```xml
<ossec_config>
  <integration>
    <name>custom-webhook</name>
    <hook_url>http://YOUR_SECUREZEN_IP:5000/api/webhook</hook_url>
    <level>5</level>
    <alert_format>json</alert_format>
  </integration>
</ossec_config>
```

2.  **Restart Wazuh Manager**:
```bash
sudo systemctl restart wazuh-manager
```

---

## Troubleshooting

### ModuleNotFoundError: No module named 'httpx'
Ensure you have installed the requirements while the virtual environment is active.
```bash
pip install httpx
```

### CrewAI "Rate Limit" Errors
If using the free tier of Groq or OpenAI, ensure you aren't running massive concurrent investigations. Upgrade your API key if production volume is high.

### DB Lock Errors
If you see SQLite `database is locked`, ensure multiple services aren't trying to write to `threat_intel.db` at the exact same millisecond. Restarting the backend usually resolves this.

---

**Author**: PRAVEENKUMAR
**Last Updated**: 2026-02-11
