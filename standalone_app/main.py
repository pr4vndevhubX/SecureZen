import uvicorn
import os
import sys

# Ensure project root is in path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the standalone app
from core.securezen.syslog.server import app

if __name__ == "__main__":
    print("🚀 [SecureZen] Starting Standalone Syslog Mode...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
