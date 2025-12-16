import cv2
import time
import uuid
import redis
from inference_sdk import InferenceHTTPClient
from src.config.settings import settings
from src.models.detection import DetectionEvent

# --- Initialization ---
try:
    REDIS_CLIENT = redis.Redis(
        host=settings.REDIS_HOST, 
        port=settings.REDIS_PORT, 
        decode_responses=True
    )
    REDIS_CLIENT.ping()
    print("✅ Successfully connected to Redis.")
except Exception as e:
    print(f"❌ Failed to connect to Redis: {e}")
    REDIS_CLIENT = None 

# Initialize Roboflow Inference Client
ROBOFLOW_CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=settings.ROBOFLOW_API_KEY
)

# --- Core Logic ---

def publish_detection_event(event: DetectionEvent):
    """Publishes the structured detection event to the Redis message channel."""
    if REDIS_CLIENT:
        try:
            message = event.model_dump_json()
            REDIS_CLIENT.publish(settings.REDIS_CHANNEL, message)
            print(f"📡 Published event {event.event_id} to {settings.REDIS_CHANNEL}")
        except Exception as e:
            print(f"🛑 Error publishing to Redis: {e}")
    else:
        print("🛑 Redis client not available. Event not published.")


def run_video_processor():
    """The main loop that captures frames, runs inference, and publishes events."""
    # Open webcam/stream (0 for default camera, or a network RTSP stream)
    cap = cv2.VideoCapture(0) 
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    print("🎥 Video Processor starting...")
    prev_time = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to grab frame or stream ended.")
                time.sleep(1)
                continue

            # 1. Run Inference
            predictions = ROBOFLOW_CLIENT.infer(
                frame, 
                model_id=settings.ROBOFLOW_MODEL_ID, 
                confidence=0.25
            )
            
            rat_detections = [p for p in predictions.get("predictions", []) if p["class"].lower() == "rat"]

            # 2. Process Detections
            if rat_detections:
                print(f"🚨 Rat detected! Processing {len(rat_detections)} instances.")
                
                # We focus on the first detected rat for event creation
                first_detection = rat_detections[0]
                
                x, y = first_detection["x"], first_detection["y"]
                w, h = first_detection["width"], first_detection["height"]
                x1, y1 = int(x - w/2), int(y - h/2)
                x2, y2 = int(x + w/2), int(y + h/2)
                
                event_data = DetectionEvent(
                    event_id=str(uuid.uuid4()),
                    camera_id="CAM_A_SECTOR_1",
                    warehouse_sector="Sector 1 - Near Food Storage",
                    confidence=first_detection["confidence"],
                    rat_class=first_detection["class"].lower(),
                    bbox=[x1, y1, x2, y2],
                    recent_detections_24h=0, 
                    time_of_day_category="Night/Off-Hours"
                )

                # 3. Publish Event
                publish_detection_event(event_data)

            # Show FPS / Loop delay
            curr_time = time.time()
            prev_time = curr_time
            time.sleep(0.1)

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Video Processor shut down.")


if __name__ == '__main__':
    run_video_processor()
