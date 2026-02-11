import redis
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SyslogBuffer:
    """
    Utility to handle high-speed raw syslog ingestion into Redis.
    Acts as the 'Shock Absorber' for the SecureZen pipeline.
    """
    
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.queue_name = "securezen_raw_syslog"
        
        # Initialize connection
        try:
            self.client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                db=self.redis_db,
                decode_responses=True
            )
            print(f"📡 Redis connected to {self.redis_host}:{self.redis_port}")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.client = None

    def push_raw_log(self, raw_data: str, source_ip: str = "unknown"):
        """
        Pushes a raw log string into the Redis list.
        Uses LPUSH (Left Push) for FIFO/LIFO flexibility.
        """
        if not self.client:
            return False
            
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "source_ip": source_ip,
            "raw_log": raw_data
        }
        
        try:
            # We use LPUSH to push into the 'queue_name' list
            self.client.lpush(self.queue_name, json.dumps(log_entry))
            return True
        except Exception as e:
            print(f"❌ Error pushing to Redis: {e}")
            return False

    def pop_raw_log(self, timeout=0):
        """
        Pops a log from the queue (Blocking).
        Used by the Pre-Processing layer to consume logs.
        """
        if not self.client:
            return None
            
        # BRPOP (Blocking Right Pop) waits until an item is available
        result = self.client.brpop(self.queue_name, timeout=timeout)
        if result:
            return json.loads(result[1])
        return None

    def get_queue_size(self):
        """Checks how many logs are currently waiting in the buffer."""
        if not self.client:
            return 0
        return self.client.llen(self.queue_name)
