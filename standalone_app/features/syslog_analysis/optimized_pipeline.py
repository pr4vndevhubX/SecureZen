import os
import sys
import pandas as pd
import logging
from datetime import datetime

# Add the internal library directory to sys.path
lib_path = os.path.join(os.path.dirname(__file__), 'lib')
if lib_path not in sys.path:
    sys.path.append(lib_path)

try:
    from logai.dataloader.data_loader import FileDataLoader, DataLoaderConfig
    from logai.dataloader.data_model import LogRecordObject
    from logai.preprocess.preprocessor import Preprocessor, PreprocessorConfig
    from logai.information_extraction.log_parser import LogParser, LogParserConfig
    from logai.analysis.anomaly_detector import AnomalyDetector, AnomalyDetectionConfig
    from logai.utils import constants
except ImportError as e:
    print(f"Error importing internal libraries: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

import xml.etree.ElementTree as ET
import re

class WazuhRuleEngine:
    def __init__(self, rules_dir):
        self.rules_dir = rules_dir
        self.rules = []
        self._load_rules()

    def _load_rules(self):
        """Parses XML rules from the rules directory."""
        if not os.path.exists(self.rules_dir):
            return

        for filename in os.listdir(self.rules_dir):
            if filename.endswith(".xml"):
                try:
                    tree = ET.parse(os.path.join(self.rules_dir, filename))
                    root = tree.getroot()
                    for group in root.findall('group'):
                        for rule in group.findall('rule'):
                            rule_id = rule.get('id')
                            level = rule.get('level')
                            description = rule.find('description').text if rule.find('description') is not None else ""
                            match = rule.find('match').text if rule.find('match') is not None else None
                            regex = rule.find('regex').text if rule.find('regex') is not None else None
                            
                            self.rules.append({
                                'id': rule_id,
                                'level': level,
                                'description': description,
                                'match': match,
                                'regex': regex
                            })
                except Exception as e:
                    print(f"Error parsing rule file {filename}: {e}")

    def check_log(self, logline):
        """Checks a single logline against all loaded rules."""
        matches = []
        for rule in self.rules:
            if rule['match'] and rule['match'] in logline:
                matches.append(rule)
            elif rule['regex'] and re.search(rule['regex'], logline):
                matches.append(rule)
        return matches

def run_pipeline(dataset_path):
    """
    Orchestrates the security analysis pipeline: 
    Data Layer -> Preprocessing -> Information Extraction -> ML Analysis -> Rule Cross-Check -> Evaluation
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting analysis for dataset: {dataset_path}")

    # 1. Data Layer: Load raw syslogs
    loader_config = DataLoaderConfig(
        filepath=dataset_path,
        log_type="log",
        reader_args={
            "log_format": "<Timestamp> <Host> <Process> <Message>" 
        }
    )
    loader = FileDataLoader(loader_config)
    log_record = loader.load_data()
    logger.info(f"Loaded {len(log_record.body)} log entries.")

    # 2. Preprocessing: Cleaning
    pp_config = PreprocessorConfig(
        custom_delimiters_regex=[r'\s+', r'[,:=]']
    )
    preprocessor = Preprocessor(pp_config)
    cleaned_body, _ = preprocessor.clean_log(log_record.body[constants.LOGLINE_NAME])
    log_record.body[constants.LOGLINE_NAME] = cleaned_body
    logger.info("Preprocessing complete.")

    # 3. Information Extraction: Parsing
    parser_config = LogParserConfig(parsing_algorithm="drain")
    parser = LogParser(parser_config)
    parsed_df = parser.fit_parse(log_record.body[constants.LOGLINE_NAME])
    logger.info("Information extraction (parsing) complete.")

    # 4. ML Analysis: Anomaly Detection
    ad_config = AnomalyDetectionConfig(algo_name="one_class_svm")
    detector = AnomalyDetector(ad_config)
    features = pd.get_dummies(parsed_df[constants.PARSED_LOGLINE_NAME]).astype(float)
    detector.fit(features)
    anomalies = detector.predict(features)
    
    ml_anomaly_count = (anomalies == -1).any(axis=1).sum() if isinstance(anomalies, pd.DataFrame) else (anomalies == -1).sum()
    logger.info(f"ML Analysis complete. Detected {ml_anomaly_count} potential anomalies.")

    # 5. Rule-Based Cross-Checking (Wazuh Rules)
    rules_dir = os.path.join(os.path.dirname(__file__), 'rules')
    rule_engine = WazuhRuleEngine(rules_dir)
    rule_matches = []
    
    for idx, line in log_record.body[constants.LOGLINE_NAME].items():
        matches = rule_engine.check_log(line)
        if matches:
            rule_matches.append({'index': idx, 'log': line, 'matches': matches})
    
    logger.info(f"Rule-Based Analysis complete. Found {len(rule_matches)} known threat patterns.")

    # 6. Database Integration: Store Results in SecureZen Dashboard
    # Add standalone_app to sys.path to import AlertStorage
    app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if app_root not in sys.path:
        sys.path.append(app_root)
    
    anomaly_indices = []
    try:
        from utils.alert_storage import AlertStorage
        storage = AlertStorage() # This will use data/syslog_alerts.db by default
        
        stored_count = 0
        
        # Store Rule-Based Matches
        for item in rule_matches:
            for rule in item['matches']:
                alert = {
                    "id": f"RULE_{rule['id']}_{item['index']}",
                    "timestamp": datetime.now().isoformat() + "Z", # Normalized timestamp
                    "rule": {
                        "id": rule['id'],
                        "level": int(rule['level']),
                        "description": rule['description']
                    },
                    "agent": {
                        "name": "Standalone_Optimizer",
                        "ip": "127.0.0.1"
                    },
                    "data": {
                        "logline": item['log'],
                        "dataset": os.path.basename(dataset_path)
                    },
                    "full_log": item['log']
                }
                storage.store_alert(alert)
                stored_count += 1
                
        # Store ML Anomalies
        # We look for indices where anomalies == -1
        # To avoid flooding, we store a summary or top N
        if isinstance(anomalies, pd.DataFrame):
            # Check for any -1 in the row (if row-based detection)
            # Or if anomalies is a 1D array/series
            anomaly_indices = anomalies.index[(anomalies == -1).any(axis=1)].tolist()
        else:
            # Assuming numpy array or pandas Series
            import numpy as np
            if hasattr(anomalies, 'index'):
                anomaly_indices = anomalies.index[anomalies == -1].tolist()
            else:
                anomaly_indices = np.where(anomalies == -1)[0].tolist()

        for idx in anomaly_indices[:50]: # Cap at 50 per file to avoid dashboard overwhelm
            logline = log_record.body[constants.LOGLINE_NAME].iloc[idx] if hasattr(log_record.body[constants.LOGLINE_NAME], 'iloc') else log_record.body[constants.LOGLINE_NAME][idx]
            alert = {
                "id": f"AI_{idx}_{datetime.now().timestamp()}",
                "timestamp": datetime.now().isoformat() + "Z",
                "rule": {
                    "id": "99999",
                    "level": 10,
                    "description": "AI: Statistical Anomaly Detected in Log Pattern"
                },
                "agent": {
                    "name": "Krya_AI_Engine",
                    "ip": "127.0.0.1"
                },
                "data": {
                    "logline": logline,
                    "anomaly_score": -1,
                    "dataset": os.path.basename(dataset_path)
                },
                "full_log": logline
            }
            storage.store_alert(alert)
            stored_count += 1
            
        logger.info(f"Database sync complete. Stored {stored_count} alerts in syslog_alerts.db")
        
    except Exception as e:
        logger.error(f"Error storing alerts in database: {e}")

    # 6.5. Hybrid Enrichment: Trigger CrewAI for detected IPs
    try:
        from core.securezen.crew import IPIntelligenceCrew
        crew = IPIntelligenceCrew()
        
        # Find unique IPs in stored alerts (srcip or dstip)
        unique_ips = set()
        
        # Regex for IPv4 extraction
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        
        # Check rule matches
        if rule_matches:
            for item in rule_matches:
                found = re.findall(ip_pattern, item['log'])
                for ip in found:
                    if not ip.startswith('127.') and not ip.startswith('192.168.1.') and not ip.startswith('10.'):
                        unique_ips.add(ip)
        
        # Check ML anomalies
        if len(anomaly_indices) > 0:
            for idx in anomaly_indices[:20]:
                logline = log_record.body[constants.LOGLINE_NAME].iloc[idx] if hasattr(log_record.body[constants.LOGLINE_NAME], 'iloc') else log_record.body[constants.LOGLINE_NAME][idx]
                found = re.findall(ip_pattern, logline)
                for ip in found:
                    if not ip.startswith('127.') and not ip.startswith('192.168.1.') and not ip.startswith('10.'):
                        unique_ips.add(ip)
        
        if unique_ips:
            logger.info(f"Triggering CrewAI enrichment for {len(unique_ips)} unique external IPs: {unique_ips}")
            import threading
            threads = []
            for ip in unique_ips:
                # Run enrichment
                thread = threading.Thread(target=crew.run_and_store, args=(ip,))
                thread.daemon = False # Don't terminate early
                thread.start()
                threads.append(thread)
            
            # For testing: wait for threads
            for t in threads:
                t.join(timeout=30) # Wait up to 30s per enrichment for test
        else:
            logger.info("No external IPs found for enrichment.")
        
    except Exception as e:
        logger.error(f"Error triggering CrewAI enrichment: {e}")
        import traceback
        logger.error(traceback.format_exc())

    # 7. Evaluation & Reporting
    report_path = os.path.join(os.path.dirname(__file__), "analysis_report.md")
    with open(report_path, "w") as f:
        f.write("# Hybrid Security Analysis Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Dataset:** {dataset_path}\n")
        f.write(f"**Total Logs Processed:** {len(log_record.body)}\n\n")
        
        f.write("## 1. Rule-Based Findings (Wazuh Rules)\n")
        f.write(f"- **Matches Found:** {len(rule_matches)}\n")
        if rule_matches:
            f.write("| Index | Log Snippet | Rule Description | Level |\n")
            f.write("|-------|-------------|------------------|-------|\n")
            for item in rule_matches[:10]: # Top 10
                desc = item['matches'][0]['description']
                level = item['matches'][0]['level']
                f.write(f"| {item['index']} | {item['log'][:50]}... | {desc} | {level} |\n")
        
        f.write("\n## 2. AI-Based Findings (Anomaly Detection)\n")
        f.write(f"- **Statistical Outliers:** {ml_anomaly_count}\n")
        f.write("\n**Summary:** The combined detection of traditional rules and AI identified potential threats which have been synced to the SecureZen dashboard.\n")

    logger.info(f"Hybrid report generated at: {report_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sample_dataset = sys.argv[1]
    else:
        # Point to a sample dataset for testing
        sample_dataset = r"C:\Users\psuresh\OneDrive - KRYA SOLUTIONS PRIVATE LIMITED\Desktop\KYD\Agentic-ai-02\IP-alone-Crewai\ip-intel-crewai\datasets\suspicious_behaviour\windows_lolbas_risk\lolbinrisk.log"
    
    if os.path.exists(sample_dataset):
        run_pipeline(sample_dataset)
    else:
        print(f"Dataset not found: {sample_dataset}")
        # Search for any log file as fallback
        datasets_dir = r"C:\Users\psuresh\OneDrive - KRYA SOLUTIONS PRIVATE LIMITED\Desktop\KYD\Agentic-ai-02\IP-alone-Crewai\ip-intel-crewai\datasets"
        found = False
        for root, dirs, files in os.walk(datasets_dir):
            for file in files:
                if file.endswith(".log") or file.endswith(".txt"):
                    sample_dataset = os.path.join(root, file)
                    print(f"Falling back to: {sample_dataset}")
                    run_pipeline(sample_dataset)
                    found = True
                    break
            if found: break
        if not found:
            print("No sample dataset found to run the pipeline.")
