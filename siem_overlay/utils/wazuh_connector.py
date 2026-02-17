"""
Wazuh Alert Connector - CSV Only (Simplified)
Webhook functionality can be added later
"""

import pandas as pd
import json
from datetime import datetime
from utils.database import ThreatDatabase
import re

class WazuhConnector:
    def __init__(self):
        self.db = ThreatDatabase()
    
    def load_csv_alerts(self, csv_path):
        """Load Wazuh alerts from CSV file"""
        print(f"[FILE] Loading alerts from CSV: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            # Expected CSV columns (adjust based on your Wazuh export format)
            # Time, Alert Id, Type, Severity, Analyst Verdict, Origin, Message, Entity, Entity Type, Entity Group
            
            alerts_loaded = 0
            
            for _, row in df.iterrows():
                # Map CSV columns to database schema
                alert_data = {
                    'alert_id': str(row.get('Alert Id', '')),
                    'timestamp': self._parse_timestamp(row.get('Time', '')),
                    'rule_level': self._severity_to_level(row.get('Severity', 'Critical')),
                    'rule_id': '',  # Not in CSV
                    'rule_description': str(row.get('Type', '')),
                    'rule_mitre_id': '',  # Extract from message if available
                    'rule_mitre_tactic': '',
                    'rule_mitre_technique': '',
                    'agent_name': str(row.get('Entity', '')),
                    'agent_ip': '',
                    'src_ip': self._extract_ip_from_entity(str(row.get('Entity', ''))),
                    'dst_ip': '',
                    'message': str(row.get('Message', '')),
                    'severity': str(row.get('Severity', 'Critical'))
                }
                
                # Extract MITRE info from message if present
                mitre_info = self._extract_mitre_from_message(str(row.get('Message', '')))
                alert_data.update(mitre_info)
                
                if self.db.insert_wazuh_alert(alert_data):
                    alerts_loaded += 1
            
            print(f"[OK] Loaded {alerts_loaded} alerts from CSV")
            return alerts_loaded
            
        except Exception as e:
            print(f"[ERR] Error loading CSV: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def _parse_timestamp(self, time_str):
        """Parse timestamp from CSV"""
        try:
            # Try common formats
            formats = [
                '%m/%d/%Y %I:%M:%S %p',  # 02/01/2026 07:28:11 AM
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(time_str, fmt)
                    return dt.isoformat()
                except:
                    continue
            
            # If all fail, return current time
            return datetime.now().isoformat()
            
        except:
            return datetime.now().isoformat()
    
    def _severity_to_level(self, severity):
        """Convert severity text to numeric level"""
        severity_map = {
            'Critical': 12,
            'High': 10,
            'Medium': 7,
            'Low': 5
        }
        return severity_map.get(str(severity), 7)
    
    def _extract_ip_from_entity(self, entity_text):
        """Extract IP from entity field"""
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        match = re.search(ip_pattern, str(entity_text))
        return match.group(0) if match else ''
    
    def _extract_mitre_from_message(self, message):
        """Extract MITRE technique from message"""
        mitre_info = {
            'rule_mitre_id': '',
            'rule_mitre_tactic': '',
            'rule_mitre_technique': ''
        }
        
        # Look for MITRE technique ID (e.g., T1071)
        technique_match = re.search(r'T\d{4}', str(message))
        if technique_match:
            mitre_info['rule_mitre_id'] = technique_match.group(0)
            
            # Try to extract technique name
            # Example: "T1071: Application Layer Protocol"
            technique_name_match = re.search(r'T\d{4}:\s*([^,\n]+)', str(message))
            if technique_name_match:
                mitre_info['rule_mitre_technique'] = technique_name_match.group(1).strip()
        
        return mitre_info

# ===== USAGE EXAMPLE =====
if __name__ == "__main__":
    connector = WazuhConnector()
    
    # Load from CSV
    connector.load_csv_alerts('data/wazuh_alerts.csv')
    
    # Option 2: Start webhook server (for future integration)
    # connector.start_webhook_server(port=5000)