from fastapi import FastAPI, HTTPException
from database import verify_access
import logging
import google.cloud.logging 
from google.cloud.logging.handlers import CloudLoggingHandler

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Google Cloud Logging
client = google.cloud.logging.Client()
handler = CloudLoggingHandler(client)
logger.addHandler(handler)

@app.post("/api/verify")
def verify(payload: dict):
    uid = payload.get("uid")
    door_id = payload.get("door_id")

    logger.info("POST from gateway | Data: %s", payload)

    allowed = verify_access(uid, door_id)

    return {"access": allowed}


