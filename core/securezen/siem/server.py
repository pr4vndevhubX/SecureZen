import uvicorn
import os
import sys

# Add parent directory to path to import base_app and crew
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        "plugins": ["wazuh_siem"]
    }

@app.get("/api/dashboard-stats")
async def get_dashboard_stats(email: str = Depends(verify_token)):
    """Get SIEM/Wazuh focused stats"""
    stats = db.get_dashboard_stats()
    alert_type_dist = db.get_alert_type_stats()
    
    return {
        "stats": stats,
        "alert_type_distribution": alert_type_dist,
        "radar_stats": db.get_radar_stats(),
        "alert_trends": db.get_alert_trends()
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
