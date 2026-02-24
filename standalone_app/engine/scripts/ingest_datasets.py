import os
import sys
import glob

# Ensure we can import from the features directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# features/syslog_analysis -> standalone_app
app_root = os.path.dirname(os.path.dirname(current_dir))
if app_root not in sys.path:
    sys.path.insert(0, app_root)

from engine.core.analysis_pipeline import run_pipeline

# Ensure LogAI core is in path for subprocess execution if needed
engine_dir = os.path.dirname(current_dir)
logai_path = os.path.join(engine_dir, "logai")
if logai_path not in sys.path:
    # We add the PARENT of logai to sys.path so 'import logai' works
    sys.path.append(engine_dir)

# Make DATASETS_DIR relative to this script's location:
# scripts/ -> engine/ -> engine/datasets/
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_engine_dir = os.path.dirname(_scripts_dir)
DATASETS_DIR = os.path.join(_engine_dir, "datasets")

def ingest_all():
    print(f"Scanning for log files in {DATASETS_DIR}...")
    
    # Extensions to look for
    extensions = ['*.log', '*.txt']
    files = []
    
    for ext in extensions:
        # Recursive search
        found = glob.glob(os.path.join(DATASETS_DIR, '**', ext), recursive=True)
        files.extend(found)
    
    print(f"Found {len(files)} log files. Starting Optimized ML Analysis...")
    
    # Run the pipeline directly in-memory
    # This avoids the overhead of reloading LogAI/ML libraries for every batch
    try:
        run_pipeline(files)
        print("\nIngestion and ML Analysis Completed Successfully.")
    except Exception as e:
        print(f"FAILED to process logs: {e}")

if __name__ == "__main__":
    ingest_all()
