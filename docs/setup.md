## ⚙️ Project Setup Guide: WORM System

This guide provides detailed instructions for setting up, configuring, and running the WORM (Warehouse Rat Monitoring) system using Docker and Docker Compose.

### 1. Prerequisites

Ensure the following tools are installed on your development machine:

* **Git:** For version control.
* **Docker:** Version 20.10+ (Includes Docker Engine and Docker CLI).
* **Docker Compose:** Version 1.29+ or Docker Compose V2 (bundled with Docker Desktop).
* **API Keys:** Valid keys for **Twilio**, **Roboflow**, and **OpenAI/LLM** provider.

### 2. Environment Configuration

The entire system relies on environment variables defined in the `.env` file for secure credential management.

1.  **Copy the Example File:**
    ```bash
    cp .env.example .env
    ```

2.  **Edit `.env`:**
    Open the newly created `.env` file and replace all placeholder values (`XXXXXXXXXXXXXXXX`) with your actual credentials and settings. **Crucially, ensure you set your correct database and Redis connection details if deviating from defaults.**

### 3. Running the Stack (Recommended)

The `docker-compose.yml` file defines the full microservice architecture, including the necessary infrastructure (Redis and PostgreSQL).

1.  **Build and Run:** Use the following command to build the Python application image, create the necessary containers, and start the entire system in detached mode (`-d`).

    ```bash
    docker-compose up --build -d
    ```

2.  **Verify Service Status:** Check that all containers are running:

    ```bash
    docker-compose ps
    ```
    You should see `video_processor`, `recommender`, `data_logger`, `alerter`, `redis`, and `postgres` all in the `Up` state.

### 4. Viewing Logs

To debug or monitor the real-time data flow, view the logs for a specific service:

* **View Detection Events:**
    ```bash
    docker-compose logs -f video_processor
    ```

* **View Recommendation Logic:**
    ```bash
    docker-compose logs -f recommender
    ```

* **View All Service Logs:**
    ```bash
    docker-compose logs -f
    ```

### 5. Running Locally (Alternative for Debugging)

If you need to run an individual service locally outside of Docker (e.g., to step through code with a debugger), you can use the `manage.py` script.

1.  **Install Dependencies:** (Assumes Python is installed)
    ```bash
    pip install -r requirements/base.txt -r requirements/dev.txt
    ```

2.  **Ensure Infrastructure is Running:** Start Redis and PostgreSQL using Docker Compose, but exclude the app services:
    ```bash
    docker-compose up -d redis postgres
    ```

3.  **Run Service Locally:**
    ```bash
    # Run the Recommender service locally
    python manage.py start recommender
    
    # Run the Data Logger service locally
    python manage.py start data_logger
    ```

### 6. Shutdown

To stop and remove all running containers defined in the `docker-compose.yml` file:

```bash
docker-compose down
