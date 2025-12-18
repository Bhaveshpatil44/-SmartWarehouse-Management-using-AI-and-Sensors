# 🐀 Warehouse Rat Monitoring and Mitigation System (WORM)

A production-ready, AI-driven platform that scales real-time rat detection into actionable mitigation recommendations and persistence logging.

## 🚀 Goal
[cite_start]To transition from a simple local detection script sending SMS alerts [cite: 1] [cite_start]to a decoupled, scalable microservice architecture that provides real-time AI suggestions, data logging (Parameter Analysis) [cite: 1][cite_start], and automatic hardware activation (Ultrasonic Module).

## 💻 Tech Stack Highlights
* **Backend Services:** Python, FastAPI (for APIs and workers)
* **Asynchronous Communication:** Redis Pub/Sub
* **Computer Vision:** Roboflow Inference Client, OpenCV
* **Artificial Intelligence:** LLM (OpenAI/Gemini) for structured recommendations
* **Alerting:** Twilio (SMS)
* **Infrastructure:** Docker, Docker Compose, PostgreSQL
* **CI/CD:** GitHub Actions

## 📐 Architecture
The system is built as a set of decoupled services communicating via a message queue (Redis). See [docs/architecture.md](docs/architecture.md) for a full diagram and detailed flow.

## 💾 Setup and Installation

### Prerequisites
1.  Docker and Docker Compose
2.  Python 3.11+
3.  Valid API keys (Twilio, Roboflow, OpenAI/Gemini, Ollama  fro Local Use)

### 1. Configure Environment
Copy and populate the environment variables:
```bash
cp .env.example .env
