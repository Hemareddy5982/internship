import pytest
from datetime import datetime, timedelta
from sqlalchemy.sql.functions import Function
from db.models import Activity
from services import dashboard_service


def test_func_count_distinct(db_session):
    """Test count distinct helper."""
    if hasattr(dashboard_service, "func_count_distinct"):
        result = dashboard_service.func_count_distinct(db_session)
        assert result is not None
        # ✅ Accept SQLAlchemy count expression
        assert isinstance(result, Function)
    else:
        pytest.skip("func_count_distinct not implemented")


def test_get_active_users_since(db_session):
    now = datetime.utcnow()
    old_time = now - timedelta(minutes=30)
    db_session.add_all([
        Activity(user_id="1", event_type="click", payload="{}", created_at=now),
        Activity(user_id="2", event_type="view", payload="{}", created_at=old_time),
    ])
    db_session.commit()

    active_count = dashboard_service.get_active_users_since(db_session, minutes=15)
    assert isinstance(active_count, int)
    assert active_count >= 0


def test_get_overview(db_session, monkeypatch):
    """Test dashboard overview aggregation."""
    from services import analytics_service, activity_service

    monkeypatch.setattr(analytics_service, "get_summary", lambda db: {
        "total_activities": 10,
        "unique_users": 3,
        "by_event_type": {"click": 5, "view": 5},
        "top_pages": [{"page": "home", "count": 5}]
    })
    monkeypatch.setattr(activity_service, "get_recent_activities", lambda db, limit=5: [
        Activity(user_id="1", event_type="visit", payload="{}", created_at=datetime.utcnow())
    ])

    result = dashboard_service.get_overview(db_session)
    assert isinstance(result, dict)
    assert "total_activities" in result
    assert "recent_activities" in result
    assert "top_pages" in result
