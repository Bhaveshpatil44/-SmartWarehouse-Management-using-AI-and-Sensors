from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

# --- 1. Event from Video Processor to Redis ---

class DetectionEvent(BaseModel):
    """
    Structured data for a single rat detection event published to Redis.
    This replaces the simple 'rat detected' flag.
    """
    event_id: str = Field(..., description="Unique ID for this detection event.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of detection (UTC).")
    camera_id: str = Field(..., description="ID of the camera/sensor that made the detection.")
    warehouse_sector: str = Field(..., description="Specific location of the detection (e.g., Sector 1, near storage).")
    
    # Rat Parameters (for Parameter Analysis Module)
    confidence: float = Field(..., description="Confidence score of the ML model.")
    rat_class: str = Field(default="rat", description="Class of object detected.")
    
    # Bounding Box (Normalized 0-1000 or actual pixel values)
    bbox: List[int] = Field(..., description="[x1, y1, x2, y2] bounding box coordinates.")
    
    # Contextual Data (in a real system, this would come from the Data Logger)
    # For now, we simulate this input for the LLM.
    recent_detections_24h: int = Field(default=0, description="Count of detections in the past 24 hours in this sector.")
    time_of_day_category: str = Field(default="Night/Off-Hours", description="E.g., Day, Night, Peak-Activity.")


# --- 2. Structured Output from LLM Recommendation Service ---

class Recommendation(BaseModel):
    """
    Structured data for the LLM-generated recommendation.
    """
    summary: str = Field(..., description="A short summary of the infestation situation and risk level.")
    mitigation_priority: str = Field(..., description="Priority level: Low, Medium, High, or Critical.")
    action_list: List[str] = Field(..., description="A numbered list of specific, actionable steps.")
    ultrasonic_activation_required: bool = Field(default=False, description="Whether the Ultrasonic Wave Transmission Module should be activated.")
    [cite_start]ultrasonic_frequency_khz: Optional[str] = Field(None, description="Recommended frequency range (e.g., '30 kHz – 50 kHz') based on documented species[cite: 2].")

# --- 3. Full Recommendation Message (Alert Service Input) ---

class AlertMessage(BaseModel):
    """
    The final message package sent to the Alerter service.
    """
    event: DetectionEvent
    recommendation: Recommendation
    message_type: str = "FULL_ALERT"