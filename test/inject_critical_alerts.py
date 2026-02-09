import sqlite3
import random
from datetime import datetime, timedelta

def inject_alerts():
    conn = sqlite3.connect('data/wazuh_alerts.db')
    cursor = conn.cursor()
    
    # Get current time
    now = datetime.now()
    
    # Scenarios for critical alerts
    scenarios = [
        "SQL Injection Attempt", 
        "Brute Force SSH Attack", 
        "Malware C2 Beacon Detected", 
        "Privilege Escalation on Server-05", 
        "Shadow IT Asset Detected", 
        "Data Exfiltration to Anonymous IP",
        "Ransomware Encryption Pattern Observed",
        "Multiple Failed Logins followed by Success",
        "Unauthorized access to sensitive database",
        "Suspicious PowerShell execution with encoded command"
    ]
    
    critical_count = 22
    injected = 0
    
    print(f"Injecting {critical_count} critical alerts with timestamp around {now.isoformat()}...")
    
    for i in range(critical_count):
        # Slightly jitter the timestamp within the last hour
        ts = now - timedelta(minutes=random.randint(1, 59))
        ts_str = ts.strftime('%Y-%m-%dT%H:%M:%S.000+0530')
        
        scenario = random.choice(scenarios)
        src_ip = f"{random.choice(['45', '185', '193', '103', '91', '212', '146'])}.{random.randint(50,250)}.{random.randint(10,240)}.{random.randint(1,254)}"
        
        cursor.execute('''
            INSERT INTO alerts (
                timestamp, rule_level, rule_description, agent_name, agent_ip, 
                srcip, severity, full_alert, received_at, processed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ts_str, 
            random.randint(10, 15), # rule_level 10-15 is critical
            f"SECUREZEN: {scenario}", 
            random.choice(["Wazuh-Agent-Linux", "Wazuh-Agent-Win", "Firewall-Core"]),
            f"10.0.0.{random.randint(10,100)}",
            src_ip,
            'Critical',
            f"Manual injection for demo alignment: {scenario}",
            ts_str,
            1
        ))
        injected += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully injected {injected} alerts.")

if __name__ == "__main__":
    inject_alerts()
