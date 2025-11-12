# app/routes/routes.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.schemas import (
    TrackActivityRequest,
    ActivityResponse,
    SummaryResponse,
    TrendsResponse,
    DashboardOverview,
    PaginatedResponse,
    PaginatedTrendsResponse
)
from services import (
    activity_service,
    analytics_service,
    dashboard_service,
    health_service,
)

router = APIRouter()


# ────────────────────────────────
# 🧭 Common Pagination Utility
# ────────────────────────────────
def paginate(query_function, db: Session, page: int, limit: int, **kwargs):
    """
    Common pagination helper.
    Automatically calculates skip, calls the query function, 
    and wraps the result in a PaginatedResponse format.
    """
    skip = (page - 1) * limit
    items, total = query_function(db, skip=skip, limit=limit, **kwargs)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "items": items,
    }


# ────────────────────────────────
# 🩺 Health Check Endpoint
# ────────────────────────────────
@router.get("/health", tags=["Health Check"])
def health_check():
    return health_service.health_check()


# ────────────────────────────────
# 🏃 Activity Endpoints
# ────────────────────────────────
@router.post(
    "/activity/track",
    response_model=ActivityResponse,
    status_code=201,
    tags=["Activity"]
)
def track_activity(payload: TrackActivityRequest, db: Session = Depends(get_db)):
    activity = activity_service.track_activity(db, payload)
    return activity


@router.get(
    "/activity/user/{user_id}",
    response_model=PaginatedResponse[ActivityResponse],
    tags=["Activity"]
)
def get_user_activity(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get paginated user activity list.
    """
    return paginate(activity_service.get_user_activities, db, page, limit, user_id=user_id)


# ────────────────────────────────
# 📊 Analytics Endpoints
# ────────────────────────────────
@router.get(
    "/analytics/summary",
    response_model=SummaryResponse,
    tags=["Analytics"]
)
def analytics_summary(db: Session = Depends(get_db)):
    return analytics_service.get_summary(db)


@router.get(
    "/analytics/trends",
    response_model=PaginatedTrendsResponse,
    tags=["Analytics"]
)
def analytics_trends(
    days: int = Query(14, ge=1, le=90),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get paginated trend data for analytics.
    """
    return paginate(analytics_service.get_trends, db, page, limit, days=days)


# ────────────────────────────────
# 📈 Dashboard Endpoints
# ────────────────────────────────
@router.get("/dashboard/overview")
def dashboard_overview(db: Session = Depends(get_db), recent_limit: int = 10):
    """
    Dashboard overview endpoint.
    Shows summary statistics and recent activities.
    """
    return dashboard_service.get_overview(db, recent_limit=recent_limit)
