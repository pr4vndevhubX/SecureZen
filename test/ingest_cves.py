import sys
import os

# Add the project root to path so we can import utils
sys.path.append(os.getcwd())

from utils.database import ThreatDatabase
from datetime import datetime, timedelta

def ingest_mock_cves():
    db = ThreatDatabase()
    
    # Mock CVE data based on the requirements for "AI-Related" and "Critical"
    mock_cves = [
        {
            "cve_id": "CVE-2024-0001",
            "description": "Critical vulnerability in AI model inference engine allowing arbitrary code execution.",
            "severity": "Critical",
            "ai_related": 1,
            "published_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "last_seen": datetime.now().isoformat(),
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-0001"]
        },
        {
            "cve_id": "CVE-2024-0002",
            "description": "High risk prompt injection vulnerability in LLM gateway.",
            "severity": "High",
            "ai_related": 1,
            "published_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "last_seen": datetime.now().isoformat(),
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-0002"]
        },
        {
            "cve_id": "CVE-2024-0003",
            "description": "Medium severity data leakage in AI training pipeline.",
            "severity": "Medium",
            "ai_related": 1,
            "published_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "last_seen": datetime.now().isoformat(),
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-0003"]
        },
        {
            "cve_id": "CVE-2023-5216",
            "description": "Buffer overflow in common web server component.",
            "severity": "Critical",
            "ai_related": 0,
            "published_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "last_seen": datetime.now().isoformat(),
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-5216"]
        },
        {
            "cve_id": "CVE-2023-9876",
            "description": "Insecure direct object reference in user management portal.",
            "severity": "Medium",
            "ai_related": 0,
            "published_at": (datetime.now() - timedelta(days=12)).isoformat(),
            "last_seen": datetime.now().isoformat(),
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-9876"]
        }
    ]
    
    count = 0
    for cve in mock_cves:
        if db.insert_cve(cve):
            count += 1
            
    print(f"[OK] Ingested {count} mock CVE entries.")

if __name__ == "__main__":
    ingest_mock_cves()
