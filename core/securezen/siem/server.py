import uvicorn
import os
import sys

# Add project root and parent directory to path
# Add project root and parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../core/securezen/siem
securezen_dir = os.path.dirname(current_dir)             # .../core/securezen
core_dir = os.path.dirname(securezen_dir)                # .../core
project_root = os.path.dirname(core_dir)                 # .../ip-intel-crewai

sys.path.append(project_root)
sys.path.append(securezen_dir)

from base_app import create_base_app, register_shared_routes, db, verify_token, Depends, IOCAnalysisRequest, BackgroundTasks, connector, copilot

# Create Overlay App
app = create_base_app("SecureZen SIEM Overlay AI SOC")

# Register Common Routes (Auth, Copilot)
register_shared_routes(app)

# --- OVERLAY SPECIFIC ROUTES ---

# Import Crew (from parent core/securezen)
try:
    from crew import IPIntelligenceCrew
except ImportError:
    IPIntelligenceCrew = None

@app.get("/api/config")
async def get_config():
    """Get the current configuration for overlay mode"""
    return {
        "mode": "overlay",
        "show_raw_logs": False,
        "show_siem_alerts": True,
        "hybrid": True,
        "plugins": ["wazuh_siem"]
    }

@app.get("/api/dashboard-stats")
async def get_dashboard_stats(email: str = Depends(verify_token)):
    """Get SIEM/Wazuh focused stats with Hybrid Simulation"""
    from utils.simulator import AlertSimulator
    
    # 1. Fetch Real Data
    real_stats = db.get_dashboard_stats()
    alert_type_dist = db.get_alert_type_stats()
    alerts = db.get_all_alerts(level_min=1, limit=1000)
    cve_summary = db.get_cve_stats()
    
    # 2. Add Simulation/Drift logic
    drifted = AlertSimulator.generate_drift_stats(real_stats)
    
    # 3. Handle Critical Alert Simulation
    sim_alerts = [AlertSimulator.generate_critical_alert() for _ in range(3)]
    
    # 4. Merge and Sort by Timestamp (Newest First)
    all_alerts = sim_alerts + alerts
    all_alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    alerts = all_alerts
    
    # Update specific counts to include simulations
    real_stats['severity_counts']['Critical'] = real_stats['severity_counts'].get('Critical', 0) + 3
    
    return {
        "stats": {
            **real_stats,
            "total_alerts": drifted['total_alerts'],
            "threat_scenarios": drifted['threat_scenarios'],
            "unassigned": real_stats.get('status_counts', {}).get('Open', 0),
            "closed": real_stats.get('status_counts', {}).get('Closed', 0)
        },
        "alert_type_distribution": alert_type_dist,
        "radar_stats": db.get_radar_stats(),
        "alert_trends": db.get_alert_trends(),
        "alerts": alerts,
        "cve_summary": cve_summary,
        "mode": "overlay"
    }

@app.post("/api/mitre/search")
async def mitre_search(request: dict, email: str = Depends(verify_token)):
    """Search MITRE ATT&CK framework"""
    message = request.get("message", "")
    # Use copilot to process MITRE search if it has that capability, 
    # otherwise return a helpful message or use a specialized tool.
    # For now, we'll route it through copilot's explanation logic.
    result = copilot.process_message(f"Explain this MITRE concept: {message}")
    content = result.get("content", "No information found.")
    
    return {
        "results": [
            {
                "metadata": {"technique_id": "INFO", "name": "MITRE Insight"},
                "document": content,
                "similarity_score": 0.95
            }
        ]
    }

@app.post("/api/ai/explain-alert")
async def explain_alert(request: dict, email: str = Depends(verify_token)):
    """Use AI to explain a specific alert"""
    message = request.get("message", "")
    result = copilot.process_message(f"Explain this security alert and suggest actions: {message}")
    content = result.get("content", "No explanation available.")
    
    # Simple heuristic for severity/action extraction from AI response
    severity = "Medium"
    if "critical" in content.lower() or "high" in content.lower():
        severity = "High"
    
    return {
        "explanation": content,
        "severity": severity,
        "action": "Investigate immediately" if severity == "High" else "Monitor for further activity"
    }

@app.post("/api/analyze-ioc")
async def analyze_ioc(request: IOCAnalysisRequest, background_tasks: BackgroundTasks, email: str = Depends(verify_token)):
    """Analyze an IP using the Agentic swarm (CrewAI)"""
    if not IPIntelligenceCrew:
        return {"ioc": request.ioc, "status": "error", "analysis": "IPIntelligenceCrew is not available."}
    
    # Check if we already have a recent analysis in DB
    existing = db.get_analysis_by_ioc(request.ioc)
    if existing:
        return existing
        
    crew = IPIntelligenceCrew()
    background_tasks.add_task(crew.run_and_store, request.ioc)
    
    return {
        "ioc": request.ioc,
        "status": "running",
        "analysis": f"Agent swarm initialized for {request.ioc}. Result will be available in 60-90s."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
