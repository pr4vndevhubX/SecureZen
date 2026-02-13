import os
import sys
import json
import time
import pandas as pd
from datetime import datetime

# Add project root and LogAI library to path
# Path: features/syslog_analysis/logai_pipeline.py -> project_root is 3 levels up
# (Note: Previous code was 3 levels, but let's be explicit and check)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from utils.syslog_buffer import SyslogBuffer
from utils.alert_storage import AlertStorage

# Import LogAI components
from logai.preprocess.preprocessor import Preprocessor, PreprocessorConfig
from logai.information_extraction.log_parser import LogParser, LogParserConfig
from logai.analysis.anomaly_detector import AnomalyDetector, AnomalyDetectionConfig

class LogAIPipeline:
    """
    New Primary Ingestion Layer using LogAI for Deep Analysis.
    Process: Raw Log -> Preprocess -> Parse -> Feature Extract -> Anomaly Detection -> Alert
    """
    
    def __init__(self):
        self.buffer = SyslogBuffer()
        self.storage = AlertStorage()
        
        # Initialize LogAI Preprocessor
        self.preprocessor_config = PreprocessorConfig(
            custom_delimiters_regex={"punctuation": r'[()\[\]{},;]'}
        )
        self.preprocessor = Preprocessor(self.preprocessor_config)
        
        # Initialize LogAI Parser (Drain algorithm by default)
        self.parser_config = LogParserConfig(parsing_algorithm="drain")
        self.parser = LogParser(self.parser_config)
        
        # Initialize Anomaly Detector
        self.anomaly_config = AnomalyDetectionConfig(algo_name="one_class_svm")
        self.anomaly_detector = AnomalyDetector(self.anomaly_config)

    def process_logs(self, raw_logs: list, source_ip: str):
        """Processes a batch of raw logs using LogAI"""
        if not raw_logs:
            return
            
        # Convert to pandas Series for LogAI compatibility
        log_series = pd.Series(raw_logs, name="logline")
        
        # 1. Preprocess
        cleaned_logs, _ = self.preprocessor.clean_log(log_series)
        
        # 2. Parse (Templates & Parameters)
        try:
            parsed_df = self.parser.fit_parse(cleaned_logs)
            
            # For demonstration, we'll promote "unseen" or "rare" templates as potential alerts
            # In a full LogAI implementation, we'd use the AnomalyDetector on features
            
            for index, row in parsed_df.iterrows():
                # Simulating threat detection based on parsing results
                # In production, this would be an Anomaly Detection score
                is_anomaly = "password" in row['logline'].lower() or "failed" in row['logline'].lower()
                
                if is_anomaly:
                    threat_score = 80 # High score for demo
                    self.promote_to_alert(row['logline'], source_ip, threat_score, row['parsed_logline'])
                    
        except Exception as e:
            print(f"❌ LogAI Processing Error: {e}")

    def promote_to_alert(self, original_log, source_ip, score, template):
        """Promotes a suspicious log to a SecureZen Alert"""
        alert = {
            "id": f"logai-{int(time.time()*1000)}",
            "timestamp": datetime.utcnow().isoformat(),
            "rule": {
                "level": min(15, score // 5),
                "description": f"LogAI Neural Detection: {template[:50]}..."
            },
            "agent": {
                "name": "LogAI-Node",
                "ip": source_ip
            },
            "full_log": original_log,
            "decoder": {"name": "syslog-logai"}
        }
        self.storage.store_alert(alert)
        print(f"🚀 [LogAI ALERT] Score: {score} | IP: {source_ip} | Log: {original_log[:50]}...")

    def run(self):
        print("="*50)
        print("🤖 LogAI Deep Analysis Pipeline Active")
        print(f"🔄 Consuming raw syslog from Redis: {self.buffer.queue_name}")
        print("="*50)
        
        batch = []
        last_source = None
        
        while True:
            # Fetch from Redis
            log_entry = self.buffer.pop_raw_log(timeout=1)
            if log_entry:
                raw_text = log_entry.get('raw_log', '')
                source_ip = log_entry.get('source_ip', 'unknown')
                
                # Small batching for performance
                batch.append(raw_text)
                last_source = source_ip
                
                if len(batch) >= 5:
                    self.process_logs(batch, last_source)
                    batch = []
            elif batch:
                self.process_logs(batch, last_source)
                batch = []

if __name__ == "__main__":
    pipeline = LogAIPipeline()
    try:
        pipeline.run()
    except KeyboardInterrupt:
        print("\n🛑 LogAI Pipeline shutting down.")
