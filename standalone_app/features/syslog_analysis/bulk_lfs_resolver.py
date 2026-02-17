import os
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

class LFSResolver:
    """
    Automates the resolution of Git LFS pointers in the datasets directory.
    Replaces pointer files with actual content from Splunk Attack Data GitHub.
    Uses ThreadPoolExecutor for parallel processing.
    """
    
    BASE_RAW_URL = "https://raw.githubusercontent.com/splunk/attack_data/master/"
    
    def __init__(self, target_dir, max_workers=10):
        self.target_dir = target_dir
        self.max_workers = max_workers
        self.resolved_count = 0
        self.failed_count = 0

    def is_lfs_pointer(self, file_path):
        """Check if a file is a Git LFS pointer based on size and content."""
        if os.path.getsize(file_path) > 1000:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(500)
                return "version https://git-lfs.github.com/spec/v1" in content
        except Exception:
            return False

    def resolve_file(self, file_path):
        """Standardizes the path and downloads from the raw GitHub master branch."""
        parts = file_path.replace("\\", "/").split("/")
        try:
            # Look for 'datasets' in the path to build the relative GitHub URL
            datasets_index = -1
            for i, part in enumerate(parts):
                if part == "datasets":
                    datasets_index = i
                    break
            
            if datasets_index == -1:
                return False

            relative_path = "/".join(parts[datasets_index:]) 
        except Exception:
            return False

        url = self.BASE_RAW_URL + relative_path
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True, file_path
            else:
                return False, file_path
        except Exception as e:
            return False, file_path

    def run(self):
        """Recursively scan and resolve all LFS pointers concurrently."""
        print(f"[SEARCH] Scanning for LFS pointers in: {self.target_dir}")
        
        pointers = []
        for root, dirs, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith(".log") or file.endswith(".xml") or file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    if self.is_lfs_pointer(file_path):
                        pointers.append(file_path)
        
        total_pointers = len(pointers)
        if total_pointers == 0:
            print("? No LFS pointers found.")
            return

        print(f"[START] Found {total_pointers} pointers. Starting parallel download with {self.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(self.resolve_file, fp): fp for fp in pointers}
            
            completed = 0
            for future in as_completed(future_to_file):
                success, path = future.result()
                completed += 1
                if success:
                    self.resolved_count += 1
                    print(f"[{completed}/{total_pointers}] [OK] Resolved: {os.path.basename(path)}")
                else:
                    self.failed_count += 1
                    print(f"[{completed}/{total_pointers}] [ERR] Failed: {os.path.basename(path)}")
        
        print("\n" + "="*50)
        print(f"? LFS Resolution Complete")
        print(f"[OK] Resolved: {self.resolved_count}")
        print(f"[ERR] Failed: {self.failed_count}")
        print("="*50)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Try multiple possible dataset locations
    possible_roots = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))), "datasets"),
        os.path.join(script_dir, "datasets"),
        os.path.join(os.getcwd(), "datasets")
    ]
    
    target = next((p for p in possible_roots if os.path.exists(p)), None)
    
    if target:
        resolver = LFSResolver(target, max_workers=50)
        resolver.run()
    else:
        print(f"[ERR] Target datasets directory not found. Checked: {possible_roots}")
