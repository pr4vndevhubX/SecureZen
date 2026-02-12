import os
import sqlite3
from datetime import datetime
import json

# Get project root (one level up from utils)
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(UTILS_DIR)

class ThreatDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            self.db_path = os.path.join(PROJECT_ROOT, 'data/wazuh_alerts.db')
        else:
            self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # IP analysis results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE,
                vt_malicious INTEGER DEFAULT 0,
                vt_total INTEGER DEFAULT 0,
                vt_reputation INTEGER DEFAULT 0,
                abuse_confidence INTEGER DEFAULT 0,
                abuse_total_reports INTEGER DEFAULT 0,
                abuse_country TEXT,
                abuse_isp TEXT,
                yeti_found BOOLEAN DEFAULT 0,
                yeti_tags TEXT,
                threat_level TEXT,
                mitre_techniques TEXT,
                kill_chain_phase TEXT,
                recommendation TEXT,
                first_seen TEXT,
                last_seen TEXT,
                total_alerts INTEGER DEFAULT 1,
                analysis_result TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # MITRE statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mitre_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                technique_id TEXT UNIQUE,
                technique_name TEXT,
                tactic TEXT,
                alert_count INTEGER DEFAULT 0,
                last_detected TEXT,
                severity_critical INTEGER DEFAULT 0,
                severity_high INTEGER DEFAULT 0,
                severity_medium INTEGER DEFAULT 0,
                severity_low INTEGER DEFAULT 0
            )
        ''')
        
        # CVE Intelligence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT UNIQUE,
                description TEXT,
                severity TEXT,
                ai_related BOOLEAN DEFAULT 0,
                published_at TEXT,
                last_seen TEXT,
                references_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ ThreatDatabase pointing to {self.db_path}")

    def get_dashboard_stats(self):
        """Get statistics for dashboard from the webhook alerts table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Alert counts by severity (mapping levels to labels)
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN rule_level >= 12 THEN 'Critical'
                    WHEN rule_level >= 10 THEN 'High'
                    WHEN rule_level >= 5 THEN 'Medium'
                    ELSE 'Low'
                END as sev_label,
                COUNT(*) 
            FROM alerts 
            GROUP BY sev_label
        ''')
        stats['severity_counts'] = dict(cursor.fetchall())
        
        # Total alerts (mapped to Threat Indicators/Detections)
        cursor.execute('SELECT COUNT(*) FROM alerts')
        stats['total_alerts'] = cursor.fetchone()[0]
        
        # Simulated raw events (Logs Analyzed)
        # We simulate a filtering ratio of roughly 1:1200
        stats['total_events'] = stats['total_alerts'] * 1248 + 5342
        
        # Threat level distribution (from analysis table)
        cursor.execute('''
            SELECT threat_level, COUNT(*) 
            FROM ip_analysis 
            GROUP BY threat_level
        ''')
        stats['threat_levels'] = dict(cursor.fetchall())
        
        # Top MITRE techniques
        cursor.execute('''
            SELECT technique_id, technique_name, tactic, alert_count
            FROM mitre_statistics
            ORDER BY alert_count DESC
            LIMIT 10
        ''')
        stats['top_mitre'] = cursor.fetchall()
        
        # Top malicious IPs
        cursor.execute('''
            SELECT ip_address, threat_level, total_alerts, mitre_techniques, abuse_confidence
            FROM ip_analysis
            WHERE threat_level IN ('CRITICAL', 'HIGH')
            ORDER BY total_alerts DESC
            LIMIT 10
        ''')
        stats['top_ips'] = cursor.fetchall()
        
        conn.close()
        return stats

    def get_alert_type_stats(self, limit=5):
        """Get top alert types from the alerts table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rule_description, COUNT(*) as count
            FROM alerts
            GROUP BY rule_description
            ORDER BY count DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        
        # Calculate percentages
        total = sum(row[1] for row in results)
        if total == 0:
            return []
            
        formatted_results = [
            {"name": row[0], "value": round((row[1]/total)*100, 1)}
            for row in results
        ]
        
        conn.close()
        return formatted_results

    def get_radar_stats(self):
        """
        Map Wazuh alerts to Krya-specific categories for the Radar chart.
        Implements a hybrid model: Real Data + Mock Baseline.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        categories = {
            'Dark Web Scan': {
                'keywords': ['dark web', 'leaked', 'credential', 'tor exit'], 
                'mock_base': 15, 'threshold': 100
            },
            'CVE Based Vulnerability': {
                'keywords': ['cve-', 'vulnerability', 'exploit', 'patch', 'outdated'], 
                'mock_base': 45, 'threshold': 120
            },
            'App Misconfig': {
                'keywords': ['configuration', 'policy', 'cis_', 'misconfig', 'default', 'weak'], 
                'mock_base': 35, 'threshold': 100
            },
            'SSL Misconfig': {
                'keywords': ['ssl', 'tls', 'certificate', 'https', 'expired', 'self-signed'], 
                'mock_base': 10, 'threshold': 80
            },
            'Malicious Assets': {
                'keywords': ['malware', 'virus', 'trojan', 'backdoor', 'shell', 'ransom'], 
                'mock_base': 30, 'threshold': 100
            },
            'Internal Posture': {
                'keywords': ['authentication', 'login', 'access control', 'privilege', 'sudo'], 
                'mock_base': 60, 'threshold': 150
            },
            'DNS Masquerade': {
                'keywords': ['dns', 'flood', 'spoof', 'nxdomain', 'tunnel'], 
                'mock_base': 5, 'threshold': 60
            }
        }
        
        radar_data = []
        max_score = 200
        
        for name, config in categories.items():
            # 1. Get Real Count from DB
            keywords = config['keywords']
            query = "SELECT COUNT(*) FROM alerts WHERE " + " OR ".join([f"rule_description LIKE '%{k}%'" for k in keywords])
            cursor.execute(query)
            real_count = cursor.fetchone()[0]
            
            # 2. Hybrid Calculation
            # Total = Real + Mock Base
            total_count = real_count + config['mock_base']
            
            # 3. Calculate Score (Scaling)
            # Formula: (Total / Threshold) * Max_Score
            # We cap it at Max_Score * 0.95 (190) to leave a small gap unless it's overflowing
            score_ratio = min(total_count / config['threshold'], 0.95)
            obtained = int(score_ratio * max_score)
            
            radar_data.append({
                "subject": name,
                "A": obtained,
                "B": max_score,
                "fullMark": max_score,
                # Add metadata for tooltip debugging if needed
                "realCount": real_count,
                "mockBase": config['mock_base']
            })
            
        conn.close()
        return radar_data

    def get_cve_stats(self):
        """Get summary stats for the CVE Intelligence dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total CVEs
        cursor.execute('SELECT COUNT(*) FROM cves')
        stats['total_cves'] = cursor.fetchone()[0]
        
        # AI-Related
        cursor.execute('SELECT COUNT(*) FROM cves WHERE ai_related = 1')
        stats['ai_related_cves'] = cursor.fetchone()[0]
        
        # Critical AI CVEs
        cursor.execute("SELECT COUNT(*) FROM cves WHERE ai_related = 1 AND severity = 'Critical'")
        stats['critical_ai_cves'] = cursor.fetchone()[0]
        
        # High AI CVEs
        cursor.execute("SELECT COUNT(*) FROM cves WHERE ai_related = 1 AND severity = 'High'")
        stats['high_ai_cves'] = cursor.fetchone()[0]
        
        # Recent CVEs for trend chart (simulating daily average)
        stats['daily_average'] = round(stats['total_cves'] / 7 if stats['total_cves'] > 0 else 113.1, 1)
        
        # Severity distribution
        cursor.execute("SELECT severity, COUNT(*) FROM cves GROUP BY severity")
        stats['severity_distribution'] = dict(cursor.fetchall())
        
        conn.close()
        return stats

    def insert_cve(self, cve_data):
        """Insert or update a CVE entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO cves 
                (cve_id, description, severity, ai_related, published_at, last_seen, references_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                cve_data.get('cve_id'),
                cve_data.get('description'),
                cve_data.get('severity'),
                cve_data.get('ai_related', 0),
                cve_data.get('published_at'),
                cve_data.get('last_seen'),
                json.dumps(cve_data.get('references', []))
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting CVE: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_alerts(self, level_min=7):
        """Get all alerts above certain level from webhook database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Mapping AlertStorage columns to ThreatDatabase format for frontend
        cursor.execute('''
            SELECT 
                wazuh_id as alert_id,
                timestamp,
                rule_level,
                rule_id,
                rule_description,
                agent_name,
                agent_ip,
                srcip as src_ip,
                dstip as dst_ip,
                COALESCE(NULLIF(severity, ''), 
                    CASE 
                        WHEN rule_level >= 12 THEN 'Critical'
                        WHEN rule_level >= 10 THEN 'High'
                        WHEN rule_level >= 5 THEN 'Medium'
                        ELSE 'Low'
                    END
                ) as severity,
                rule_description as message
            FROM alerts
            WHERE rule_level >= ?
            ORDER BY timestamp DESC
        ''', (level_min,))
        
        columns = [description[0] for description in cursor.description]
        alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return alerts
    
    def get_recent_analyses(self, limit=10):
        """Get recent IP analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ip_address, threat_level, analysis_result, created_at
            FROM ip_analysis
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "ioc": row[0],
                "status": "completed",
                "analysis": row[2] if not row[2].startswith('{') else "Detailed analysis in DB",
                "timestamp": row[3]
            })
        
        conn.close()
        return results

    def check_ip_in_siem(self, ip_address):
        """Check if IP exists in SIEM alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM alerts
            WHERE srcip = ? OR dstip = ?
        ''', (ip_address, ip_address))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0, count

    def insert_ip_analysis(self, data):
        """Insert or update an IP analysis result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # We use INSERT OR REPLACE to update existing analysis for same IP
            cursor.execute('''
                INSERT OR REPLACE INTO ip_analysis 
                (ip_address, threat_level, vt_malicious, vt_total, abuse_confidence, analysis_result, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('ip_address'),
                data.get('threat_level', 'ANALYZED'),
                data.get('vt_malicious', 0),
                data.get('vt_total', 0),
                data.get('abuse_confidence', 0),
                data.get('full_result', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting IP analysis: {e}")
            return False
        finally:
            conn.close()

    def get_analysis_by_ioc(self, ioc):
        """Get the latest analysis result for a specific IP"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT ip_address, threat_level, analysis_result, created_at, 
                       vt_malicious, vt_total, abuse_confidence
                FROM ip_analysis
                WHERE ip_address = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (ioc,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "ioc": row[0],
                    "status": "done",
                    "analysis": row[2],
                    "timestamp": row[3],
                    "vt_score": f"{row[4]}/{row[5]}",
                    "abuse_score": row[6]
                }
            return None
        except Exception as e:
            print(f"Error fetching analysis for {ioc}: {e}")
            return None
        finally:
            conn.close()

    def get_alert_trends(self, hours=168):
        """Get alert trends over time (default: last 7 days = 168 hours)"""
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get alerts from the last N hours
            cursor.execute('''
                SELECT timestamp, rule_level
                FROM alerts
                WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp ASC
            ''', (hours,))
            
            rows = cursor.fetchall()
            
            if not rows:
                # Return mock data if no alerts found
                now = datetime.now()
                return [
                    {
                        "time": (now - timedelta(hours=168-i*24)).strftime("%m/%d/%Y, %I:%M:%S %p"),
                        "count": 45 + (i * 5)
                    }
                    for i in range(8)
                ]
            
            # Group alerts by time intervals (every 4 hours for better visualization)
            interval_hours = 4
            time_buckets = {}
            
            for timestamp_str, level in rows:
                try:
                    # Parse timestamp
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    
                    # Round down to nearest interval
                    bucket_time = dt.replace(minute=0, second=0, microsecond=0)
                    bucket_time = bucket_time - timedelta(hours=bucket_time.hour % interval_hours)
                    bucket_key = bucket_time.strftime("%m/%d/%Y, %I:%M:%S %p")
                    
                    if bucket_key not in time_buckets:
                        time_buckets[bucket_key] = 0
                    time_buckets[bucket_key] += 1
                except Exception as e:
                    print(f"Error parsing timestamp {timestamp_str}: {e}")
                    continue
            
            # Convert to sorted list
            trend_data = [
                {"time": time_key, "count": count}
                for time_key, count in sorted(time_buckets.items())
            ]
            
            # Ensure we have at least some data points
            if len(trend_data) < 3:
                now = datetime.now()
                # Create wave pattern data instead of linear progression
                wave_counts = [15, 18, 35, 60, 48, 25, 55, 65]
                return [
                    {
                        "time": (now - timedelta(hours=168-i*24)).strftime("%m/%d/%Y, %I:%M:%S %p"),
                        "count": wave_counts[i]
                    }
                    for i in range(8)
                ]
            
            return trend_data
            
        except Exception as e:
            print(f"Error getting alert trends: {e}")
            # Return fallback data with wave pattern
            now = datetime.now()
            wave_counts = [15, 18, 35, 60, 48, 25, 55, 65]
            return [
                {
                    "time": (now - timedelta(hours=168-i*24)).strftime("%m/%d/%Y, %I:%M:%S %p"),
                    "count": wave_counts[i]
                }
                for i in range(8)
            ]
        finally:
            conn.close()