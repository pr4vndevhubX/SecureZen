import sqlite3
import os

# The dashboard and AlertStorage use standalone_app/data/syslog_alerts.db
db_path = r"standalone_app/data/syslog_alerts.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM alerts")
        count = cursor.fetchone()[0]
        print(f"Total alerts in database ({db_path}): {count}")
        
        # Also check most recent entries
        cursor.execute("SELECT rule_description, timestamp FROM alerts ORDER BY timestamp DESC LIMIT 5")
        recent = cursor.fetchall()
        print("\nRecent Alerts:")
        for r in recent:
            print(f" - {r[1]}: {r[0]}")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in DB: {tables}")
    
    conn.close()
else:
    print(f"Database not found at {db_path}")
