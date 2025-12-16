Markdown# 💻 WORM System API Documentation

The Warehouse Rat Monitoring (WORM) system's external interface is built using FastAPI. While most of the core business logic (detection, logging, recommendation) runs via asynchronous worker services, the API is essential for **health checks**, **external communication**, and **future application integration** (e.g., a mobile dashboard).

### **Base URL**
The API service is accessible via the `api` service in the Docker network.
* **Local Development:** `http://localhost:8000`
* **Within Docker Network:** `http://api:8000`

---

## 1. Health Check Endpoint

This endpoint is crucial for container orchestration tools (like Kubernetes or Docker Compose's healthcheck feature) to determine the application's operational status.

### **Endpoint**
`GET /health`

| Parameter | Type | Description |
| :--- | :--- | :--- |
| None | N/A | Checks service readiness. |

### **Example Response (200 OK)**

```json
{
  "status": "ok",
  "service": "WORM_API"
}
2. Status Endpoint (Future Extension)This endpoint provides a snapshot of the worker services' connectivity status (e.g., confirming Redis and Database are reachable). This would be critical for dashboard development.EndpointGET /status/infrastructureParameterTypeDescriptionNoneN/AChecks connectivity to infrastructure components (Redis, PostgreSQL).Example Response (200 OK)JSON{
  "api_status": "ok",
  "redis_connection": "connected",
  "database_connection": "connected",
  "last_event_published_at": "2025-12-16T15:30:00Z" 
}
3. Webhook Endpoint (Future Extension - Ultrasonic Trigger)In a real deployment, the Alerter Service would communicate with a hardware control API to activate the Ultrasonic Repeller. This conceptual endpoint simulates that interface.EndpointPOST /action/ultrasonicParameterTypeDescriptionfrequency_khzstringThe recommended frequency (e.g., "30-50 kHz") from the LLM.duration_sintegerDuration of activation in seconds (e.g., 1800 for 30 minutes).Request Body ExampleJSON{
  "frequency_khz": "30-50 kHz",
  "duration_s": 1800,
  "sector_id": "Sector 1"
}
Example Response (202 Accepted)JSON{
  "message": "Ultrasonic module activation command accepted and queuing for hardware control.",
  "status": "queued"
}
