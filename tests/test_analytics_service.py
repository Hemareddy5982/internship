import pytest
from datetime import datetime, timedelta
from db.models import Activity
from services import analytics_service

@pytest.fixture
def db_session():
    from db.database import SessionLocal
    db = SessionLocal()
    yield db
    db.close()

def test_get_summary(db_session):
    db_session.add(Activity(user_id="1", event_type="view", payload="{}", created_at=datetime.utcnow()))
    db_session.commit()
    result = analytics_service.get_summary(db_session)
    assert "total_activities" in result
    assert isinstance(result["total_activities"], int)

def test_get_trends(db_session):
    now = datetime.utcnow()
    for i in range(5):
        db_session.add(Activity(user_id="1", event_type="view", payload="{}", created_at=now - timedelta(days=i)))
    db_session.commit()
    result = analytics_service.get_trends(db_session, days=5)
    if isinstance(result, tuple):
        result = result[0]
    assert isinstance(result, list)

