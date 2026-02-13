"""
Wazuh Alert Receiver - Webhook Service
Receives alerts from Wazuh manager and stores in SQLite database
Provides search endpoint for CrewAI integration
"""

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os
import traceback
from datetime import datetime, timedelta
from typing import Optional

# Add project root to path (3 levels up from here: features/wazuh_siem/webhook.py -> features/wazuh_siem -> features -> root)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from utils.alert_storage import AlertStorage

app = FastAPI(title="Wazuh Alert Receiver", version="1.0.0")
alert_storage = AlertStorage()

stats = {'total_received': 0, 'stored': 0, 'filtered': 0}

API_KEY = "Apkl3@Jfyg2"

import re
import httpx

async def trigger_automated_analysis(alert: dict):
    """
    Extract IOCs and trigger CrewAI analysis for suspicious alerts (> Level 7)
    Only triggers if the alert description/log appears genuinely suspicious
    """
    try:
        # 1. Suspiciousness Check
        description = alert.get("rule", {}).get("description", "").lower()
        full_log = alert.get("full_log", "").lower()
        content = f"{description} {full_log}"
        
        # Keywords that indicate a high-priority threat requiring deep analysis
        suspicious_keywords = [
            "malware", "suspicious", "attack", "exploit", "ransomware", 
            "vulnerability", "unauthorized", "brute force", "c2", "command and control",
            "exfiltration", "persistence", "privilege escalation", "lateral movement",
            "rce", "sqli", "xss", "trojan", "worm", "backdoor", "rootkit"
        ]
        
        is_suspicious = any(kw in content for kw in suspicious_keywords)
        
        if not is_suspicious:
            print(f"ℹ️ Alert level {alert.get('rule',{}).get('level')} received, but no highly suspicious patterns detected. Skipping automated analysis.")
            return

        # 2. Extract potential IOCs
        # Regex for IPv4
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, content)
        
        # Filter suspicious IPs (exclude private/broadcast)
        suspicious_ips = []
        for ip in ips:
            if not (ip.startswith("127.") or ip.startswith("192.168.") or 
                   ip.startswith("10.") or ip.startswith("172.16.") or 
                   ip == "0.0.0.0" or ip == "255.255.255.255"):
                suspicious_ips.append(ip)
        
        if not suspicious_ips:
            # Fallback to srcip if available
            data = alert.get("data", {})
            srcip = data.get("srcip") or data.get("src_ip")
            if srcip and srcip not in ["127.0.0.1", "0.0.0.0"]:
                is_private = (srcip.startswith("127.") or srcip.startswith("192.168.") or 
                             srcip.startswith("10.") or srcip.startswith("172.16."))
                if not is_private:
                    suspicious_ips.append(srcip)

        # 3. Trigger analysis for unique suspicious IPs
        unique_ips = list(set(suspicious_ips))
        if unique_ips:
            print(f"🧠 Automated Analysis Triggered for suspicious alert: {unique_ips}")
            async with httpx.AsyncClient() as client:
                for target_ioc in unique_ips:
                    try:
                        await client.post(
                            "http://localhost:5000/api/analyze-ioc",
                            json={"ioc": target_ioc},
                            timeout=60.0
                        )
                    except Exception as e:
                        print(f"⚠️ Failed to trigger analysis for {target_ioc}: {e}")
        else:
            print(f"ℹ️ No external IOCs found for suspicious level {alert.get('rule',{}).get('level')} alert")

    except Exception as e:
        print(f"❌ Error in automated analysis trigger: {e}")

@app.post("/loghook")
async def loghook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for Wazuh alerts
    Receives both single alerts and batch alerts
    """
    try:
        # 1️⃣ Authenticate Wazuh
        if request.headers.get("X-API-Key") != API_KEY:
            print("❌ Unauthorized request")
            return JSONResponse(
                status_code=401,
                content={"status": "unauthorized"}
            )

        payload = await request.json()

        # =========================
        # 🔁 HANDLE BATCH ALERTS
        # =========================
        if isinstance(payload, list):
            stored_count = 0

            for alert in payload:
                try:
                    # Safe extraction of rule level
                    rule_level = alert.get("rule", {}).get("level", 0)
                    
                    # Handle None or non-numeric values
                    if rule_level is None:
                        rule_level = 0
                    else:
                        rule_level = int(rule_level)

                    if rule_level < 5:
                        stats['filtered'] += 1
                        continue

                    alert_storage.store_alert(alert)
                    stored_count += 1
                    
                    # 🧘 Automated analysis for high level alerts
                    if rule_level > 7:
                        background_tasks.add_task(trigger_automated_analysis, alert)

                except Exception as alert_error:
                    print(f"⚠️ Error processing individual alert: {alert_error}")
                    print(f"Alert data: {alert}")
                    continue

            stats['total_received'] += len(payload)
            stats['stored'] += stored_count

            print(f"📦 Batch received | Total: {len(payload)} | Stored: {stored_count}")

            return {
                "status": "stored",
                "batch_size": len(payload),
                "stored": stored_count
            }

        # =========================
        # 🔔 HANDLE SINGLE ALERT
        # =========================
        alert = payload.get("alert", payload)
        
        # Safe extraction of rule level
        rule_level = alert.get("rule", {}).get("level", 0)
        
        # Handle None or non-numeric values
        if rule_level is None:
            rule_level = 0
        else:
            rule_level = int(rule_level)

        print(f"📩 Received alert | Level: {rule_level}")

        stats['total_received'] += 1

        if rule_level < 5:
            stats['filtered'] += 1
            return {"status": "filtered"}

        alert_id = alert_storage.store_alert(alert)
        stats['stored'] += 1

        # 🧠 Trigger automated analysis for high level alerts
        if rule_level > 7:
            background_tasks.add_task(trigger_automated_analysis, alert)

        print(f"✅ Stored alert ID: {alert_id}")

        return {
            "status": "stored",
            "alert_id": alert_id,
            "level": rule_level
        }

    except Exception as e:
        # Enhanced error logging
        error_msg = str(e) if str(e) else repr(e)
        error_trace = traceback.format_exc()
        
        print(f"❌ Error: {error_msg}")
        print(f"📋 Full traceback:\n{error_trace}")
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": error_msg,
                "type": type(e).__name__
            }
        )


@app.get("/alerts/search")
async def search_alerts(
    ip: str,
    days: int = 30,
    min_level: int = 5
):
    """
    Search alerts for specific IP address
    Used by CrewAI WazuhSIEMTool
    
    Args:
        ip: IP address to search for
        days: Number of days to look back
        min_level: Minimum alert severity level
        
    Returns:
        JSON with matching alerts and metadata
    """
    try:
        print(f"🔍 Search request: IP={ip}, days={days}, min_level={min_level}")
        
        # Query database using fast IP search
        matching_alerts = alert_storage.search_alerts_by_ip(ip, days=days)
        
        # Filter by minimum level
        filtered_alerts = []
        for alert in matching_alerts:
            rule_level = alert.get('rule_level', 0)
            if rule_level >= min_level:
                # Format alert for crew consumption
                formatted_alert = {
                    'id': alert.get('id'),
                    'timestamp': alert.get('timestamp'),
                    'rule_id': alert.get('rule_id'),
                    'rule_level': rule_level,
                    'rule_description': alert.get('rule_description'),
                    'agent_name': alert.get('agent_name'),
                    'srcip': alert.get('srcip'),
                    'dstip': alert.get('dstip'),
                    'classification': alert.get('classification'),
                    'severity': alert.get('severity')
                }
                filtered_alerts.append(formatted_alert)
        
        print(f"✅ Found {len(filtered_alerts)} alerts matching criteria")
        
        return {
            "alerts": filtered_alerts,
            "total_count": len(filtered_alerts),
            "query": {
                "ip": ip,
                "days": days,
                "min_level": min_level
            },
            "search_method": "indexed_ip_columns"
        }
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "alerts": [],
                "total_count": 0
            }
        )


@app.get("/stats")
async def get_stats():
    """
    Get webhook and database statistics
    """
    db_stats = alert_storage.get_stats()
    
    return {
        "webhook_stats": stats,
        "database_stats": db_stats,
        "uptime": "N/A"  # Could add uptime tracking
    }


@app.get("/alerts/recent")
async def get_recent_alerts(limit: int = 10):
    """
    Get recent unprocessed alerts
    """
    alerts = alert_storage.get_unprocessed_alerts(limit)
    return {
        "count": len(alerts),
        "alerts": alerts
    }


@app.get("/alerts/unique-ips")
async def get_unique_ips(days: int = 7, limit: int = 100):
    """
    Get unique source/destination IPs from recent alerts
    Useful for threat hunting
    """
    try:
        ip_data = alert_storage.get_unique_ips(days=days, limit=limit)
        return ip_data
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    db_stats = alert_storage.get_stats()
    
    return {
        "status": "healthy",
        "service": "wazuh-webhook",
        "version": "1.0.0",
        "alerts_stored": stats['stored'],
        "database_health": {
            "total_alerts": db_stats.get('total_alerts', 0),
            "unprocessed": db_stats.get('unprocessed', 0)
        }
    }


@app.get("/")
async def root():
    """
    Root endpoint - service info
    """
    return {
        "service": "Wazuh Alert Receiver",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "webhook": "/loghook (POST)",
            "search": "/alerts/search?ip={ip}&days={days}",
            "stats": "/stats",
            "recent": "/alerts/recent?limit={limit}",
            "unique_ips": "/alerts/unique-ips?days={days}",
            "health": "/health"
        },
        "documentation": "/docs"
    }


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Wazuh Alert Receiver")
    print("=" * 70)
    print(f"📡 Webhook endpoint: http://0.0.0.0:3030/loghook")
    print(f"🔍 Search endpoint: http://0.0.0.0:3030/alerts/search")
    print(f"📊 Stats endpoint: http://0.0.0.0:3030/stats")
    print(f"💚 Health check: http://0.0.0.0:3030/health")
    print(f"📚 API docs: http://0.0.0.0:3030/docs")
    print("=" * 70)
    print(f"🔑 API Key required: {API_KEY[:10]}...")
    print("=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=3030)
