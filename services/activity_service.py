# services/activity_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.models import Activity
from schemas.schemas import TrackActivityRequest
from datetime import datetime
import json


def track_activity(db: Session, payload: TrackActivityRequest):
    """
    Insert a new activity record into the database.
    """
    # Ensure payload is always a JSON string
    payload_data = payload.payload
    if isinstance(payload_data, dict):
        payload_data = json.dumps(payload_data)
    print(payload,'testing payload')
    new_activity = Activity(
        user_id=payload.user_id,
        event_type=payload.event_type,
        page=payload.page,
        payload=payload_data,
        created_at=payload.timestamp or datetime.utcnow()
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


def get_recent_activities(db: Session, limit: int = 10):
    """
    Fetch the most recent activities.
    """
    return (
        db.query(Activity)
        .order_by(Activity.created_at.desc())
        .limit(limit)
        .all()
    )


def get_user_activities(db, user_id: str, skip: int, limit: int):
    from sqlalchemy import text

    # total count
    total = db.execute(
        text("SELECT COUNT(*) FROM activities WHERE user_id = :uid"),
        {"uid": user_id}
    ).scalar()

    # rows
    rows = db.execute(
        text("""
            SELECT *
            FROM activities
            WHERE user_id = :uid
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
        """),
        {"uid": user_id, "limit": limit, "skip": skip}
    ).mappings().all()

    # 🔥 Convert RowMapping → Pure Python dict (Pydantic-safe)
    clean_rows = [dict(row) for row in rows]

    return clean_rows, total
