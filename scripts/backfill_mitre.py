
import os
import sys
import sqlite3
import json
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.alert_storage import AlertStorage

class MitreBackfiller:
    def __init__(self):
        self.storage = AlertStorage()
        self.db_path = self.storage.db_path
        
    def run(self):
        print(f"[START] Starting MITRE Backfill on {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Clear existing stats to avoid double counting (optional, but safer for backfill)
        print("? Clearing existing MITRE stats...")
        cursor.execute("DELETE FROM mitre_statistics")
        conn.commit()
        
        # 2. Get all alerts
        print("? Fetching all alerts...")
        cursor.execute("SELECT id, full_alert FROM alerts")
        rows = cursor.fetchall()
        total = len(rows)
        print(f"[OK] Found {total} alerts to process")
        
        processed = 0
        mitre_hits = 0
        
        start_time = time.time()
        
        for row in rows:
            alert_id = row[0]
            try:
                full_alert = json.loads(row[1])
                
                # Re-use the logic from AlertStorage (we have to access internal method or duplicate logic)
                # Since I'm using the class instance, I can't easily call valid instance method on self
                # So I'll just use the same logic here
                
                rule = full_alert.get('rule', {})
                mitre = rule.get('mitre', {})
                
                # Extract ID and Tactic
                mitre_id = mitre.get('id', [])
                tactic = mitre.get('tactic', [])
                
                if mitre_id:
                    # Handle list or string
                    if isinstance(mitre_id, list):
                        mitre_id = mitre_id[0] if mitre_id else None
                    if isinstance(tactic, list):
                        tactic = tactic[0] if tactic else None
                    
                    if mitre_id:
                        self.update_stats(cursor, mitre_id, tactic, rule.get('level', 0))
                        mitre_hits += 1
                        
            except Exception as e:
                print(f"[ERR] Error processing alert {alert_id}: {e}")
                
            processed += 1
            if processed % 1000 == 0:
                print(f"? Processed {processed}/{total} ({round(processed/total*100, 1)}%) - Found {mitre_hits} MITRE events")
                
        conn.commit()
        conn.close()
        
        duration = time.time() - start_time
        print(f"\n[OK] Backfill Complete!")
        print(f"[STATS] Processed: {total}")
        print(f"? MITRE Events: {mitre_hits}")
        print(f"?? Time: {round(duration, 2)}s")

    def update_stats(self, cursor, mitre_id, tactic, level):
        level = int(level)
        is_critical = 1 if level >= 12 else 0
        is_high = 1 if level >= 10 and level < 12 else 0
        is_medium = 1 if level >= 5 and level < 10 else 0
        is_low = 1 if level < 5 else 0

        # Upsert into mitre_statistics
        cursor.execute("SELECT id FROM mitre_statistics WHERE technique_id = ?", (mitre_id,))
        row = cursor.fetchone()
        
        if row:
            # Update
            cursor.execute("""
                UPDATE mitre_statistics 
                SET alert_count = alert_count + 1,
                    last_detected = ?,
                    severity_critical = severity_critical + ?,
                    severity_high = severity_high + ?,
                    severity_medium = severity_medium + ?,
                    severity_low = severity_low + ?
                WHERE id = ?
            """, (
                self.get_utc_now(),
                is_critical, is_high, is_medium, is_low,
                row[0]
            ))
        else:
            # Insert
            cursor.execute("""
                INSERT INTO mitre_statistics (
                    technique_id, technique_name, tactic, alert_count, last_detected,
                    severity_critical, severity_high, severity_medium, severity_low
                ) VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?)
            """, (
                mitre_id, 
                f"Technique {mitre_id}", 
                tactic or 'Unknown', 
                self.get_utc_now(),
                is_critical, is_high, is_medium, is_low
            ))

    def get_utc_now(self):
        from datetime import datetime
        return datetime.utcnow().isoformat()

if __name__ == "__main__":
    backfiller = MitreBackfiller()
    backfiller.run()
