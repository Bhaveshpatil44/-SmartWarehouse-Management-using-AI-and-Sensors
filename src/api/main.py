# --- Content for src/api/main.py ---
from fastapi import FastAPI

app = FastAPI(title="WORM Health API")

@app.get("/health", tags=["Status"])
def health_check():
    """
    Simple endpoint to check the API service status.
    """
    return {"status": "ok", "service": "WORM_API"}

# End of content
