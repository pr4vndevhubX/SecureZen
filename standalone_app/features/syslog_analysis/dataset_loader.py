import os
import sys
import requests
import pandas as pd

# Add local internal library to path
lib_path = os.path.join(os.path.dirname(__file__), "lib")
sys.path.append(lib_path)

# Importing internal data loader from lib
from logai.dataloader.data_loader import FileDataLoader, DataLoaderConfig

class SecureZenDatasetLoader:
    """
    Utility to fetch Threat Data from GitHub and load it into SecureZen Neural Engine format.
    """
    
    BASE_RAW_URL = "https://raw.githubusercontent.com/splunk/attack_data/master/"
    
    def __init__(self, local_data_dir="data"):
        self.local_data_dir = local_data_dir
        os.makedirs(self.local_data_dir, exist_ok=True)

    def fetch_dataset(self, relative_path: str):
        """Downloads a dataset to local storage."""
        url = self.BASE_RAW_URL + relative_path
        local_path = os.path.join(self.local_data_dir, os.path.basename(relative_path))
        
        print(f"📥 Fetching dataset from: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Saved to: {local_path}")
                return local_path
            else:
                print(f"❌ Failed to fetch dataset: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return None

    def load_for_neural_engine(self, file_path: str, log_format: str = None):
        """Loads a local file for SecureZen Neural Engine processing."""
        if not log_format:
            # Default Linux Syslog format (RFC3164)
            log_format = "<month> <day> <time> <hostname> <component>:<body1>"
            
        config = DataLoaderConfig(
            filepath=file_path,
            log_type="log",
            reader_args={"log_format": log_format}
        )
        loader = FileDataLoader(config)
        return loader.load_data()

if __name__ == "__main__":
    loader = SecureZenDatasetLoader()
    # Test with a local known file if needed
