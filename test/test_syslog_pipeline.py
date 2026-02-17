import socket
import time
import sys
import os

def send_test_syslog(message, port=5140):
    """Sends a raw UDP packet to the local syslog listener"""
    # Standard Syslog format: <PRI>TIMESTAMP HOSTNAME APP: MESSAGE
    timestamp = time.strftime("%b %d %H:%M:%S")
    formatted_msg = f"<34>{timestamp} test-server-01 test-app: {message}"
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(formatted_msg.encode('utf-8'), ("127.0.0.1", port))
        print(f"[SIGNAL] Sent raw log to portal {port}: {formatted_msg}")
    finally:
        sock.close()

if __name__ == "__main__":
    print("[START] Starting Syslog Pipeline Test Simulation")
    
    # Test 1: A "Noise" log (should be filtered out)
    print("\n--- Test 1: Normal System Noise ---")
    send_test_syslog("Health check: Service 'cron' is running normally.")
    
    # Test 2: A "Medium" threat (might get stored)
    print("\n--- Test 2: Medium Threat ---")
    send_test_syslog("Unauthorized access attempt on /etc/config/settings.conf")
    
    # Test 3: A "Critical" threat (should definitely be stored and score high)
    print("\n--- Test 3: Critical Threat ---")
    send_test_syslog("CRITICAL: SQL Injection exploit detected from source IP 192.168.1.100")
    
    print("\n[OK] Simulation complete.")
    print("? Check the output of 'services/syslog_preprocessor.py' to see the logs being analyzed!")
