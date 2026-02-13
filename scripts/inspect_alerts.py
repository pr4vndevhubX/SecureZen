import sqlite3
import json

def inspect_alerts():
    conn = sqlite3.connect('data/wazuh_alerts.db')
    cursor = conn.cursor()
    
    print("--- Checking Alerts Table ---")
    cursor.execute("SELECT count(*) FROM alerts")
    count = cursor.fetchone()[0]
    print(f"Total Alerts in DB: {count}")
    
    cursor.execute("SELECT full_alert FROM alerts LIMIT 1")
    row = cursor.fetchone()
    if row:
        alert = json.loads(row[0])
        print("\nSample Alert JSON Keys:", list(alert.keys()))
        print("Sample MITRE Data:", alert.get('rule', {}).get('mitre', {}))
    
    print("\n--- Checking for Reconnaissance ---")
    # Check if 'Reconnaissance' exists in any common field
    cursor.execute("SELECT count(*) FROM alerts WHERE full_alert LIKE '%Reconnaissance%'")
    recon_count = cursor.fetchone()[0]
    print(f"Alerts containing 'Reconnaissance': {recon_count}")

    print("\n--- Checking Rule Level Distribution ---")
    cursor.execute("SELECT rule_level, COUNT(*) FROM alerts GROUP BY rule_level ORDER BY rule_level DESC")
    levels = cursor.fetchall()
    for level, count in levels:
        print(f"Level {level}: {count} alerts")

    conn.close()

if __name__ == "__main__":
    inspect_alerts()
