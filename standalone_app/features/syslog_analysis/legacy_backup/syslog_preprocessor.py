import json
import re
import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.syslog_buffer import SyslogBuffer
from utils.alert_storage import AlertStorage

class NeuralPreprocessor:
    """
    Layer 3: The Intelligence Layer.
    Consumes raw logs from Redis and promotes them to 'Alerts'.
    """
    
    def __init__(self):
        self.buffer = SyslogBuffer()
        self.storage = AlertStorage()
        
        # Simple Regex for RFC3164 Syslog (Common format)
        # Examples: <34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick
        self.syslog_pattern = re.compile(r'^<(?P<pri>\d+)>(?P<timestamp>\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+(?P<hostname>\S+)\s+(?P<app_name>\S+)(?:\[(?P<pid>\d+)\])?:\s+(?P<message>.*)$')

    def parse_log(self, raw_log):
        """Step 1: Parsing - Transforming raw text to JSON"""
        match = self.syslog_pattern.match(raw_log)
        if match:
            data = match.groupdict()
            # Calculate Severity from PRI (Priority)
            # Facility = PRI // 8, Severity = PRI % 8
            data['severity_lvl'] = int(data['pri']) % 8
            return data
        
        # Fallback for non-standard formats
        return {
            "message": raw_log,
            "severity_lvl": 5, # Default to notice
            "hostname": "unknown",
            "app_name": "generic"
        }

    def apply_neural_filter(self, parsed_data):
        """
        Step 2: Neural Analysis (Simulated)
        In a full implementation, this calls an LLM or Neural Network.
        Here we use heuristic scoring to decide if this is a 'High Value' alert.
        """
        message = parsed_data.get('message', '').lower()
        score = 0
        
        # High-intent keywords (Malicious patterns)
        threat_keywords = {
            "failed password": 40,
            "invalid user": 30,
            "exploit": 90,
            "malware": 95,
            "unauthorized": 50,
            "shell": 40,
            "root": 20
        }
        
        for kw, weight in threat_keywords.items():
            if kw in message:
                score += weight
                
        # Adjust score by original syslog severity level (0=Emerg, 7=Debug)
        # Lower severity (higher number) reduces the total score
        original_sev = parsed_data.get('severity_lvl', 7)
        score += (7 - original_sev) * 10
        
        return score

    def run(self):
        """The main loop of the pre-processor"""
        print("="*50)
        print("[BRAIN] SecureZen Neural Pre-processor Active")
        print(f"? Reading from Redis: {self.buffer.queue_name}")
        print("="*50)

        while True:
            # 1. Fetch from Redis (Wait indefinitely if queue is empty)
            log_entry = self.buffer.pop_raw_log(timeout=0)
            if not log_entry:
                continue

            raw_text = log_entry.get('raw_log', '')
            source_ip = log_entry.get('source_ip', 'unknown')
            
            # 2. Parse the text
            parsed = self.parse_log(raw_text)
            
            # 3. Analyze / Score (Neural Filter)
            threat_score = self.apply_neural_filter(parsed)
            
            # 4. Filter & Promote
            # Only store in DB if score > 30 (Filters out 90% of noise)
            if threat_score > 30:
                print(f"? [ALERT DETECTED] Score: {threat_score} | App: {parsed['app_name']} | Host: {parsed['hostname']}")
                
                # Format for AlertStorage (Wazuh format emulation)
                simulated_alert = {
                    "id": f"sz-{int(time.time()*1000)}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "rule": {
                        "level": min(15, threat_score // 10), # Scale to Wazuh's 0-15
                        "description": f"SecureZen Neural Detection: {parsed['message'][:50]}..."
                    },
                    "agent": {
                        "name": parsed['hostname'],
                        "ip": source_ip
                    },
                    "full_log": raw_text,
                    "decoder": {"name": parsed['app_name']}
                }
                
                # 5. Save to Permanent Alert Storage
                self.storage.store_alert(simulated_alert)
            else:
                # Silently drop noise
                pass

if __name__ == "__main__":
    preprocessor = NeuralPreprocessor()
    try:
        preprocessor.run()
    except KeyboardInterrupt:
        print("\n? Pre-processor shutting down.")
