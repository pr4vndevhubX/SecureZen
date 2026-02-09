import sqlite3

conn = sqlite3.connect('data/wazuh_alerts.db')
cursor = conn.cursor()

# Test different queries
queries = [
    ("All alerts", "SELECT COUNT(*) FROM alerts"),
    ("Last 7 days", "SELECT COUNT(*) FROM alerts WHERE datetime(timestamp) >= datetime('now', '-7 days')"),
    ("Authentication related", "SELECT COUNT(*) FROM alerts WHERE rule_description LIKE '%authentication%'"),
    ("Login related", "SELECT COUNT(*) FROM alerts WHERE rule_description LIKE '%login%'"),
    ("Failed related", "SELECT COUNT(*) FROM alerts WHERE rule_description LIKE '%failed%'"),
]

print("🔍 Database Query Tests:\n")
for name, query in queries:
    cursor.execute(query)
    count = cursor.fetchone()[0]
    print(f"{name}: {count}")

# Show sample descriptions
print("\n📝 Sample Alert Descriptions:")
cursor.execute("SELECT DISTINCT rule_description FROM alerts LIMIT 10")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

conn.close()
