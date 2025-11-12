from sqlalchemy.orm import Session
from datetime import datetime
from db.models import Activity  # adjust import path if needed
from schemas.schemas import TrackActivityRequest


# -----------------------------
# 🏃 Track Activity
# -----------------------------
def track_activity(db: Session, payload: TrackActivityRequest):
    """
    Insert a new activity record into the database.
    """
    new_activity = Activity(
        user_id=payload.user_id,
        event_type=payload.event_type,
        page=payload.page,
        payload=payload.payload,
        created_at=payload.timestamp or datetime.utcnow()
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


# -----------------------------
# 📜 Get User Activities (Paginated)
# -----------------------------
def get_user_activities(db: Session, user_id: str, skip: int = 0, limit: int = 20):
    """
    Retrieve paginated user activity data for a specific user.
    Returns a tuple: (activities, total_count)
    """
    query = db.query(Activity).filter(Activity.user_id == user_id).order_by(Activity.created_at.desc())
    total = query.count()
    activities = query.offset(skip).limit(limit).all()
    return activities, total


# -----------------------------
# 🕒 Get Recent Activities
# -----------------------------
def get_recent_activities(db: Session, limit: int = 20):
    """
    Retrieve the most recent activities (for dashboard or analytics).
    """
    activities = db.query(Activity).order_by(Activity.created_at.desc()).limit(limit).all()
    return activities


# -----------------------------
# 📋 (Optional) Get All Activities
# -----------------------------
def get_all_activities(db: Session, skip: int = 0, limit: int = 20):
    """
    Retrieve all activities (admin-level, paginated).
    """
    query = db.query(Activity).order_by(Activity.created_at.desc())
    total = query.count()
    activities = query.offset(skip).limit(limit).all()
    return activities, total
