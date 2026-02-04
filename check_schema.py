import sqlite3
import os

db_path = 'data/wazuh_alerts.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE name='alerts'")
    row = cursor.fetchone()
    if row:
        print(row[0])
    else:
        print("Table 'alerts' not found")
    conn.close()
