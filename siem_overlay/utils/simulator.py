import random
import uuid
from datetime import datetime, timedelta

class AlertSimulator:
    @staticmethod
    def generate_critical_alert():
        """Generates a realistic Critical severity alert based on common attack patterns"""
        templates = [
            {
                "description": "Exploit: EternalBlue (MS17-010) detected in network traffic",
                "id": "100101",
                "mitre_id": "T1210",
                "mitre_tactic": "Lateral Movement",
                "message": "Signature match for EternalBlue exploit attempting to reach Server-01"
            },
            {
                "description": "Ransomware activity: Mass file renaming and encryption pattern",
                "id": "100202",
                "mitre_id": "T1486",
                "mitre_tactic": "Impact",
                "message": "Process 'unknown.exe' performing rapid I/O operations on user documents"
            },
            {
                "description": "Exfiltration: Large volume of data transfer to unusual overseas IP",
                "id": "100303",
                "mitre_id": "T1048",
                "mitre_tactic": "Exfiltration",
                "message": "Data transfer of 4.2GB detected to 8.21.4.15 (China)"
            },
            {
                "description": "Persistence: New unauthorized user added to Domain Admins group",
                "id": "100404",
                "mitre_id": "T1098",
                "mitre_tactic": "Persistence",
                "message": "User 'guest_svc' promoted to Domain Admin by 'SYSTEM'"
            }
        ]
        
        template = random.choice(templates)
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"
        
        return {
            "alert_id": f"SIM-{uuid.uuid4().hex[:8]}",
            "timestamp": ts,
            "rule_level": 12,
            "rule_id": template["id"],
            "rule_description": template["description"],
            "agent_name": random.choice(["Server-01", "Database-01", "Domain-Controller"]),
            "agent_ip": "192.168.1.50",
            "src_ip": f"103.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "dst_ip": "192.168.1.50",
            "severity": "Critical",
            "message": template["message"],
            "rule_mitre_id": template["mitre_id"],
            "rule_mitre_tactic": template["mitre_tactic"],
            "is_simulated": True
        }

    @staticmethod
    def generate_drift_stats(real_stats):
        """Adds a randomized drift to real stats to make the UI look alive"""
        drift = random.randint(-5, 15)
        new_total = real_stats.get('total_alerts', 0) + drift
        
        # Simulate much larger raw event count
        return {
            "total_alerts": new_total,
            "total_events": new_total * 1248 + random.randint(100, 1000),
            "threat_scenarios": new_total + random.randint(5, 20)
        }
