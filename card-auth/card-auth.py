from fastapi import FastAPI, HTTPException
from database import verify_access

app = FastAPI()

@app.post("/api/verify")
def verify(payload: dict):
    uid = payload.get("uid")
    door_id = payload.get("door_id")

    allowed = verify_access(uid, door_id)

    return {"access": allowed}


