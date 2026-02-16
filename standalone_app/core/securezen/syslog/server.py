import uvicorn
import os
import sys

# Add app root and core/securezen to path
current_dir = os.path.dirname(os.path.abspath(__file__))
# syslog/core/securezen/syslog/server.py -> syslog/core/securezen -> syslog/core -> syslog_root
app_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
securezen_dir = os.path.dirname(current_dir)

if app_root not in sys.path:
    sys.path.insert(0, app_root)
if securezen_dir not in sys.path:
    sys.path.insert(0, securezen_dir)

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
        "show_siem_alerts": True,
        "hybrid": True,
        "plugins": ["syslog_analysis"]
    }

@app.get("/api/dashboard-stats")
async def get_dashboard_stats(email: str = Depends(verify_token)):
    """Get standalone-only stats (LogAI focused) with Hybrid capabilities"""
    from utils.simulator import AlertSimulator
    
    # 1. Fetch Real Data
    real_stats = db.get_dashboard_stats()
    alert_type_dist = db.get_alert_type_stats()
    alerts = db.get_all_alerts(level_min=1, limit=1000)
    
    # 2. Add Hybrid Simulation (Drift + Critical Threats)
    drifted = AlertSimulator.generate_drift_stats(real_stats)
    sim_alerts = [AlertSimulator.generate_critical_alert() for _ in range(3)]
    
    # In hybrid mode, combine real syslog-derived alerts with simulated criticals
    alerts = sim_alerts + alerts
    
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
        "mode": "standalone"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
