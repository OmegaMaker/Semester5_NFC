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





###########################################################
####################ADMIN FUNCTIONS########################
###########################################################

# --------------------------------------------------
# ADMIN: CARDS
# --------------------------------------------------

def fetch_all_cards():
    query = text("""
        SELECT uid,
               owner_name,
               access_level,
               valid_from,
               valid_to,
               extra_door_access
        FROM cards
        ORDER BY created_at DESC
    """)
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return [dict(row._mapping) for row in result]


def upsert_card(
    uid: str,
    owner_name: str | None,
    access_level: int | None,
    valid_from,
    valid_to,
    extra_door_access,
):
    """
    Creates or updates card depending on uid.
    """
    query = text("""
        INSERT INTO cards (
            uid, owner_name, access_level,
            valid_from, valid_to, extra_door_access
        )
        VALUES (
            :uid, :owner_name, :access_level,
            :valid_from, :valid_to, :extra
        )
        ON CONFLICT (uid) DO UPDATE SET
            owner_name = EXCLUDED.owner_name,
            access_level = EXCLUDED.access_level,
            valid_from = EXCLUDED.valid_from,
            valid_to   = EXCLUDED.valid_to,
            extra_door_access = EXCLUDED.extra_door_access,
            updated_at = NOW()
    """)
    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "uid": uid,
                "owner_name": owner_name,
                "access_level": access_level,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "extra": extra_door_access,
            },
        )


def delete_card(uid: str):
    query = text("DELETE FROM cards WHERE uid = :uid")
    with engine.begin() as conn:
        conn.execute(query, {"uid": uid})


# --------------------------------------------------
# ADMIN: DOORS + ACCESS LEVELS
# --------------------------------------------------

def fetch_all_doors_with_levels():
    """
    Returns all door and which access level they have
    """
    query = text("""
        SELECT d.door_id,
               d.name,
               COALESCE(
                 ARRAY_AGG(al.access_level ORDER BY al.access_level)
                     FILTER (WHERE al.access_level IS NOT NULL),
                 '{}'
               ) AS access_levels
        FROM doors d
        LEFT JOIN access_level_doors al
          ON al.door_id = d.door_id
        GROUP BY d.door_id, d.name
        ORDER BY d.door_id
    """)
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return [dict(row._mapping) for row in result]


def upsert_door(door_id: str, name: str | None, access_levels: list[int]):
    """
    Creates or updates door and dets access level. 
    """
    with engine.begin() as conn:
        # upsert på doors
        conn.execute(
            text("""
                INSERT INTO doors (door_id, name)
                VALUES (:door_id, :name)
                ON CONFLICT (door_id) DO UPDATE SET
                    name = EXCLUDED.name
            """),
            {"door_id": door_id, "name": name},
        )

        # ta bort gamla kopplingar
        conn.execute(
            text("DELETE FROM access_level_doors WHERE door_id = :door_id"),
            {"door_id": door_id},
        )

        # skapa nya kopplingar
        for level in access_levels:
            conn.execute(
                text("""
                    INSERT INTO access_level_doors (access_level, door_id)
                    VALUES (:level, :door_id)
                """),
                {"level": level, "door_id": door_id},
            )


def delete_door(door_id: str):
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM access_level_doors WHERE door_id = :door_id"),
            {"door_id": door_id},
        )
        conn.execute(
            text("DELETE FROM doors WHERE door_id = :door_id"),
            {"door_id": door_id},
        )