# app/services/dashboard_service.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from services.activity_service import get_recent_activities
from services.analytics_service import get_summary
from db.models import Activity
from utils.analytics_utils import parse_payload_text

def get_active_users_since(db: Session, minutes: int = 15) -> int:
    since = datetime.utcnow() - timedelta(minutes=minutes)
    count = db.query(func_count_distinct(Activity.user_id)).filter(Activity.created_at >= since).scalar() or 0
    return count

# helper because SQLAlchemy func.count(distinct(...)) is used often
from sqlalchemy import func
def func_count_distinct(col):
    return func.count(func.distinct(col))

def get_overview(db: Session, recent_limit: int = 20):
    summary = get_summary(db)
    recent_objs = get_recent_activities(db, limit=recent_limit)
    # convert nested Pydantic objects to ActivityResponse-like dicts (they are already Pydantic models)
    recent_list = []
    for r in recent_objs:
        # r is an ActivityResponse (Pydantic model)
        # ensure payload is a parsed object
        if isinstance(r.payload, str):
            r.payload = parse_payload_text(r.payload)
        recent_list.append(r)
    active_users = get_active_users_since(db, minutes=15)
    return {
        "total_activities": summary["total_activities"],
        "active_users_last_15m": active_users,
        "recent_activities": recent_list,
        "top_pages": summary["top_pages"],
    }
