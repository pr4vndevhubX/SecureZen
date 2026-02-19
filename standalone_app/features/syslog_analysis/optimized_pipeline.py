import os
import sys
import sqlite3
import pandas as pd
import logging
from datetime import datetime

# Add the internal library directory to sys.path
lib_path = os.path.join(os.path.dirname(__file__), 'lib')
if lib_path not in sys.path:
    sys.path.append(lib_path)

try:
    # Import from the local ported LogAI source code
    # We use a try-except to handle different execution contexts (as a script or as a module)
    try:
        from features.syslog_analysis.logai.dataloader.data_loader import FileDataLoader, DataLoaderConfig
        from features.syslog_analysis.logai.dataloader.data_model import LogRecordObject
        from features.syslog_analysis.logai.preprocess.preprocessor import Preprocessor, PreprocessorConfig
        from features.syslog_analysis.logai.information_extraction.log_parser import LogParser, LogParserConfig
        from features.syslog_analysis.logai.analysis.anomaly_detector import AnomalyDetector, AnomalyDetectionConfig
        from features.syslog_analysis.logai.utils import constants
    except ImportError:
        # Fallback for direct script execution
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
        from logai.dataloader.data_loader import FileDataLoader, DataLoaderConfig
        from logai.dataloader.data_model import LogRecordObject
        from logai.preprocess.preprocessor import Preprocessor, PreprocessorConfig
        from logai.information_extraction.log_parser import LogParser, LogParserConfig
        from logai.analysis.anomaly_detector import AnomalyDetector, AnomalyDetectionConfig
        from logai.utils import constants
except Exception as e:
    print(f"Critical error importing LogAI core: {e}")
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

def parse_sysmon_linux_logs(filepath):
    """
    Parses Sysmon for Linux XML logs into a pandas DataFrame compatible with LogRecordObject.
    """
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Sysmon logs might be multiple XML root elements concatenated, which is invalid XML.
        # We need to wrap them or parse them individually.
        # Assuming one <Event> per line or a file full of <Event> tags.
        
        # Strategy: Find all <Event> blocks
        events = re.findall(r'<Event.*?</Event>', content, re.DOTALL)
        
        for event_xml in events:
            root = ET.fromstring(event_xml)
            namespace = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
            
            system = root.find('ns:System', namespace)
            event_data = root.find('ns:EventData', namespace)
            
            timestamp = system.find('ns:TimeCreated', namespace).get('SystemTime')
            host = system.find('ns:Computer', namespace).text
            
            # Extract key fields from EventData
            data_map = {}
            if event_data is not None:
                for data_item in event_data.findall('ns:Data', namespace):
                    name = data_item.get('Name')
                    value = data_item.text
                    data_map[name] = value
            
            # Construct a log message string similar to syslog for consistency
            # Format: <Timestamp> <Host> <Process> <Message>
            image = data_map.get('Image', 'UnknownProcess')
            message = " ".join([f"{k}={v}" for k, v in data_map.items()])
            
            data.append({
                constants.LOGLINE_NAME: f"{timestamp} {host} {image} {message}",
                "timestamp": timestamp,
                "host": host
            })
            
    except Exception as e:
        print(f"Error parsing Sysmon XML {filepath}: {e}")
        return pd.DataFrame()
        
    return pd.DataFrame(data)

def run_pipeline(dataset_paths):
    """
    Orchestrates the security analysis pipeline for a batch of files.
    Data Layer -> Preprocessing -> Information Extraction -> ML Analysis -> Rule Cross-Check -> Evaluation
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Normalize input: always work with a list
    if isinstance(dataset_paths, str):
        dataset_paths = [dataset_paths]

    logger.info(f"Starting batch analysis for {len(dataset_paths)} files...")

    # --- GLOBAL INITIALIZATIONS (Run ONCE per batch) ---
    logger.info("Initializing Analysis Engine (Rules, ML, CrewAI)...")
    
    # 1. Wazuh Rules
    rules_dir = os.path.join(os.path.dirname(__file__), 'rules')
    rule_engine = WazuhRuleEngine(rules_dir)
    
    # 2. Database Connection
    # Current file: standalone_app/features/syslog_analysis/optimized_pipeline.py
    # Root: standalone_app
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_root = os.path.dirname(os.path.dirname(current_dir))
    project_root = os.path.dirname(app_root)
    
    for p in [app_root, project_root]:
        if p not in sys.path:
            sys.path.append(p)

    try:
        from utils.alert_storage import AlertStorage
    except ImportError:
        from standalone_app.utils.alert_storage import AlertStorage
    try:
        storage = AlertStorage()
    except Exception as e:
        logger.error(f"Failed to initialize AlertStorage: {e}")
        return

    # 3. LogAI Models (Initialized ONCE for the entire batch)
    try:
        parser_config = LogParserConfig(parsing_algorithm="drain")
        parser = LogParser(parser_config)
        
        ad_config = AnomalyDetectionConfig(algo_name="one_class_svm")
        detector = AnomalyDetector(ad_config)
        
        preprocessor = Preprocessor(PreprocessorConfig(custom_delimiters_regex=[r'\s+', r'[,:=]']))
    except Exception as e:
        logger.error(f"Failed to initialize LogAI Models: {e}")
        parser, detector, preprocessor = None, None, None

    # 4. CrewAI Agent
    try:
        from core.securezen.crew import IPIntelligenceCrew
        crew = IPIntelligenceCrew()
    except Exception as e:
        logger.error(f"Failed to initialize CrewAI: {e}")
        crew = None

    # --- PROCESS FILES ---
    for i, dataset_path in enumerate(dataset_paths, 1):
        logger.info(f"[{i}/{len(dataset_paths)}] Analyze: {os.path.basename(dataset_path)}")
        try:
            process_single_file(dataset_path, logger, rule_engine, storage, crew, parser, detector, preprocessor)
        except Exception as e:
             logger.error(f"Failed to process {dataset_path}: {e}")

def process_single_file(dataset_path, logger, rule_engine, storage, crew, parser=None, detector=None, preprocessor=None):
    # 1. Data Layer: Load raw syslogs
    # Check if file is Sysmon formatted (XML-like content check)
    is_sysmon = False
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            head = f.read(1024)
            if '<Event' in head and 'http://schemas.microsoft.com/win/2004/08/events/event' in head:
                is_sysmon = True
    except Exception:
        pass

    if is_sysmon:
        logger.info("Detected Sysmon for Linux XML log format.")
        df = parse_sysmon_linux_logs(dataset_path)
        if df.empty:
            logger.warning("Parsed DataFrame is empty. Skipping.")
            return
        
        # Manually construct LogRecordObject
        log_record = LogRecordObject()
        log_record.body = df
    else:
        loader_config = DataLoaderConfig(
            filepath=dataset_path,
            log_type="log",
            reader_args={
                "log_format": "<Timestamp> <Host> <Process> <Message>" 
            }
        )
        loader = FileDataLoader(loader_config)
        log_record = loader.load_data()
    
    if log_record.body.empty:
            logger.warning("Log record body is empty. Skipping.")
            return

    logger.info(f"Loaded {len(log_record.body)} log entries.")

    # 2. Preprocessing: Cleaning
    if not preprocessor:
        pp_config = PreprocessorConfig(
            custom_delimiters_regex=[r'\s+', r'[,:=]']
        )
        preprocessor = Preprocessor(pp_config)
        
    cleaned_body, _ = preprocessor.clean_log(log_record.body[constants.LOGLINE_NAME])
    log_record.body[constants.LOGLINE_NAME] = cleaned_body

    # 3. Information Extraction: Parsing
    if not parser:
        parser_config = LogParserConfig(parsing_algorithm="drain")
        parser = LogParser(parser_config)
        
    parsed_df = parser.fit_parse(log_record.body[constants.LOGLINE_NAME])

    # 4. ML Analysis: Anomaly Detection
    if not detector:
        ad_config = AnomalyDetectionConfig(algo_name="one_class_svm")
        detector = AnomalyDetector(ad_config)
        
    features = pd.get_dummies(parsed_df[constants.PARSED_LOGLINE_NAME]).astype(float)
    detector.fit(features)
    anomalies = detector.predict(features)
    
    ml_anomaly_count = (anomalies == -1).any(axis=1).sum() if isinstance(anomalies, pd.DataFrame) else (anomalies == -1).sum()
    logger.info(f"ML Analysis complete. Detected {ml_anomaly_count} potential anomalies.")

    # 5. Rule-Based Cross-Checking (Wazuh Rules)
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

        # --- NEW: Store Log Patterns ---
        conn = sqlite3.connect(storage.db_path)
        cursor = conn.cursor()
        
        # Simple pattern extraction (using parsed logline templates if available, otherwise raw)
        # In a real LogAI pipeline, parsed_df[constants.PARSED_LOGLINE_NAME] would be the template.
        # Here we use the parsed output or fallback to a simplified regex masking.
        
        try:
             # Group by template/message to count occurrences
            logger.info(f"DEBUG: parsed_df columns: {parsed_df.columns.tolist()}")
            if constants.PARSED_LOGLINE_NAME in parsed_df.columns:
                pattern_counts = parsed_df[constants.PARSED_LOGLINE_NAME].value_counts()
                logger.info(f"DEBUG: Found {len(pattern_counts)} unique patterns.")
                for pattern, count in pattern_counts.items():
                    cursor.execute('''
                        INSERT INTO log_patterns (signature, occurrence_count, first_seen, last_seen)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(signature) DO UPDATE SET
                            occurrence_count = occurrence_count + excluded.occurrence_count,
                            last_seen = excluded.last_seen
                    ''', (str(pattern), int(count), datetime.now().isoformat(), datetime.now().isoformat()))
            else:
                logger.warning(f"DEBUG: {constants.PARSED_LOGLINE_NAME} NOT in parsed_df columns.")
            conn.commit()
            logger.info("Log patterns stored.")
        except Exception as e:
            logger.error(f"Error storing patterns: {e}")

        # --- NEW: Store Clusters (Mocking for now based on user request as we don't have clustering enabled) ---
        # In full implementation, we would use KMeans/Dbscan output. 
        # For now, we'll create a single cluster entry for the file to populate the chart.
        try:
             cursor.execute('''
                INSERT OR REPLACE INTO log_clusters (cluster_id, size, representative_log, anomalies_count, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (abs(hash(dataset_path)) % 10000, len(log_record.body), "System generated cluster for " + os.path.basename(dataset_path), len(anomaly_indices), "Active"))
             conn.commit()
        except Exception as e:
            logger.error(f"Error storing clusters: {e}")
            
        conn.close()

    except Exception as e:
        logger.error(f"Error storing alerts in database: {e}")

    # 6.5. Hybrid Enrichment: CrewAI IP enrichment (disabled during batch ingestion for speed)
    # To re-enable, set ENABLE_CREWAI_ENRICHMENT=1 in environment
    if os.environ.get('ENABLE_CREWAI_ENRICHMENT', '0') == '1':
        try:
            from core.securezen.crew import IPIntelligenceCrew
            crew = IPIntelligenceCrew()
            unique_ips = set()
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            if rule_matches:
                for item in rule_matches:
                    is_critical = any(int(r['level']) >= 10 for r in item['matches'])
                    if is_critical:
                        found = re.findall(ip_pattern, item['log'])
                        for ip in found:
                            if not ip.startswith('127.') and not ip.startswith('192.168.') and not ip.startswith('10.'):
                                unique_ips.add(ip)
            if unique_ips:
                logger.info(f"Triggering CrewAI enrichment for {len(unique_ips)} IPs")
                import threading
                for ip in unique_ips:
                    t = threading.Thread(target=crew.run_and_store, args=(ip,))
                    t.daemon = True
                    t.start()
        except Exception as e:
            logger.error(f"CrewAI enrichment skipped: {e}")
    else:
        logger.info("CrewAI enrichment disabled (set ENABLE_CREWAI_ENRICHMENT=1 to enable)")

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
        # Batch processing: Accept all arguments as file paths
        datasets = sys.argv[1:]
        run_pipeline(datasets)
    else:
        # Point to a sample dataset for testing
        sample_dataset = r"C:\Users\psuresh\OneDrive - KRYA SOLUTIONS PRIVATE LIMITED\Desktop\KYD\Agentic-ai-02\IP-alone-Crewai\ip-intel-crewai\datasets\suspicious_behaviour\windows_lolbas_risk\lolbinrisk.log"
    
        if os.path.exists(sample_dataset):
            run_pipeline([sample_dataset])
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
                        run_pipeline([sample_dataset])
                        found = True
                        break
                if found:
                    break
        if not found:
            print("No sample dataset found to run the pipeline.")
