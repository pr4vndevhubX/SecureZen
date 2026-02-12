import uvicorn
import os
import sys

# Add parent directory to path to import base_app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_app import create_base_app, register_shared_routes, db, verify_token, Depends

# Create Standalone App
app = create_base_app("SecureZen Standalone Raw Log Intelligence")

# Register Common Routes (Auth, Copilot)
register_shared_routes(app)

# --- STANDALONE SPECIFIC ROUTES ---

@app.get("/api/config")
async def get_config():
    """Get the current configuration for standalone mode"""
    return {
        "mode": "standalone",
        "show_raw_logs": True,
        "show_siem_alerts": False,
        "plugins": ["syslog_analysis"]
    }

@app.get("/api/dashboard-stats")
async def get_dashboard_stats(email: str = Depends(verify_token)):
    """Get standalone-only stats (LogAI focused)"""
    # Base real stats from DB
    stats = db.get_dashboard_stats()
    
    # Force zero out SIEM specific metrics
    stats['total_alerts'] = 0 
    stats['severity_counts'] = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    
    # Dynamic alert type distribution for LogAI
    alert_type_dist = db.get_alert_type_stats()
    
    return {
        "stats": stats,
        "alert_type_distribution": alert_type_dist,
        "radar_stats": db.get_radar_stats(), 
        "alert_trends": db.get_alert_trends()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
