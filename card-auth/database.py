from sqlalchemy import create_engine, text
from datetime import datetime

DB_USER = "postgres"
DB_PASSWORD = "Database123!"
DB_HOST = "34.51.245.141"
DB_NAME = "card_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
)

# --------------------------------------------------
# FETCH CARD
# --------------------------------------------------

def fetch_card(uid: str):
    query = text("""
        SELECT uid, access_level, valid_from, valid_to, extra_door_access
        FROM cards
        WHERE uid = :uid
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"uid": uid}).fetchone()
        return dict(result._mapping) if result else None

# --------------------------------------------------
# FETCH WHICH DOORS BELONG TO AN ACCESS LEVEL
# --------------------------------------------------

def fetch_doors_for_access_level(level: int):
    query = text("""
        SELECT door_id
        FROM access_level_doors
        WHERE access_level = :lvl
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"lvl": level}).fetchall()
        return [row[0] for row in result]

# --------------------------------------------------
# MAIN VERIFICATION LOGIC
# --------------------------------------------------

def verify_access(uid: str, door_id: str) -> bool:
    card = fetch_card(uid)
    if card is None:
        return False

    # ------------------------
    # VALIDITY CHECK
    # ------------------------
    now = datetime.utcnow()

    valid_from = card["valid_from"]
    valid_to = card["valid_to"]

    if valid_from and now < valid_from:
        return False
    if valid_to and now > valid_to:
        return False

    # ------------------------
    # ACCESS LEVEL CHECK
    # ------------------------
    access_level_doors = fetch_doors_for_access_level(card["access_level"])
    has_normal_access = door_id in access_level_doors

    # ------------------------
    # EXTRA ACCESS CHECK (ARRAY)
    # ------------------------
    extra = card["extra_door_access"] or []

    has_extra_access = door_id in extra

    # ------------------------
    # RESULT
    # ------------------------
    return has_normal_access or has_extra_access