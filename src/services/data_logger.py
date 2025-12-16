import time
import sqlite3
import redis
from pydantic import ValidationError

from src.config.settings import settings
from src.models.detection import DetectionEvent

# --- Initialization ---
DB_FILE = 'rat_detections.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            camera_id TEXT,
            sector TEXT,
            confidence REAL,
            rat_class TEXT,
            recent_24h INTEGER
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized for data logging.")

try:
    REDIS_CLIENT = redis.Redis(
        host=settings.REDIS_HOST, 
        port=settings.REDIS_PORT, 
        decode_responses=True
    )
    REDIS_CLIENT.ping()
    PUB_SUB = REDIS_CLIENT.pubsub()
    PUB_SUB.subscribe(settings.REDIS_CHANNEL)
    print(f"✅ Subscribed to Redis channel: {settings.REDIS_CHANNEL}")
except Exception as e:
    print(f"❌ Failed to connect to Redis for Data Logger: {e}")
    REDIS_CLIENT = None
    PUB_SUB = None 

# --- Core Logic ---

def log_event_to_db(event: DetectionEvent):
    """Inserts a processed DetectionEvent into the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO detections VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id,
            event.timestamp.isoformat(),
            event.camera_id,
            event.warehouse_sector,
            event.confidence,
            event.rat_class,
            event.recent_detections_24h
        ))
        conn.commit()
        print(f"💾 Logged event {event.event_id} to DB.")
    except sqlite3.Error as e:
        print(f"🛑 DB Write Error: {e}")
    finally:
        conn.close()


def run_data_logger():
    """Main loop for the Data Logger service."""
    init_db()
    if not REDIS_CLIENT or not PUB_SUB:
        return

    print("📊 Data Logger Service starting...")
    
    for message in PUB_SUB.listen():
        if message['type'] == 'message':
            try:
                event_data_json = message['data']
                event = DetectionEvent.model_validate_json(event_data_json)
                log_event_to_db(event)
                
            except (ValidationError, Exception) as e:
                print(f"🛑 Error in data logger loop: {e}")
        
        time.sleep(0.01)

if __name__ == '__main__':
    run_data_logger()
