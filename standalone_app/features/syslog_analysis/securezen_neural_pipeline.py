
import os
import sys
import json
import time
import pandas as pd
from datetime import datetime

# Add project root and LogAI library to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from utils.syslog_buffer import SyslogBuffer
from utils.alert_storage import AlertStorage

# Import Internal Logic (formerly LogAI)
# Treating 'lib' as a black box engine.
from logai.preprocess.preprocessor import Preprocessor, PreprocessorConfig
from logai.information_extraction.log_parser import LogParser, LogParserConfig
from logai.analysis.anomaly_detector import AnomalyDetector, AnomalyDetectionConfig

# New AI Engines
from logai.algorithms.vectorization_algo.tfidf import TfIdf, TfIdfParams
from logai.algorithms.clustering_algo.kmeans import KMeansAlgo, KMeansParams

# GenAI
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class SecureZenNeuralEngine:
    """
    SecureZen Neural Engine
    =======================
    The core neural processing unit for the SecureZen AI SOC.
    
    Architecture:
    1. Data Layer: Ingestion from Redis/Files
    2. Preprocessing: Cleaning and Normalization
    3. Information Extraction: Neural Parsing (Drain) & Vectorization (TF-IDF)
    4. Analysis: Clustering (K-Means) & Anomaly Detection
    5. Reasoning: LLM-based Hybrid Classification & Summarization (Groq)
    """
    
    def __init__(self):
        self.buffer = SyslogBuffer()
        self.storage = AlertStorage()
        
        print("🧠 Initializing SecureZen Neural Engine...")
        
        # 1. Preprocessing Engine
        self.preprocessor_config = PreprocessorConfig(
            custom_delimiters_regex={"punctuation": r'[()\[\]{},;]'}
        )
        self.preprocessor = Preprocessor(self.preprocessor_config)
        
        # 2. Information Extraction Engine (Neural Parsing)
        self.parser_config = LogParserConfig.from_dict({
            "parsing_algorithm": "drain",
            "parsing_algo_params": {"sim_th": 0.4, "depth": 4}
        })
        self.parser = LogParser(self.parser_config)

        # 2.5 Vectorization Engine (TF-IDF)
        self.vectorizer_config = TfIdfParams(max_features=500)
        self.vectorizer = TfIdf(self.vectorizer_config)
        
        # 2.8 Clustering Engine (K-Means)
        self.clustering_config = KMeansParams(n_clusters=5)  # Dynamic clustering
        self.clustering = KMeansAlgo(self.clustering_config)
        
        # 3. Anomaly Analysis Engine
        self.anomaly_config = AnomalyDetectionConfig(algo_name="isolation_forest")
        self.anomaly_detector = AnomalyDetector(self.anomaly_config)
        
        # 4. GenAI Engine (LLM)
        self.llm_client = None
        self.llm_model = os.getenv("OPENAI_MODEL_NAME", "openai/gpt-oss-120b")
        if OpenAI:
            try:
                self.llm_client = OpenAI(
                    base_url=os.getenv("OPENAI_API_BASE"),
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                print("🤖 GenAI Module: Online (Groq/OpenAI)")
            except Exception as e:
                print(f"⚠️ GenAI Module Initialization Failed: {e}")
        
        print("✅ Neural Engine Online.")

    def preprocess_data(self, raw_logs: pd.Series):
        """Stage 1: Clean and normalize raw log data."""
        cleaned_logs, _ = self.preprocessor.clean_log(raw_logs)
        return cleaned_logs

    def extract_features(self, cleaned_logs: pd.Series):
        """Stage 2: Extract structured templates and features."""
        try:
            parsed_df = self.parser.fit_parse(cleaned_logs)
            return parsed_df
        except Exception as e:
            print(f"⚠️ Feature Extraction Warning: {e}")
            # Return basic DF if parsing fails
            return pd.DataFrame({'logline': cleaned_logs})

    def vectorize_logs(self, parsed_df: pd.DataFrame):
        """Stage 2.5: Convert text templates to numeric vectors (TF-IDF)."""
        try:
            # We fit_transform on the current batch.
            # In production, we should 'fit' on a training set and 'transform' here.
            # For this transition, we assume dynamic fitting.
            if 'logline' not in parsed_df.columns:
                return None
            
            self.vectorizer.fit(parsed_df['logline'])
            vectors = self.vectorizer.transform(parsed_df['logline'])
            return vectors
        except Exception as e:
            print(f"⚠️ Vectorization Warning: {e}")
            return None

    def cluster_logs(self, vectors):
        """Stage 2.8: Cluster logs using K-Means."""
        try:
            if vectors is None:
                return None
            self.clustering.fit(vectors)
            clusters = self.clustering.predict(vectors)
            return clusters
        except Exception as e:
            print(f"⚠️ Clustering Warning: {e}")
            return None

    def hybrid_classify_llm(self, log_text: str):
        """
        Stage 4: GenAI Hybrid Classification ("AI Explain")
        Uses Groq/LLM to explain the log and assess severity.
        """
        if not self.llm_client:
            return None

        try:
            prompt = (
                f"You are a Tier-3 Security Analyst. Analyze this syslog entry:\n"
                f"Log: {log_text}\n\n"
                f"1. Explain what happened in 1 sentence.\n"
                f"2. Assign Severity (Low/Medium/High/Critical).\n"
                f"3. Output format: JSON {{'explanation': '...', 'severity': '...'}}"
            )
            
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            # Basic parsing if LLM returns markdown code block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            return json.loads(content)
        except Exception as e:
            print(f"⚠️ GenAI Classification Failed: {e}")
            return None

    def generate_summary(self, alerts: list):
        """
        Stage 5: Alert Summarization (GenAI)
        Aggregates multiple alerts into a concise analyst briefing.
        """
        if not self.llm_client or not alerts:
            return None

        try:
            alert_texts = [f"- {a['rule']['description']} (Score: {a['data'].get('vector_score', 0)})" for a in alerts[:10]]
            combined_text = "\n".join(alert_texts)
            
            prompt = (
                f"You are a Security Operations Center (SOC) Manager. \n"
                f"Summarize these recent security alerts into a brief 3-bullet executive update:\n\n"
                f"{combined_text}"
            )
            
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ GenAI Summarization Failed: {e}")
            return None

    def analyze_anomalies(self, parsed_df: pd.DataFrame, clusters=None):
        """Stage 3: Detect anomalies using clustering and rarity analysis."""
        # Use 'parsed_logline' which contains the learned template
        template_column = 'parsed_logline'
        if template_column not in parsed_df.columns:
            template_column = 'logline'
            
        template_counts = parsed_df[template_column].value_counts(normalize=True).to_dict()
        
        anomalies = []
        for index, row in parsed_df.iterrows():
            # Rarity score (0 to 100)
            rarity = 1.0 - template_counts.get(row[template_column], 0)
            
            # Dynamic Threat Scoring
            threat_boost = 0
            if any(x in str(row['logline']).lower() for x in ["fail", "deny", "invalid", "violation", "reject", "unauthorized"]):
                threat_boost = 40
            
            # Final Score = (Rarity Weight) + (Keyword Weight)
            final_score = (rarity * 60) + threat_boost
            
            # Cluster Context (if available)
            cluster_id = -1
            if clusters is not None and index < len(clusters):
                cluster_id = int(clusters.iloc[index])
            
            if final_score > 70: # Threshold for "Alert"
                anomalies.append({
                    "original_log": row['logline'],
                    "score": int(min(100, final_score)),
                    "template": row[template_column],
                    "cluster_id": cluster_id
                })
        return anomalies

    def classify_log(self, log_text: str):
        """
        Stage 1.5: AI Classification (Normal vs. Critical)
        Returns: 'Normal', 'Suspicious', or 'Critical'
        """
        lower_log = log_text.lower()
        
        critical_keywords = [
            "failed password", "unauthorized", "intrusion", "exploit", "attack", 
            "root", "admin", "denied", "segfault", "panic", "corrupt"
        ]
        
        suspicious_keywords = [
            "connection lost", "timeout", "warning", "delete", "remove", 
            "modify", "change", "reset"
        ]
        
        if any(k in lower_log for k in critical_keywords):
            return "Critical"
        elif any(k in lower_log for k in suspicious_keywords):
            return "Suspicious"
        
        return "Normal"

    def process_batch(self, raw_logs: list, source_ip: str):
        """Main Pipeline Execution Method"""
        if not raw_logs:
            return

        # Filter: Only analyze interesting logs to save compute resource
        interesting_logs = []
        for log in raw_logs:
            classification = self.classify_log(log)
            # We deep analyze Critical and Suspicious logs
            if classification in ["Critical", "Suspicious"]:
                interesting_logs.append(log)
        
        if not interesting_logs:
            return

        # Convert to pandas Series for internal engine
        log_series = pd.Series(interesting_logs, name="logline")
        
        # Execute Pipeline Stages
        # 1. Clean
        cleaned_logs = self.preprocess_data(log_series)
        
        # 2. Extract Features (Templates)
        parsed_df = self.extract_features(cleaned_logs)
        
        # 2.5 Vectorize & Cluster (Full AI Suite)
        vectors = self.vectorize_logs(parsed_df)
        clusters = self.cluster_logs(vectors)
        
        # 3. Analyze
        anomalies = self.analyze_anomalies(parsed_df, clusters)
        
        # Handle Results
        for anomaly in anomalies:
            # 4. GenAI Enrichment (for high severity)
            ai_context = None
            if anomaly['score'] > 85: 
                ai_context = self.hybrid_classify_llm(anomaly['original_log'])
            
            self.trigger_alert(
                original_log=anomaly['original_log'],
                source_ip=source_ip,
                score=anomaly['score'],
                template=anomaly['template'],
                cluster_id=anomaly.get('cluster_id', -1),
                ai_context=ai_context
            )

    def trigger_alert(self, original_log, source_ip, score, template, cluster_id=-1, ai_context=None):
        """Promotes a suspicious log to a SecureZen Neural Alert"""
        
        description = f"SecureZen Neural Detection: {template[:50]}..."
        severity_level = min(15, score // 5)
        
        # If GenAI provided context, use it
        classification = "Critical"
        if ai_context:
             if 'severity' in ai_context:
                 classification = ai_context.get('severity', 'Critical')
             if 'explanation' in ai_context:
                 description = f"AI: {ai_context.get('explanation', '')[:100]}..."
        
        alert = {
            "id": f"sz-neural-{int(time.time()*1000)}",
            "timestamp": datetime.utcnow().isoformat(),
            "rule": {
                "level": severity_level,
                "description": description
            },
            "agent": {
                "name": "SecureZen-Node",
                "ip": source_ip
            },
            "full_log": original_log,
            "decoder": {"name": "neural-engine"},
            "data": {
                "classification": classification,
                "cluster_id": cluster_id,
                "vector_score": score
            }
        }
        
        # Store in DB
        self.storage.store_alert(alert)
        
        # Publish to Redis for Dashboard Real-time View
        try:
            import json
            # We reuse the buffer's redis connection if available
            if hasattr(self.buffer, 'client') and self.buffer.client:
                # Publish to 'neural_alerts' channel
                self.buffer.client.publish('neural_alerts', json.dumps(alert))
        except Exception as e:
            print(f"⚠️ Redis Publish Error: {e}")

        print(f"🚀 [NEURAL ALERT] Score: {score} | Cluster: {cluster_id} | Type: {description[:50]}...")

    def run_stream(self):
        """Starts the real-time processing loop."""
        print("="*50)
        print("🛡️  SecureZen Neural Engine: Active Monitoring")
        print(f"🔄 Consuming raw syslog from Redis: syslog:raw")
        print("="*50)
        
        batch = []
        last_source = None
        
        while True:
            # Fetch from Redis
            log_entry = self.buffer.pop_raw_log(timeout=1)
            if log_entry:
                raw_text = log_entry.get('raw_log', '')
                source_ip = log_entry.get('source_ip', 'unknown')
                
                # STAGE 1.5: Immediate Classification
                classification = self.classify_log(raw_text)
                
                # If Critical/Suspicious, add to analytical batch
                if classification in ["Critical", "Suspicious"]:
                    batch.append(raw_text)
                    last_source = source_ip
                
                # Batch processing for efficiency (every 5 logs or timeout)
                if len(batch) >= 5:
                    self.process_batch(batch, last_source)
                    batch = []
            elif batch:
                # Process remaining buffer on timeout
                self.process_batch(batch, last_source)
                batch = []

if __name__ == "__main__":
    engine = SecureZenNeuralEngine()
    try:
        engine.run_stream()
    except KeyboardInterrupt:
        print("\n🛑 SecureZen Neural Engine shutting down.")
