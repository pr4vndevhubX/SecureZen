from crewai.tools import BaseTool
import re

class AlertTriageTool(BaseTool):
    name: str = "Alert Triage Tool"
    description: str = "Analyze and prioritize security alerts based on threat intelligence data"
    
    def _run(self, alert_data: str) -> str:
        """
        Real threat scoring based on available intelligence.
        Analyzes the context from previous agent findings to determine priority.
        """
        # Extract key threat indicators from the alert_data context
        priority_score = 0
        justification_parts = []
        
        # Check for VirusTotal detections
        vt_match = re.search(r'(\d+)\s+out of\s+(\d+)\s+vendors.*malicious', alert_data, re.IGNORECASE)
        if vt_match:
            detections = int(vt_match.group(1))
            total = int(vt_match.group(2))
            detection_rate = (detections / total) * 100 if total > 0 else 0
            
            if detection_rate > 15:  # More than 15% vendors flagged it
                priority_score += 40
                justification_parts.append(f"VirusTotal: {detections}/{total} vendors flagged as malicious ({detection_rate:.1f}%)")
            elif detection_rate > 5:
                priority_score += 20
                justification_parts.append(f"VirusTotal: {detections}/{total} vendors flagged ({detection_rate:.1f}%)")
        
        # Check for AbuseIPDB confidence
        abuse_match = re.search(r'Abuse confidence:\s+(\d+)%', alert_data, re.IGNORECASE)
        if abuse_match:
            confidence = int(abuse_match.group(1))
            if confidence >= 90:
                priority_score += 40
                justification_parts.append(f"AbuseIPDB: {confidence}% abuse confidence (HIGH)")
            elif confidence >= 50:
                priority_score += 25
                justification_parts.append(f"AbuseIPDB: {confidence}% abuse confidence (MEDIUM)")
            elif confidence >= 20:
                priority_score += 10
                justification_parts.append(f"AbuseIPDB: {confidence}% abuse confidence (LOW)")
        
        # Check for report count
        reports_match = re.search(r'(\d+)\s+reports', alert_data, re.IGNORECASE)
        if reports_match:
            reports = int(reports_match.group(1))
            if reports > 10000:
                priority_score += 15
                justification_parts.append(f"High report volume: {reports:,} reports")
            elif reports > 1000:
                priority_score += 10
                justification_parts.append(f"Moderate report volume: {reports:,} reports")
        
        # Check for MITRE techniques
        if 'T1071' in alert_data or 'T1190' in alert_data or 'T1566' in alert_data:
            priority_score += 5
            justification_parts.append("Associated with known MITRE ATT&CK techniques")
        
        # Determine priority level based on score
        if priority_score >= 70:
            priority = "P1"
            severity = "CRITICAL"
        elif priority_score >= 50:
            priority = "P2"
            severity = "HIGH"
        elif priority_score >= 30:
            priority = "P3"
            severity = "MEDIUM"
        elif priority_score >= 15:
            priority = "P4"
            severity = "LOW"
        else:
            priority = "P5"
            severity = "INFORMATIONAL"
        
        # Build response
        if justification_parts:
            justification = " | ".join(justification_parts)
            return f"Priority: {priority} ({severity}) | Score: {priority_score}/100 | Factors: {justification}"
        else:
            # Fallback if no data found
            return f"Priority: P5 (INFORMATIONAL) | Score: 0/100 | No significant threat indicators found in available data"
