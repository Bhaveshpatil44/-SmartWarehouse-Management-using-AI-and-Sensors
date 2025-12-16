import time
import redis
from twilio.rest import Client
from pydantic import ValidationError

from src.config.settings import settings
from src.models.detection import AlertMessage

# --- Initialization ---
try:
    TWILIO_CLIENT = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    print("✅ Twilio Client initialized.")
except Exception as e:
    print(f"❌ Twilio Client Initialization failed: {e}")
    TWILIO_CLIENT = None

try:
    REDIS_CLIENT = redis.Redis(
        host=settings.REDIS_HOST, 
        port=settings.REDIS_PORT, 
        decode_responses=True
    )
    REDIS_CLIENT.ping()
    PUB_SUB = REDIS_CLIENT.pubsub()
    PUB_SUB.subscribe(settings.REDIS_ALERT_CHANNEL) 
    print(f"✅ Subscribed to Redis channel: {settings.REDIS_ALERT_CHANNEL}")
except Exception as e:
    print(f"❌ Failed to connect to Redis for Alerter: {e}")
    REDIS_CLIENT = None
    PUB_SUB = None 

# --- Core Actions ---

def send_sms_alert(alert: AlertMessage):
    """Sends SMS using Twilio, incorporating LLM advice."""
    if not TWILIO_CLIENT:
        return

    body_message = (
        f"🚨 CRITICAL ALERT! Rat in {alert.event.warehouse_sector}.\n"
        f"Summary: {alert.recommendation.summary}\n"
        f"Priority: {alert.recommendation.mitigation_priority}\n"
        f"Action 1: {alert.recommendation.action_list[0]}"
    )
    
    try:
        message = TWILIO_CLIENT.messages.create(
            body=body_message,
            from_=settings.TWILIO_FROM_NUMBER,
            to=settings.TWILIO_TO_NUMBER
        )
        print(f"📞 SMS Alert sent successfully! SID: {message.sid}")
    except Exception as e:
        print(f"🛑 Twilio Error sending SMS: {e}")

def trigger_ultrasonic_module(alert: AlertMessage):
    """Simulates sending a command to the Ultrasonic Wave Transmission Module."""
    rec = alert.recommendation
    if rec.ultrasonic_activation_required:
        freq = rec.ultrasonic_frequency_khz or "Unknown"
        print(f"🔊 Ultrasonic Module Triggered!")
        print(f"   Action: Activate Repeller")
        print(f"   Frequency: {freq} (Targeted species control)")
    else:
        print("🔊 Ultrasonic Module not required for this event.")


def run_alerter_service():
    """Main loop for the Alerter service."""
    if not REDIS_CLIENT or not PUB_SUB:
        return

    print("🔔 Alerter Service starting...")
    
    for message in PUB_SUB.listen():
        if message['type'] == 'message':
            try:
                alert_data_json = message['data']
                alert = AlertMessage.model_validate_json(alert_data_json)
                print(f"🔔 Received FULL ALERT for event {alert.event.event_id}")

                send_sms_alert(alert)
                trigger_ultrasonic_module(alert)
                
            except (ValidationError, Exception) as e:
                print(f"🛑 Error in alerter loop: {e}")
        
        time.sleep(0.01)

if __name__ == '__main__':
    run_alerter_service()
