# app/services/activity_service.py
from sqlalchemy.orm import Session
from datetime import datetime
import json

from db.models import Activity
from schemas.schemas import TrackActivityRequest, ActivityResponse
from utils.analytics_utils import parse_payload_text

def track_activity(db: Session, payload: TrackActivityRequest) -> ActivityResponse:
    payload_text = None
    if payload.payload is not None:
        payload_text = json.dumps(payload.payload)

    ts = payload.timestamp or datetime.utcnow()
    act = Activity(
        user_id=payload.user_id,
        event_type=payload.event_type,
        page=payload.page,
        payload=payload_text,
        created_at=ts
    )
    db.add(act)
    db.commit()
    db.refresh(act)

    resp = ActivityResponse.from_orm(act)
    resp.payload = parse_payload_text(act.payload)
    return resp

def get_user_activities(db: Session, user_id: str, limit: int = 200) -> list[ActivityResponse]:
    rows = db.query(Activity).filter(Activity.user_id == user_id).order_by(Activity.created_at.desc()).limit(limit).all()
    result = []
    for r in rows:
        ar = ActivityResponse.from_orm(r)
        ar.payload = parse_payload_text(r.payload)
        result.append(ar)
    return result

def get_recent_activities(db: Session, limit: int = 50) -> list[ActivityResponse]:
    rows = db.query(Activity).order_by(Activity.created_at.desc()).limit(limit).all()
    result = []
    for r in rows:
        ar = ActivityResponse.from_orm(r)
        ar.payload = parse_payload_text(r.payload)
        result.append(ar)
    return result
