from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from db.models import Activity
from schemas.schemas import TrendsResponse, SummaryResponse


def get_summary(db: Session) -> SummaryResponse:
    total_activities = db.query(func.count(Activity.id)).scalar() or 0
    unique_users = db.query(func.count(func.distinct(Activity.user_id))).scalar() or 0

    # by event type
    by_event_tuples = (
        db.query(Activity.event_type, func.count(Activity.id))
        .group_by(Activity.event_type)
        .all()
    )
    by_event = {t[0]: t[1] for t in by_event_tuples}

    # top pages (exclude NULL)
    top_pages_q = (
        db.query(Activity.page, func.count(Activity.id).label("cnt"))
        .filter(Activity.page != None)
        .group_by(Activity.page)
        .order_by(desc("cnt"))
        .limit(10)
        .all()
    )
    top_pages = [{"page": row[0], "count": row[1]} for row in top_pages_q]

    return {
        "total_activities": total_activities,
        "unique_users": unique_users,
        "by_event_type": by_event,
        "top_pages": top_pages,
    }


def get_trends(db: Session, days: int = 14, skip: int = 0, limit: int = 20):
    """
    Generate trend analytics for the past `days` days.
    Compatible with paginate() helper.
    """
    end = datetime.utcnow()
    start = end - timedelta(days=days - 1)

    # For SQLite: strftime("%Y-%m-%d", created_at)
    rows = (
        db.query(
            func.strftime("%Y-%m-%d", Activity.created_at).label("day"),
            func.count(Activity.id)
        )
        .filter(Activity.created_at >= start)
        .group_by("day")
        .order_by(desc(Activity.created_at))
        .all()
    )

    day_map = {r[0]: r[1] for r in rows}
    series = []
    for i in range(days):
        d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        series.append({"date": d, "count": day_map.get(d, 0)})

    # ✅ Apply pagination correctly
    total = len(series)
    paginated_items = series[skip: skip + limit]

    # ✅ Return tuple as (items, total)
    return paginated_items, total
