import sys
from crew import IPIntelligenceCrew

def test_investigation(ip="8.8.8.8"):
    print(f"\n[SEARCH] Testing IP Intelligence Crew with IP: {ip}")
    print("="*60)
    
    try:
        # Initialize Crew
        crew_instance = IPIntelligenceCrew()
        crew = crew_instance.crew()
        
        # Define inputs
        inputs = {'ip_addresses': ip}
        
        # Run
        print("[START] Kickoff... (This might take a minute)")
        result = crew.kickoff(inputs=inputs)
        
        print("\n" + "="*60)
        print("[OK] ANALYSIS RESULT:")
        print("="*60)
        print(result)
        print("="*60)
        
    except Exception as e:
        print(f"[ERR] Error: {e}")

if __name__ == "__main__":
    target_ip = sys.argv[1] if len(sys.argv) > 1 else "8.8.8.8"
    test_investigation(target_ip)
