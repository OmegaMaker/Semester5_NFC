from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import logging
import google.cloud.logging 
from google.cloud.logging.handlers import CloudLoggingHandler

from database import (
    fetch_all_cards,
    upsert_card,
    delete_card,
    fetch_all_doors_with_levels,
    upsert_door,
    delete_door,
)

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Google Cloud Logging
client = google.cloud.logging.Client()
handler = CloudLoggingHandler(client)
logger.addHandler(handler)

# ----------------- ADMIN: CARDS -----------------
@app.get("/api/cards")
def api_get_cards():
    return {"cards": fetch_all_cards()}


@app.post("/api/cards/save")
def api_save_card(payload: dict):
    uid = (payload.get("uid") or "").strip()
    owner_name = (payload.get("owner_name") or "").strip() or None
    access_level_raw = (payload.get("access_level") or "").strip()
    valid_from = (payload.get("valid_from") or "").strip() or None
    valid_to = (payload.get("valid_to") or "").strip() or None
    extra_doors_raw = (payload.get("extra_doors") or "").strip()

    if not uid:
        raise HTTPException(status_code=400, detail="Missing uid")

    access_level = None
    if access_level_raw:
        try:
            access_level = int(access_level_raw)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="access_level must be an integer",
            )

    # "d-4.0,d-2.1" -> ["d-4.0", "d-2.1"]
    extra_door_access = [
        d.strip() for d in extra_doors_raw.split(",") if d.strip()
    ]
    if not extra_door_access:
        extra_door_access = None

    upsert_card(
        uid=uid,
        owner_name=owner_name,
        access_level=access_level,
        valid_from=valid_from,
        valid_to=valid_to,
        extra_door_access=extra_door_access,
    )
    logger.info("Admin: Card updated | Data: %s, %s, %s, %s, %s, %s", uid, owner_name, access_level, valid_from, valid_to, extra_door_access)
    return {"status": "ok"}


@app.delete("/api/cards/{uid}")
def api_delete_card(uid: str):
    delete_card(uid)
    logger.info("Admin: %s deleted", uid)
    return {"status": "deleted"}


# ----------------- ADMIN: DOORS -----------------

@app.get("/api/doors")
def api_get_doors():
    return {"doors": fetch_all_doors_with_levels()}


@app.post("/api/doors/save")
def api_save_door(payload: dict):
    door_id = (payload.get("door_id") or "").strip()
    name = (payload.get("name") or "").strip() or None
    access_levels_raw = (payload.get("access_levels") or "").strip()

    if not door_id:
        raise HTTPException(status_code=400, detail="Missing door_id")

    access_levels: list[int] = []
    if access_levels_raw:
        for part in access_levels_raw.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                access_levels.append(int(part))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="access_levels must be a comma-separated list of integers",
                )

    upsert_door(door_id=door_id, name=name, access_levels=access_levels)
    logger.info("Admin: Door updated | Data: %s, %s, %s", door_id, name, access_levels)
    return {"status": "ok"}


@app.delete("/api/doors/{door_id}")
def api_delete_door(door_id: str):
    delete_door(door_id)
    logger.info("Admin: Door %s deleted", door_id)
    return {"status": "deleted"}

# ----------------- ADMIN HTML -----------------

@app.get("/", response_class=HTMLResponse)
def admin_page():
    html_path = Path(__file__).with_name("admin.html")
    if not html_path.exists():
        raise HTTPException(status_code=500, detail="admin.html not found")
    logger.info("Admin: Page loaded")
    return html_path.read_text(encoding="utf-8")