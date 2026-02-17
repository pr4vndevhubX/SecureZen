import os
import sys
import logging
from concurrent.futures import ThreadPoolExecutor

# Add the directory containing optimized_pipeline to sys.path
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
if PIPELINE_DIR not in sys.path:
    sys.path.append(PIPELINE_DIR)

from optimized_pipeline import run_pipeline

DATASETS_DIR = r"c:\Users\psuresh\OneDrive - KRYA SOLUTIONS PRIVATE LIMITED\Desktop\KYD\Agentic-ai-02\IP-alone-Crewai\ip-intel-crewai\datasets"

def find_all_logs(directory):
    log_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".log") or file.endswith(".txt"):
                log_files.append(os.path.join(root, file))
    return log_files

def process_file(file_path):
    print(f"\n>>> Processing: {file_path}")
    try:
        run_pipeline(file_path)
        print(f"<<< Finished: {file_path}")
    except Exception as e:
        print(f"!!! Error processing {file_path}: {e}")

def main():
    print("[START] Starting Batch Dataset Analysis...")
    log_files = find_all_logs(DATASETS_DIR)
    
    # Process files sequentially for now to avoid DB lock issues or resource exhaustion
    # But we can use ThreadPoolExecutor if needed for speed
    print(f"Found {len(log_files)} files to analyze.")
    
    # Selecting a subset or processing all depending on scale
    # To be safe and show results quickly, we'll process them one by one
    for file in log_files:
        process_file(file)
    
    print("\n[OK] All datasets processed and synced to SecureZen Dashboard.")

if __name__ == "__main__":
    main()
