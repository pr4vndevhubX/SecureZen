import socket
import sys
import os
from datetime import datetime

# Add project root to path for imports
# Path: features/syslog_analysis/syslog_listener.py -> project_root is 2 levels up
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.syslog_buffer import SyslogBuffer

def start_syslog_listener(host="0.0.0.0", port=514):
    """
    Starts a UDP Syslog Server to capture raw logs.
    This is Layer 1 of the architecture.
    """
    buffer = SyslogBuffer()
    
    # Create UDP socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        print("="*50)
        print(f"🚀 SecureZen Syslog Listener Started")
        print(f"📡 Listening on: {host}:{port} (UDP)")
        print(f"📦 Buffering to: Redis ({buffer.queue_name})")
        print("="*50)
    except Exception as e:
        print(f"❌ Failed to bind to port {port}: {e}")
        print("💡 TIP: You might need administrator/root privileges to bind to port 514.")
        return

    try:
        while True:
            # 1. Receive raw data from network
            data, addr = sock.recvfrom(4096) # Standard syslog size limit is 1024-4096
            raw_msg = data.decode('utf-8', errors='ignore').strip()
            
            if not raw_msg:
                continue
                
            # 2. Extract source IP from the packet
            sender_ip = addr[0]
            
            # 3. Push to Redis (The 'Shock Absorber' step)
            success = buffer.push_raw_log(raw_msg, source_ip=sender_ip)
            
            if success:
                print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] Log received from {sender_ip} -> Redis")
            else:
                print(f"⚠️ Failed to buffer log from {sender_ip}")

    except KeyboardInterrupt:
        print("\n🛑 Syslog listener stopped by user.")
    finally:
        sock.close()

if __name__ == "__main__":
    # In production, you might use 514. 
    # For testing, we can use 5140 to avoid permission issues.
    PORT = int(os.getenv("SYSLOG_PORT", 5140))
    start_syslog_listener(port=PORT)
