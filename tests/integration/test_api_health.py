import pytest
import requests
import os

# Define the base URL for the FastAPI service.
# When run inside a Docker Compose environment, this should point to the 'api' service name.
# When run locally, this should point to the localhost port.
# We prioritize the Docker service name for CI/CD environments.

API_BASE_URL = os.environ.get("API_URL", "http://localhost:8000")

# Note: In a true integration test setup within Docker Compose, you would use 
# a tool like 'pytest-docker-compose' or rely on the networking setup. 
# For a simple file, we check the connection status first.

def test_api_health_endpoint():
    """
    Tests the fundamental /health endpoint to ensure the FastAPI service is running.
    """
    url = f"{API_BASE_URL}/health"
    
    try:
        # A short timeout is used to fail quickly if the service is down
        response = requests.get(url, timeout=2)
        
        # Check that the HTTP status code is 200 OK
        assert response.status_code == 200
        
        # Check the content type
        assert response.headers['Content-Type'] == 'application/json'
        
        # Check the JSON response content
        data = response.json()
        assert data['status'] == 'ok'
        assert data['service'] == 'WORM_API'

    except requests.exceptions.ConnectionError:
        pytest.fail(
            f"Failed to connect to the API service at {url}. "
            "Ensure the FastAPI service is running (e.g., via 'docker-compose up api')."
        )
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during API health check: {e}")
