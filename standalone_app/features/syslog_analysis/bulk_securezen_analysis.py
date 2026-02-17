
import os
import sys
import glob
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from securezen_neural_pipeline import SecureZenNeuralEngine
from dataset_loader import SecureZenDatasetLoader

def process_single_file(file_path, engine):
    """
    Processes a single log file through the Neural Engine.
    Returns: (file_path, status, alert_count)
    """
    try:
        # Load data using the SecureZen loader
        # We use the internal loader logic which returns a LogRecordObject
        # But our engine expects raw logs or a pandas series.
        
        # Robustly read file, skipping binary/zip issues
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_logs = f.readlines()
        except Exception:
            # If basic read fails (e.g. permission or whatever), just fail this file
            return (file_path, "skipped (read_error)", 0)
            
        if not raw_logs:
            return (file_path, "skipped (empty)", 0)

        # Process in batches
        # We wrap this in another try/except to catch engine specific errors
        try:
           engine.process_batch(raw_logs, source_ip="dataset-import")
        except Exception as e:
           return (file_path, f"skipped (engine_error: {str(e)})", 0)
        
        return (file_path, "success", len(raw_logs))
        
    except Exception as e:
        return (file_path, f"error: {str(e)}", 0)

def main():
    # Pointing to the project root 'datasets' directory
    DATASETS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "datasets"))
    
    print("="*60)
    print("[START] SecureZen Neural Engine: Bulk Analysis Mode")
    print("="*60)
    
    if not os.path.exists(DATASETS_DIR):
        print(f"[ERR] Directory '{DATASETS_DIR}' not found. Please ensure datasets are present.")
        return

    # Find all .log files recursively
    log_files = []
    for root, dirs, files in os.walk(DATASETS_DIR):
        for file in files:
            if file.endswith(".log"):
                log_files.append(os.path.join(root, file))
                
    total_files = len(log_files)
    print(f"? Found {total_files} log files to process.")
    
    if total_files == 0:
        print("[WARN] No .log files found to analyze.")
        return

    # Initialize Engine
    engine = SecureZenNeuralEngine()
    
    print(f"\n? Starting Sequential Analysis (Thread-safe for Sqlite)...")
    
    success_count = 0
    error_count = 0
    total_processed_logs = 0
    start_time = time.time()
    
    # Processing Loop
    for i, file_path in enumerate(log_files):
        rel_path = os.path.relpath(file_path, DATASETS_DIR)
        print(f"[{i+1}/{total_files}] Analyzing: {rel_path}...", end="\r")
        
        path, status, count = process_single_file(file_path, engine)
        
        if status == "success":
            success_count += 1
            total_processed_logs += count
        else:
            print(f"\n[ERR] Failed {rel_path}: {status}")
            error_count += 1
            
    elapsed = time.time() - start_time
    
    print("\n" + "="*60)
    print("[STATS] Analysis Complete")
    print(f"   - Time Elapsed: {elapsed:.2f}s")
    print(f"   - Files Processed: {success_count}")
    print(f"   - Errors: {error_count}")
    print(f"   - Total Logs Analyzed: {total_processed_logs}")
    
    # Test GenAI Summarization
    if engine.llm_client:
        print("\n? Generating AI Summary of Alerts (Test Mock)...")
        # Creates dummy alerts to test the summarization capabilities
        dummy_alerts = [
            {"rule": {"description": "Failed password for root"}, "data": {"vector_score": 90}},
            {"rule": {"description": "Connection lost"}, "data": {"vector_score": 88}},
            {"rule": {"description": "Suspicious process spawned"}, "data": {"vector_score": 95}}
        ]
        summary = engine.generate_summary(dummy_alerts)
        if summary:
            print(f"\n? AI Analyst Summary:\n{summary}\n")
    
    print("="*60)

if __name__ == "__main__":
    main()
