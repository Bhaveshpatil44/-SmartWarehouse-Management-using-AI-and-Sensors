# 🐀 System Architecture: Warehouse Rat Monitoring and Mitigation

This system uses a decoupled microservice architecture to scale from simple detection to a real-time recommendation engine. Communication between all services is asynchronous via a Redis Message Broker (Pub/Sub).

## Flow of Data

1.  **Ingestion:** The **Video Processor** captures video, runs inference, and publishes a raw `DetectionEvent` to the `rat_detections` channel.
2.  [cite_start]**Analysis (Logging):** The **Data Logger** subscribes to `rat_detections` and stores the event parameters in the PostgreSQL database for historical "Parameter Analysis".
3.  **Intelligence:** The **Recommender** subscribes to `rat_detections`, uses the LLM to generate structured mitigation advice (`Recommendation`), and publishes the enriched `AlertMessage` to the `full_alerts` channel.
4.  **Action & Notification:** The **Alerter** subscribes to `full_alerts` and triggers the final actions:
    * [cite_start]Sends a prioritized SMS/Mobile Alert via Twilio.
    * [cite_start]Activates the conceptual **Ultrasonic Wave Transmission Module** at the LLM-recommended frequency (e.g., 30-50 kHz for Indian Bandicoot ).

## Component Table

| Service | Primary Technology | Input Channel | Output Channel |
| :--- | :--- | :--- | :--- |
| **Video Processor** | Python, OpenCV, Roboflow | N/A (Camera Stream) | `rat_detections` |
| **Data Logger** | Python, PostgreSQL/SQLAlchemy | `rat_detections` | N/A (Database Write) |
| **Recommender** | Python, FastAPI, LLM (OpenAI/Gemini) | `rat_detections` | `full_alerts` |
| **Alerter** | Python, Twilio, FastAPI | `full_alerts` | N/A (External Action) |
| **Infrastructure** | Redis, PostgreSQL | N/A | N/A |
