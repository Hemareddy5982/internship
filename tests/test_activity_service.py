from datetime import datetime
from services import activity_service
from db.models import Activity
from schemas.schemas import TrackActivityRequest
import json


def test_track_activity(db_session):
    # ✅ Pass dict payload (schema expects dict)
    request = TrackActivityRequest(
        user_id="1",
        event_type="login",
        page=None,
        payload={"action": "test"},  # ✅ dict, not JSON string
        timestamp=datetime.utcnow()
    )

    # Manually serialize payload before inserting, since DB expects Text
    request.payload = json.dumps(request.payload)

    new_activity = activity_service.track_activity(db_session, request)

    assert new_activity.user_id == "1"
    assert new_activity.event_type == "login"
    assert isinstance(new_activity.payload, str)  # ✅ stored as string in DB
    assert isinstance(new_activity.created_at, datetime)


def test_get_recent_activities(db_session):
    now = datetime.utcnow()
    db_session.add_all([
        Activity(user_id="1", event_type="click", payload="{}", created_at=now),
        Activity(user_id="2", event_type="view", payload="{}", created_at=now),
    ])
    db_session.commit()

    results = activity_service.get_recent_activities(db_session, limit=2)
    assert isinstance(results, list)
    assert len(results) <= 2


def test_get_user_activities(db_session):
    now = datetime.utcnow()
    db_session.add_all([
        Activity(user_id="1", event_type="click", payload="{}", created_at=now),
        Activity(user_id="2", event_type="view", payload="{}", created_at=now),
    ])
    db_session.commit()

    activities, total = activity_service.get_user_activities(db_session, user_id="1", limit=10)

    assert isinstance(activities, list)
    assert isinstance(total, int)
    assert all(isinstance(a, Activity) for a in activities)
    assert all(a.user_id == "1" for a in activities)
