import sqlite3
import os

db_path = 'data/wazuh_alerts.db'

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check count
        cursor.execute("SELECT COUNT(*) FROM alerts")
        count = cursor.fetchone()[0]
        print(f"📊 Total Alerts: {count}")
        
        if count > 0:
            # Check date range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM alerts")
            min_ts, max_ts = cursor.fetchone()
            print(f"🕒 Time Range: {min_ts} to {max_ts}")
            
            # Check recent (last 24h)
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE datetime(timestamp) >= datetime('now', '-24 hours')")
            recent = cursor.fetchone()[0]
            print(f"📅 Last 24h: {recent}")
            
            # Show sample
            cursor.execute("SELECT timestamp, rule_description FROM alerts LIMIT 3")
            print("\n📝 Sample:")
            for row in cursor.fetchall():
                print(row)
        
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")
