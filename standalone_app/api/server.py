import uvicorn
import os
import sys

# Add app root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
# standalone_app/api/server.py -> standalone_app
app_root = os.path.dirname(current_dir)

if app_root not in sys.path:
    sys.path.insert(0, app_root)

from .base_app import create_base_app, register_shared_routes, db, verify_token, Depends
from fastapi.middleware.wsgi import WSGIMiddleware
import importlib.util

# Create Standalone App
app = create_base_app("SecureZen Standalone Raw Log Intelligence")

# Add LogAI Engine Path to sys.path for internal imports
logai_engine_path = os.path.join(app_root, "engine", "logai")
if logai_engine_path not in sys.path:
    sys.path.insert(0, logai_engine_path)

# Initialize and Mount LogAI Dash App
try:
    from gui.application import app as dash_app
    app.mount("/logai/gui", WSGIMiddleware(dash_app.server))
    print("[INIT] [LogAI] Dash GUI mounted at /logai/gui")
except Exception as e:
    print(f"[WARN] [LogAI] Failed to mount Dash GUI: {e}")

# Register Common Routes (Auth, Copilot)
register_shared_routes(app)

# --- STANDALONE SPECIFIC ROUTES ---

import threading
import glob

# Global analysis job state
_analysis_state = {
    "status": "idle",  # idle | running | complete | error
    "progress": 0,
    "total_files": 0,
    "current_file": "",
    "message": "Ready to analyze",
    "last_run": None,
}

# Datasets directory (mirrors ingest_datasets.py)
_this_dir = os.path.dirname(os.path.abspath(__file__))
_app_root = os.path.dirname(_this_dir)  # standalone_app/
_DATASETS_DIR = os.path.join(_app_root, "engine", "datasets")


def _run_analysis_background(file_paths: list):
    """Background worker: runs analysis_pipeline and updates _analysis_state."""
    global _analysis_state
    from datetime import datetime
    try:
        _analysis_state["status"] = "running"
        _analysis_state["total_files"] = len(file_paths)
        _analysis_state["progress"] = 0
        _analysis_state["message"] = f"Initializing analysis for {len(file_paths)} files..."

        # Import pipeline
        engine_dir = os.path.join(_app_root, "engine")
        if engine_dir not in sys.path:
            sys.path.insert(0, engine_dir)

        # Patch analysis_pipeline to report progress
        from engine.core.analysis_pipeline import run_pipeline, process_single_file
        import logging, xml.etree.ElementTree as ET, re

        # Use the WazuhRuleEngine from analysis_pipeline
        from engine.core.analysis_pipeline import WazuhRuleEngine

        # Lazy imports for LogAI models
        from logai.dataloader.data_loader import FileDataLoader, DataLoaderConfig
        from logai.preprocess.preprocessor import Preprocessor, PreprocessorConfig
        from logai.information_extraction.log_parser import LogParser, LogParserConfig
        from logai.analysis.anomaly_detector import AnomalyDetector, AnomalyDetectionConfig
        from logai.utils import constants as logai_constants

        rules_dir = os.path.join(_app_root, "engine", "core", "rules")
        rule_engine = WazuhRuleEngine(rules_dir)

        from engine.utils.alert_storage import AlertStorage
        storage = AlertStorage()

        parser = LogParser(LogParserConfig(parsing_algorithm="drain"))
        ad_config = AnomalyDetectionConfig(algo_name="one_class_svm")
        detector = AnomalyDetector(ad_config)
        preprocessor = Preprocessor(PreprocessorConfig(custom_delimiters_regex=[r'\s+', r'[,:=]']))
        logger = logging.getLogger("logai.bg_pipeline")

        for i, fp in enumerate(file_paths, 1):
            fname = os.path.basename(fp)
            _analysis_state["current_file"] = fname
            _analysis_state["message"] = f"[{i}/{len(file_paths)}] Analyzing: {fname}"
            _analysis_state["progress"] = int((i - 1) / len(file_paths) * 100)
            try:
                process_single_file(fp, logger, rule_engine, storage, None, parser, detector, preprocessor)
            except Exception as e:
                logger.error(f"Error processing {fname}: {e}")

        _analysis_state["status"] = "complete"
        _analysis_state["progress"] = 100
        _analysis_state["message"] = f"Analysis complete — {len(file_paths)} files processed."
        _analysis_state["last_run"] = datetime.now().isoformat()
    except Exception as e:
        _analysis_state["status"] = "error"
        _analysis_state["message"] = f"Analysis failed: {str(e)}"


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


@app.get("/api/logai/datasets")
async def list_datasets(email: str = Depends(verify_token)):
    """List all log files available in the datasets directory."""
    try:
        extensions = ["*.log", "*.txt"]
        files = []
        for ext in extensions:
            found = glob.glob(os.path.join(_DATASETS_DIR, "**", ext), recursive=True)
            files.extend(found)
        # Return relative paths + sizes for display
        result = []
        for fp in sorted(files):
            rel = os.path.relpath(fp, _DATASETS_DIR)
            size_kb = round(os.path.getsize(fp) / 1024, 1)
            result.append({
                "filename": rel.replace("\\", "/"),
                "path": fp,
                "size_kb": size_kb,
                "basename": os.path.basename(fp),
            })
        return {"datasets_dir": _DATASETS_DIR, "files": result, "count": len(result)}
    except Exception as e:
        return {"error": str(e), "files": [], "count": 0}


@app.post("/api/logai/run-analysis")
async def run_analysis(
    payload: dict = None,
    email: str = Depends(verify_token)
):
    """
    Trigger LogAI analysis on selected datasets in a background thread.
    Body: { "files": ["BGL_2000.log"] }  — if empty, runs ALL datasets.
    """
    global _analysis_state

    if _analysis_state["status"] == "running":
        return {"status": "already_running", "message": "Analysis is already running."}

    # Resolve file paths
    if payload and payload.get("files"):
        selected = payload["files"]
        file_paths = [os.path.join(_DATASETS_DIR, f) for f in selected
                      if os.path.exists(os.path.join(_DATASETS_DIR, f))]
    else:
        # Run ALL datasets
        extensions = ["*.log", "*.txt"]
        file_paths = []
        for ext in extensions:
            file_paths.extend(glob.glob(os.path.join(_DATASETS_DIR, "**", ext), recursive=True))

    if not file_paths:
        return {"status": "error", "message": "No valid dataset files found."}

    # Reset state and launch background thread
    _analysis_state.update({
        "status": "running",
        "progress": 0,
        "total_files": len(file_paths),
        "current_file": "",
        "message": f"Queued {len(file_paths)} files...",
    })

    t = threading.Thread(target=_run_analysis_background, args=(file_paths,), daemon=True)
    t.start()

    return {
        "status": "started",
        "message": f"Analysis started for {len(file_paths)} files.",
        "total_files": len(file_paths),
    }


@app.get("/api/logai/analysis-status")
async def get_analysis_status(email: str = Depends(verify_token)):
    """Poll the current background analysis job status."""
    return {**_analysis_state}

@app.get("/api/dashboard-stats")
async def get_dashboard_stats(email: str = Depends(verify_token)):
    """Get standalone-only stats (LogAI focused) with Hybrid capabilities"""
    from engine.utils.simulator import AlertSimulator
    
    # 1. Fetch Real Data
    real_stats = db.get_dashboard_stats()
    alert_type_dist = db.get_alert_type_stats()
    alerts = db.get_all_alerts(level_min=1, limit=1000)
    
    # 2. Add Hybrid Simulation (Drift + Critical Threats)
    # drift = AlertSimulator.generate_drift_stats(real_stats)
    # sim_alerts = [AlertSimulator.generate_critical_alert() for _ in range(3)]
    
    # In hybrid mode, combine real syslog-derived alerts with simulated criticals
    # alerts = sim_alerts + alerts
    
    return {
        "stats": {
            **real_stats,
            "total_alerts": real_stats.get('total_alerts', 0), 
            "threat_scenarios": real_stats.get('threat_scenarios', 0), 
            "unassigned": real_stats.get('status_counts', {}).get('Open', 0),
            "closed": real_stats.get('status_counts', {}).get('Closed', 0)
        },
        "alert_type_distribution": alert_type_dist,
        "radar_stats": db.get_radar_stats(), 
        "alert_trends": db.get_alert_trends(),
        "alerts": alerts,
        "log_patterns": db.get_log_patterns(limit=15),
        "clusters": db.get_log_clusters(),
        "mode": "standalone"
    }

@app.get("/api/logai/stats")
async def get_logai_stats(email: str = Depends(verify_token)):
    """SecureZen Analysis: pattern counts, cluster distribution, top patterns."""
    import sqlite3 as _sqlite3
    from engine.utils.alert_storage import AlertStorage
    storage = AlertStorage()
    db_path = storage.db_path

    try:
        conn = _sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Pattern count
        cursor.execute("SELECT COUNT(*) FROM log_patterns")
        pattern_count = cursor.fetchone()[0]

        # Cluster count
        cursor.execute("SELECT COUNT(*) FROM log_clusters")
        cluster_count = cursor.fetchone()[0]

        # Anomaly / threat alert count (Rule level >= 5)
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE rule_level >= 5")
        anomaly_count = cursor.fetchone()[0]

        # Total Alerts (Rule level >= 1)
        cursor.execute("SELECT COUNT(*) FROM alerts")
        total_alerts_count = cursor.fetchone()[0]

        # Total log lines analyzed (sum of cluster sizes)
        cursor.execute("SELECT COALESCE(SUM(size), 0) FROM log_clusters")
        total_lines = cursor.fetchone()[0]

        # Top 15 patterns
        cursor.execute('''
            SELECT id, signature, occurrence_count, first_seen, last_seen
            FROM log_patterns
            ORDER BY occurrence_count DESC
            LIMIT 15
        ''')
        top_patterns = [
            {"id": r[0], "pattern": r[1], "count": r[2],
             "first_seen": r[3], "last_seen": r[4]}
            for r in cursor.fetchall()
        ]

        # Cluster distribution
        cursor.execute('''
            SELECT cluster_id, size, representative_log, anomalies_count
            FROM log_clusters
            ORDER BY size DESC
        ''')
        clusters = [
            {"name": r[2].split(":")[0] if r[2] else f"Cluster {r[0]}",
             "value": r[1], "anomalies": r[3]}
            for r in cursor.fetchall()
        ]

        # Severity breakdown - Use better labels for cards
        cursor.execute('''
            SELECT
                CASE
                    WHEN rule_level >= 12 THEN 'Critical'
                    WHEN rule_level >= 10 THEN 'High'
                    WHEN rule_level >= 5  THEN 'Medium'
                    ELSE 'Low'
                END as sev_label,
                COUNT(*)
            FROM alerts
            GROUP BY sev_label
        ''')
        global_severity = dict(cursor.fetchall())

        # Top IPs (Malicious)
        cursor.execute('''
            SELECT ip_address, threat_level, total_alerts, vt_malicious, vt_total
            FROM ip_analysis
            ORDER BY total_alerts DESC
            LIMIT 5
        ''')
        top_ips = [
            {"ip": r[0], "level": r[1], "count": r[2], "vt": f"{r[3]}/{r[4]}"}
            for r in cursor.fetchall()
        ]

        # Primary Attack Path Vectors
        cursor.execute('''
            SELECT tactic, COUNT(*) as c 
            FROM mitre_statistics 
            GROUP BY tactic 
            ORDER BY c DESC 
            LIMIT 4
        ''')
        top_vectors = [r[0] for r in cursor.fetchall()]

        # Alert Trends (Fix timestamp queries inside ThreatDatabase)
        from engine.utils.database import ThreatDatabase
        tdb = ThreatDatabase(db_path=db_path)
        alert_trends = tdb.get_alert_trends()

        # Status Counts (Open, Closed, Remediated)
        dashboard_data = tdb.get_dashboard_stats()
        status_counts = dashboard_data.get('status_counts', {})

        # Recent High Severity Alerts (Filter by rule_level >= 10 for 'Critical/High')
        cursor.execute('''
            SELECT rule_description, severity, timestamp, srcip, agent_name
            FROM alerts
            WHERE rule_level >= 10
            ORDER BY datetime(REPLACE(timestamp, 'Z', '')) DESC
            LIMIT 10
        ''')
        recent_alerts = []
        for r in cursor.fetchall():
             # Map severity label if NULL in DB
             sev = r[1]
             if not sev:
                 sev = 'Critical' # Fallback for high rule levels
             recent_alerts.append({
                 "description": r[0], "severity": sev, "timestamp": r[2], "srcip": r[3], "agent": r[4]
             })

        # Neural AI Insights Logic (Dynamic based on DB contents)
        insights = []
        if anomaly_count > 0:
            insights.append(f"Neural Engine identified {anomaly_count} patterns matching known threat tactics in the current stream.")
        
        if top_ips:
            critical_actors = [ip['ip'] for ip in top_ips if ip.get('level') == 'Critical']
            if critical_actors:
                insights.append(f"Priority Alert: {len(critical_actors)} known threat actors identified (Source IPs: {', '.join(critical_actors[:2])}).")
        
        if top_vectors:
            insights.append(f"AI suggests focusing on '{top_vectors[0]}' vectors which account for the highest volume of detections.")
        
        if not insights and total_alerts_count > 0:
            insights.append(f"System currently monitoring {total_alerts_count} active security events. No critical departures detected since last refresh.")
        elif not insights:
            insights = ["Neural Link Active. Baseline established. Ready for log ingestion."]

        conn.close()
        return {
            "pattern_count": pattern_count,
            "cluster_count": cluster_count,
            "anomaly_count": anomaly_count,
            "total_lines": total_lines,
            "top_patterns": top_patterns,
            "clusters": clusters,
            "severity": global_severity, # Consistency
            "top_ips": top_ips,
            "top_vectors": top_vectors,
            "alert_trends": alert_trends,
            "global_severity": global_severity,
            "status_counts": status_counts,
            "remediated": status_counts.get('Remediated', 0),
            "recent_alerts": recent_alerts,
            "ai_insights": insights,
            "total_alerts": total_alerts_count # For the funnel
        }
    except Exception as e:
        return {"error": str(e), "pattern_count": 0, "cluster_count": 0,
                "anomaly_count": 0, "total_lines": 0,
                "top_patterns": [], "clusters": [], "severity": {}}


@app.get("/api/logai/anomaly-timeline")
async def get_anomaly_timeline(email: str = Depends(verify_token)):
    """SecureZen Analysis: hourly anomaly counts for the timeline chart."""
    import sqlite3 as _sqlite3
    from engine.utils.alert_storage import AlertStorage
    storage = AlertStorage()
    db_path = storage.db_path

    try:
        conn = _sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                strftime('%Y-%m-%dT%H:00:00', REPLACE(timestamp, 'Z', '')) as hour,
                COUNT(*) as count,
                SUM(CASE WHEN rule_level >= 10 THEN 1 ELSE 0 END) as high_count
            FROM alerts
            WHERE rule_level >= 5
            GROUP BY hour
            ORDER BY hour ASC
            LIMIT 48
        ''')
        rows = cursor.fetchall()
        conn.close()

        timeline = [
            {"time": r[0], "anomalies": r[1], "high": r[2]}
            for r in rows
        ]
        return {"timeline": timeline}
    except Exception as e:
        return {"timeline": [], "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
