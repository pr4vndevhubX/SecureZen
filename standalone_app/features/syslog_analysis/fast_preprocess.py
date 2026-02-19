"""
SecureZen Fast Pre-Processor
============================
Lightweight, dependency-free log analysis engine.
Scans all dataset files, extracts patterns, detects anomalies,
and stores results in the SecureZen database — in minutes.

No heavy ML libraries required. Uses regex + keyword matching.
"""

import os
import sys
import re
import glob
import sqlite3
import json
from datetime import datetime
from collections import defaultdict

# ── Path setup ────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # ip-intel-crewai/standalone_app
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

DATASETS_DIR = os.path.join(os.path.dirname(APP_ROOT), "datasets")
DB_PATH = os.path.join(APP_ROOT, "data", "syslog_alerts.db")

# ── Threat keyword patterns (for anomaly detection) ───────────────────────────
THREAT_KEYWORDS = [
    # Authentication attacks
    r'\bfailed\s+(?:login|password|authentication)\b',
    r'\binvalid\s+(?:user|password|credential)\b',
    r'\bbrute.?force\b',
    r'\bssh.*(?:failed|refused|denied)\b',
    r'\bpam_unix.*authentication failure\b',
    # Network threats
    r'\bport.?scan\b',
    r'\bsyn.?flood\b',
    r'\bddos\b',
    r'\bfirewall.*(?:denied|blocked|drop)\b',
    r'\baccess.?denied\b',
    # Malware / execution
    r'\bmalware\b',
    r'\btrojan\b',
    r'\bransomware\b',
    r'\bshellcode\b',
    r'\bexploit\b',
    r'\bpayload\b',
    r'\breverse.?shell\b',
    # Privilege escalation
    r'\bsudo.*(?:failed|denied|not allowed)\b',
    r'\bprivilege.?escalation\b',
    r'\broot.?access\b',
    r'\bunauthorized\b',
    # Suspicious processes
    r'\b(?:cmd|powershell|bash|sh)\s+-[ec]\b',
    r'\bbase64.*decode\b',
    r'\bwget\s+http\b',
    r'\bcurl\s+http\b',
    # Windows events
    r'\bevent.?id.*(?:4625|4648|4672|4698|4720|4732|4756)\b',
    r'\bsecurity.*audit.*failure\b',
    # Cisco ASA / Firewall
    r'\b%ASA-[3-7]-\d+\b',
    r'\bdenied\s+(?:inbound|outbound)\b',
    r'\bteardown\s+(?:tcp|udp)\b',
]

COMPILED_THREATS = [re.compile(p, re.IGNORECASE) for p in THREAT_KEYWORDS]

# ── Log template tokenizer ────────────────────────────────────────────────────
IP_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
NUM_RE = re.compile(r'\b\d+\b')
HEX_RE = re.compile(r'\b[0-9a-fA-F]{8,}\b')
TIMESTAMP_RE = re.compile(
    r'\b(?:\d{4}[-/]\d{2}[-/]\d{2}|\w{3}\s+\d{1,2})\s+\d{2}:\d{2}:\d{2}\b'
)
PATH_RE = re.compile(r'(?:/[\w./\-_]+|[A-Za-z]:\\[\w\\./\-_ ]+)')
USER_RE = re.compile(r'\buser[=:\s]+\S+', re.IGNORECASE)


def extract_template(line: str) -> str:
    """Replace variable parts with placeholders to create a log template."""
    t = TIMESTAMP_RE.sub('<TIME>', line)
    t = IP_RE.sub('<IP>', t)
    t = PATH_RE.sub('<PATH>', t)
    t = USER_RE.sub('user=<USER>', t)
    t = HEX_RE.sub('<HEX>', t)
    t = NUM_RE.sub('<NUM>', t)
    # Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    # Truncate very long templates
    return t[:200] if len(t) > 200 else t


def is_threat(line: str) -> tuple:
    """Check if a log line matches any threat pattern. Returns (bool, description)."""
    for i, pattern in enumerate(COMPILED_THREATS):
        if pattern.search(line):
            return True, THREAT_KEYWORDS[i]
    return False, None


def classify_log_source(filepath: str) -> str:
    """Classify log source from filename/path."""
    path_lower = filepath.lower()
    if 'cisco' in path_lower or 'asa' in path_lower:
        return 'Cisco ASA'
    elif 'windows' in path_lower or 'win' in path_lower or 'lolbas' in path_lower:
        return 'Windows'
    elif 'linux' in path_lower or 'sysmon' in path_lower:
        return 'Linux/Sysmon'
    elif 'ssh' in path_lower:
        return 'SSH'
    elif 'apache' in path_lower or 'nginx' in path_lower or 'web' in path_lower:
        return 'Web Server'
    elif 'firewall' in path_lower or 'fw' in path_lower:
        return 'Firewall'
    elif 'dns' in path_lower:
        return 'DNS'
    elif 'auth' in path_lower:
        return 'Auth'
    else:
        return 'Generic Syslog'


def ensure_tables(conn):
    """Ensure all required tables exist."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signature TEXT UNIQUE,
            event_id TEXT,
            occurrence_count INTEGER DEFAULT 1,
            first_seen TEXT,
            last_seen TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_clusters (
            cluster_id INTEGER PRIMARY KEY,
            size INTEGER DEFAULT 0,
            representative_log TEXT,
            anomalies_count INTEGER DEFAULT 0,
            status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wazuh_id TEXT,
            timestamp TEXT NOT NULL,
            rule_id TEXT,
            rule_level INTEGER,
            rule_description TEXT,
            agent_name TEXT,
            agent_ip TEXT,
            srcip TEXT,
            dstip TEXT,
            full_alert TEXT NOT NULL,
            received_at TEXT NOT NULL,
            processed INTEGER DEFAULT 0,
            processed_at TEXT,
            classification TEXT,
            severity TEXT,
            status TEXT DEFAULT 'Open',
            UNIQUE(wazuh_id, timestamp)
        )
    ''')
    conn.commit()


def process_file(filepath: str, conn, pattern_counts: dict, cluster_data: dict):
    """Process a single log file. Updates pattern_counts and cluster_data in-place."""
    source = classify_log_source(filepath)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    threat_count = 0
    line_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                line_count += 1
                
                # Extract template
                template = extract_template(line)
                if not template:
                    continue
                
                # Update pattern counts
                pattern_counts[template] = pattern_counts.get(template, 0) + 1
                
                # Check for threats
                is_t, threat_desc = is_threat(line)
                if is_t:
                    threat_count += 1
                    # Extract IPs
                    ips = IP_RE.findall(line)
                    srcip = ips[0] if len(ips) > 0 else None
                    dstip = ips[1] if len(ips) > 1 else None
                    
                    # Determine severity
                    line_lower = line.lower()
                    if any(k in line_lower for k in ['critical', 'emergency', 'ransomware', 'exploit']):
                        level, severity = 12, 'Critical'
                    elif any(k in line_lower for k in ['failed', 'denied', 'brute', 'malware', 'trojan']):
                        level, severity = 10, 'High'
                    elif any(k in line_lower for k in ['warning', 'suspicious', 'scan']):
                        level, severity = 7, 'Medium'
                    else:
                        level, severity = 5, 'Medium'
                    
                    alert_id = f"SZ_{abs(hash(line + filepath)) % 9999999}"
                    alert = {
                        "id": alert_id,
                        "timestamp": now,
                        "rule": {"id": "SZ001", "level": level, "description": f"SecureZen: {template[:100]}"},
                        "agent": {"name": source, "ip": "0.0.0.0"},
                        "data": {"logline": line[:500], "dataset": os.path.basename(filepath)},
                        "full_log": line[:500]
                    }
                    
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO alerts
                            (wazuh_id, timestamp, rule_id, rule_level, rule_description,
                             agent_name, agent_ip, srcip, dstip, full_alert, received_at, severity, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')
                        ''', (
                            alert_id, now, 'SZ001', level,
                            f"SecureZen: {template[:100]}",
                            source, '0.0.0.0', srcip, dstip,
                            json.dumps(alert), now, severity
                        ))
                    except Exception:
                        pass
        
        # Update cluster data per source type
        if source not in cluster_data:
            cluster_data[source] = {'size': 0, 'anomalies': 0, 'sample': ''}
        cluster_data[source]['size'] += line_count
        cluster_data[source]['anomalies'] += threat_count
        if not cluster_data[source]['sample'] and line_count > 0:
            cluster_data[source]['sample'] = os.path.basename(filepath)
        
        conn.commit()
        return line_count, threat_count
        
    except Exception as e:
        return 0, 0


def flush_patterns(conn, pattern_counts: dict, batch_size: int = 500):
    """Flush accumulated pattern counts to the database."""
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    # Sort by count descending, take top patterns
    sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
    
    for template, count in sorted_patterns[:batch_size]:
        try:
            cursor.execute('''
                INSERT INTO log_patterns (signature, occurrence_count, first_seen, last_seen)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(signature) DO UPDATE SET
                    occurrence_count = occurrence_count + excluded.occurrence_count,
                    last_seen = excluded.last_seen
            ''', (template, count, now, now))
        except Exception:
            pass
    
    conn.commit()
    pattern_counts.clear()


def flush_clusters(conn, cluster_data: dict):
    """Write cluster data to the database."""
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    for i, (source, data) in enumerate(cluster_data.items()):
        cluster_id = abs(hash(source)) % 100000
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO log_clusters
                (cluster_id, size, representative_log, anomalies_count, status)
                VALUES (?, ?, ?, ?, 'Active')
            ''', (
                cluster_id,
                data['size'],
                f"{source}: {data['sample']}",
                data['anomalies']
            ))
        except Exception:
            pass
    
    conn.commit()


def main():
    print("=" * 60)
    print("  SecureZen Fast Pre-Processor")
    print("  Scanning datasets and extracting threat patterns...")
    print("=" * 60)
    
    # Ensure DB directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Find all log files
    extensions = ['*.log', '*.txt']
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(DATASETS_DIR, '**', ext), recursive=True))
    
    if not files:
        print(f"[WARN] No log files found in: {DATASETS_DIR}")
        print("       Please check the datasets directory path.")
        return
    
    print(f"\n[INFO] Found {len(files)} log files in {DATASETS_DIR}")
    print(f"[INFO] Writing to database: {DB_PATH}\n")
    
    conn = sqlite3.connect(DB_PATH)
    ensure_tables(conn)
    
    pattern_counts = {}   # template -> count (in-memory accumulator)
    cluster_data = {}     # source -> {size, anomalies, sample}
    
    total_lines = 0
    total_threats = 0
    FLUSH_EVERY = 50  # Flush patterns to DB every N files
    
    for i, filepath in enumerate(files, 1):
        lines, threats = process_file(filepath, conn, pattern_counts, cluster_data)
        total_lines += lines
        total_threats += threats
        
        # Progress
        if i % 10 == 0 or i == len(files):
            pct = (i / len(files)) * 100
            print(f"  [{i:4d}/{len(files)}] {pct:5.1f}% | Lines: {total_lines:,} | Threats: {total_threats:,} | Patterns: {len(pattern_counts):,}")
        
        # Flush patterns periodically to avoid memory buildup
        if i % FLUSH_EVERY == 0:
            flush_patterns(conn, pattern_counts)
    
    # Final flush
    print("\n[INFO] Flushing patterns to database...")
    flush_patterns(conn, pattern_counts)
    
    print("[INFO] Writing cluster data...")
    flush_clusters(conn, cluster_data)
    
    conn.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("  SecureZen Pre-Processing Complete!")
    print("=" * 60)
    print(f"  Files Processed : {len(files):,}")
    print(f"  Total Log Lines : {total_lines:,}")
    print(f"  Threats Detected: {total_threats:,}")
    print(f"  Log Sources     : {len(cluster_data)}")
    print(f"\n  Cluster Breakdown:")
    for source, data in sorted(cluster_data.items(), key=lambda x: x[1]['size'], reverse=True):
        print(f"    {source:<20} {data['size']:>8,} lines  |  {data['anomalies']:>5,} threats")
    print(f"\n  Dashboard is ready! Start the server and open the browser.")
    print("=" * 60)


if __name__ == "__main__":
    main()
