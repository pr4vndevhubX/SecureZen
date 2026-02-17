import time
import os
import sys
import logging
from datetime import datetime
import json

# Add app root to path for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
# siem_overlay/services/enrichment_service.py -> siem_overlay
app_root = os.path.dirname(current_dir)
if app_root not in sys.path:
    sys.path.insert(0, app_root)

# Import necessary components using absolute imports within app context
from utils.alert_storage import AlertStorage
from core.securezen.crew import IPIntelligenceCrew

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EnrichmentService")

def run_enrichment_service():
    logger.info("[START] Starting Threat Intel Enrichment Service...")
    
    try:
        storage = AlertStorage()
        crew = IPIntelligenceCrew()
    except Exception as e:
        logger.error(f"Failed to initialize service components: {e}")
        return
    
    while True:
        try:
            # 1. Get unprocessed alerts from database
            alerts = storage.get_unprocessed_alerts(limit=50)
            
            if not alerts:
                logger.debug("No new alerts found. Sleeping for 10 seconds...")
                time.sleep(10)
                continue
                
            logger.info(f"Processing {len(alerts)} new alerts for enrichment...")
            
            # 2. Extract unique IPs to minimize redundant API calls
            unique_ips = set()
            alert_ids = []
            
            for alert in alerts:
                # Extracts IPs from alert data
                # AlertStorage might have already extracted them into srcip/dstip top level fields
                # but we check the data dictionary too
                data = alert.get('data', {})
                srcip = alert.get('srcip') or data.get('srcip') or data.get('src_ip')
                dstip = alert.get('dstip') or data.get('dstip') or data.get('dst_ip')
                
                # Filter out private/local IPs
                for ip in [srcip, dstip]:
                    if ip and not ip.startswith(('127.', '10.', '192.168.', '172.16.', '169.254.')):
                        unique_ips.add(ip)
                
                alert_ids.append(alert.get('db_id'))
            
            # 3. Trigger enrichment for each unique IP found
            if unique_ips:
                logger.info(f"Triggering CrewAI enrichment for {len(unique_ips)} unique external IPs: {unique_ips}")
                for ip in unique_ips:
                    logger.info(f"Enriching IP: {ip}")
                    # Running sequentially to respect API rate limits and avoid LLM context flooding
                    success = crew.run_and_store(ip)
                    if success:
                        logger.info(f"Successfully enriched {ip}")
                    else:
                        logger.warning(f"Failed to enrich {ip}")
            
            # 4. Mark all processed alerts as such in the database
            if alert_ids:
                storage.mark_as_processed(alert_ids)
                logger.info(f"Marked {len(alert_ids)} alerts as processed.")
            
        except Exception as e:
            logger.error(f"Error in enrichment service loop: {e}")
            import traceback
            logger.error(traceback.format_exc())
            time.sleep(30) # Back off on error

if __name__ == "__main__":
    run_enrichment_service()
