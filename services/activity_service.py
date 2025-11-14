# services/activity_service.py
from sqlalchemy.orm import Session
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


def get_user_activities(db: Session, user_id: str, skip: int = 0, limit: int = 20):
    """
    Fetch activities for a specific user WITH pagination support.
    This must accept skip + limit because paginate() sends them.
    """
    query = db.query(Activity).filter(Activity.user_id == user_id)

    total = query.count()

    results = (
        query.order_by(Activity.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return results, total
