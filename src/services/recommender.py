import time
import json
import redis
from openai import OpenAI
from pydantic import ValidationError

from src.config.settings import settings
from src.models.detection import DetectionEvent, Recommendation, AlertMessage

# --- Initialization ---
try:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
    LLM_CLIENT = OpenAI(api_key=settings.OPENAI_API_KEY)
    LLM_MODEL = "gpt-4-turbo-preview"
    print(f"✅ LLM Client initialized with model: {LLM_MODEL}")
except Exception as e:
    print(f"❌ LLM Client Initialization failed: {e}")
    LLM_CLIENT = None

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
    print(f"❌ Failed to connect to Redis for Recommender: {e}")
    REDIS_CLIENT = None
    PUB_SUB = None 


# --- LLM Prompt Definition ---

SYSTEM_PROMPT = """
You are a highly specialized AI Pest Mitigation Expert for large industrial warehouses. 
Your role is to analyze real-time rat detection data and generate actionable, critical mitigation recommendations.

Your response MUST be a valid JSON object that strictly adheres to the provided JSON Schema. 
Do not include any surrounding text, markdown, or commentary outside of the JSON object.
Context for Rat Species Frequencies:
- Rattus rattus (Roof Rat): 20-40 kHz
- Bandicota bengalensis (Indian Bandicoot): 30-50 kHz
"""

def generate_recommendation(event: DetectionEvent) -> Recommendation | None:
    """Calls the LLM with structured output to generate mitigation advice."""
    if not LLM_CLIENT:
        return None

    user_prompt = f"""
    A new rat detection event has occurred. Analyze the context and provide immediate, tailored mitigation advice.
    
    Detection Event Details:
    - Timestamp: {event.timestamp}
    - Location: {event.warehouse_sector}
    - Recent Detections (Last 24h in this sector): {event.recent_detections_24h}
    - Time of Day Category: {event.time_of_day_category}
    - Detected Species (Assume): Bandicota bengalensis (Indian Bandicoot) 
      
    Instructions:
    1. Determine the 'mitigation_priority' based on location and frequency.
    2. Provide at least three concrete, actionable 'action_list' items.
    3. Set 'ultrasonic_activation_required' to True if activation is appropriate.
    4. Set 'ultrasonic_frequency_khz' based on the 'Indian Bandicoot' frequency range: 30-50 kHz.
    """

    try:
        response = LLM_CLIENT.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} 
        )
        
        llm_output = json.loads(response.choices[0].message.content)
        recommendation_model = Recommendation.model_validate(llm_output)
        print(f"🧠 Recommendation Generated: Priority {recommendation_model.mitigation_priority}")
        return recommendation_model
    
    except (ValidationError, Exception) as e:
        print(f"🛑 Error processing LLM response: {e}")
        return None


def run_recommender_service():
    """The main loop for the Recommender service."""
    if not REDIS_CLIENT or not PUB_SUB:
        return

    print("🧠 Recommender Service starting...")
    
    for message in PUB_SUB.listen():
        if message['type'] == 'message':
            try:
                event_data_json = message['data']
                event = DetectionEvent.model_validate_json(event_data_json)
                print(f"👂 Consumed Event {event.event_id}")

                recommendation = generate_recommendation(event)

                if recommendation:
                    alert_message = AlertMessage(
                        event=event,
                        recommendation=recommendation
                    )

                    message_to_publish = alert_message.model_dump_json()
                    REDIS_CLIENT.publish(settings.REDIS_ALERT_CHANNEL, message_to_publish)
                    print(f"📢 Published Full Alert to {settings.REDIS_ALERT_CHANNEL}")
                
            except (ValidationError, Exception) as e:
                print(f"🛑 Error in recommender loop: {e}")
        
        time.sleep(0.01)

if __name__ == '__main__':
    run_recommender_service()
