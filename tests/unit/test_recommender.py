import pytest
import json
from pydantic import ValidationError
from src.models.detection import Recommendation, DetectionEvent
from datetime import datetime
from typing import List

# --- Mock Data for Testing ---

# 1. Mock data simulating a successful, correct LLM response
MOCK_GOOD_RESPONSE = {
    "summary": "Critical, high-frequency infestation detected near Sector 1 entrance.",
    "mitigation_priority": "Critical",
    "action_list": [
        "Deploy 5 bait stations immediately around the detected sector.",
        "Inspect perimeter seals for entry points.",
        "Activate ultrasonic repellers at 30-50 kHz for 60 minutes."
    ],
    "ultrasonic_activation_required": True,
    "ultrasonic_frequency_khz": "30-50 kHz"
}

# 2. Mock data simulating a failed/incorrect LLM response (Missing required field, wrong type)
MOCK_BAD_RESPONSE = {
    "summary": "Rat detected.",
    # Mitigation_priority is missing (required field)
    "action_list": "Check traps.", # This is a string, not List[str]
    "ultrasonic_activation_required": True,
}

# 3. Mock data for a Detection Event (used for a future integration test, but defined here)
MOCK_DETECTION_EVENT = DetectionEvent(
    event_id="test-1234",
    timestamp=datetime.utcnow(),
    camera_id="CAM-TEST",
    warehouse_sector="Sector 2 - Near Entry",
    confidence=0.95,
    rat_class="rat",
    bbox=[100, 200, 300, 400],
    recent_detections_24h=5,
    time_of_day_category="Night/Peak"
)

# --- Test Cases ---

def test_recommendation_model_validates_correct_output():
    """Test that a correctly structured LLM response is validated successfully."""
    try:
        recommendation = Recommendation.model_validate(MOCK_GOOD_RESPONSE)
        assert recommendation.summary.startswith("Critical")
        assert recommendation.mitigation_priority == "Critical"
        assert isinstance(recommendation.action_list, List)
        assert len(recommendation.action_list) >= 1
        assert recommendation.ultrasonic_activation_required is True
        assert recommendation.ultrasonic_frequency_khz == "30-50 kHz"
    except ValidationError as e:
        pytest.fail(f"Validation failed unexpectedly with valid data: {e}")

def test_recommendation_model_fails_on_missing_field():
    """Test that an LLM response missing a required field raises a ValidationError."""
    
    # Remove a required field ('mitigation_priority') from the dictionary clone
    bad_data = MOCK_GOOD_RESPONSE.copy()
    del bad_data['mitigation_priority']
    
    with pytest.raises(ValidationError) as excinfo:
        Recommendation.model_validate(bad_data)
    
    error_messages = str(excinfo.value)
    assert 'mitigation_priority' in error_messages

def test_recommendation_model_fails_on_incorrect_data_type():
    """Test that an LLM response with an incorrect data type raises a ValidationError."""
    
    # Use the prepared bad response (action_list is string, should be list)
    with pytest.raises(ValidationError) as excinfo:
        Recommendation.model_validate(MOCK_BAD_RESPONSE)
    
    error_messages = str(excinfo.value)
    # Check for the field that has the wrong type
    assert 'action_list' in error_messages
    # Check for the missing required field
    assert 'mitigation_priority' in error_messages



