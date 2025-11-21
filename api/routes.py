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
@router.get(
    "/health",
    tags=["Health Check"],
    summary="Health Check",
    description="Verifies that the API is running and all dependencies are available."
)
def health_check():
    """
    Health check endpoint.
    
    Verifies that the API is running and all dependencies are available.
    
    Returns:
        dict: Status information of the API and its services.
    """
    return health_service.health_check()


# ────────────────────────────────
# 🏃 Activity Endpoints
# ────────────────────────────────
@router.post(
    "/activity/track",
    response_model=ActivityResponse,
    status_code=201,
    tags=["Activity"],
    summary="Track User Activity",
    description="Creates and stores a new activity record in the database. This endpoint records user actions for analytics and history purposes."
)
def track_activity(payload: TrackActivityRequest, db: Session = Depends(get_db)):
    """
    Track a new user activity.
    
    Creates and stores a new activity record in the database.
    This endpoint records user actions for analytics and history purposes.
    
    Args:
        payload (TrackActivityRequest): Activity data including user_id, activity_type, and metadata.
        db (Session): Database session dependency.
    
    Returns:
        ActivityResponse: The created activity record with id, timestamp, and all details.
    
    Raises:
        HTTPException: If the activity data is invalid or database operation fails.
    """
    activity = activity_service.track_activity(db, payload)
    return activity


@router.get(
    "/activity/user/{user_id}",
    response_model=PaginatedResponse[ActivityResponse],
    tags=["Activity"],
    summary="Get User Activity History",
    description="Retrieves paginated activity history for a specific user. Returns all activities associated with the user_id with support for pagination."
)
def get_user(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number for pagination (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Number of records per page (1-100)"),
    db: Session = Depends(get_db),
):
    """
    Retrieve paginated activity history for a specific user.
    
    Fetches all activities associated with a user_id, supporting pagination
    for efficient data retrieval and display.
    
    Args:
        user_id (str): The unique identifier of the user.
        page (int): Page number for pagination (1-indexed). Defaults to 1.
        limit (int): Number of records per page (1-100). Defaults to 20.
        db (Session): Database session dependency.
    
    Returns:
        PaginatedResponse[ActivityResponse]: Paginated list of user activities with metadata.
        Contains: page, limit, total count, and items array.
    
    Raises:
        HTTPException: If user_id is not found or invalid.
    """
    return paginate(activity_service.get_user_activities, db, page, limit, user_id=user_id)


# ────────────────────────────────
# 📊 Analytics Endpoints
# ────────────────────────────────
@router.get(
    "/analytics/summary",
    response_model=SummaryResponse,
    tags=["Analytics"],
    summary="Analytics Summary",
    description="Provides high-level statistics about all activities in the system, including total counts, user metrics, and activity type breakdowns."
)
def analytics_summary(db: Session = Depends(get_db)):
    """
    Get overall analytics summary.
    
    Provides high-level statistics about all activities in the system,
    including total counts, user metrics, and activity type breakdowns.
    
    Args:
        db (Session): Database session dependency.
    
    Returns:
        SummaryResponse: Summary statistics with aggregated data across all users and activities.
    
    Raises:
        HTTPException: If database query fails.
    """
    return analytics_service.get_summary(db)


@router.get(
    "/analytics/trends",
    response_model=PaginatedTrendsResponse,
    tags=["Analytics"],
    summary="Analytics Trends",
    description="Analyzes activity patterns and trends over a specified time period (1-90 days). Supports pagination for viewing trend data efficiently."
)
def analytics_trends(
    days: int = Query(14, ge=1, le=90, description="Number of days to analyze (1-90)"),
    page: int = Query(1, ge=1, description="Page number for pagination (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Number of trend records per page (1-100)"),
    db: Session = Depends(get_db),
):
    """
    Retrieve paginated trend analysis over a specified time period.
    
    Analyzes activity patterns and trends for the given number of days,
    supporting pagination for viewing trend data in manageable chunks.
    
    Args:
        days (int): Number of days to analyze (1-90). Defaults to 14.
        page (int): Page number for pagination (1-indexed). Defaults to 1.
        limit (int): Number of trend records per page (1-100). Defaults to 20.
        db (Session): Database session dependency.
    
    Returns:
        PaginatedTrendsResponse: Paginated trend analysis data with page metadata.
        Contains: page, limit, total count, and trend items array.
    
    Raises:
        HTTPException: If days parameter is out of range or database query fails.
    """
    return paginate(analytics_service.get_trends, db, page, limit, days=days)


# ────────────────────────────────
# 📈 Dashboard Endpoints
# ────────────────────────────────
@router.get(
    "/dashboard/overview",
    summary="Dashboard Overview",
    description="Provides a comprehensive dashboard view combining summary statistics, key metrics, and the most recent user activities for quick insights."
)
def dashboard_overview(
    db: Session = Depends(get_db),
    recent_limit: int = Query(10, ge=1, le=100, description="Maximum number of recent activities to include (1-100)")
):
    """
    Get dashboard overview with summary and recent activities.
    
    Provides a comprehensive dashboard view combining summary statistics,
    key metrics, and the most recent user activities for quick insights.
    
    Args:
        db (Session): Database session dependency.
        recent_limit (int): Maximum number of recent activities to include. Defaults to 10.
    
    Returns:
        DashboardOverview: Dashboard data containing summary stats and recent activity list.
    
    Raises:
        HTTPException: If database query fails.
    """
    return dashboard_service.get_overview(db, recent_limit=recent_limit)
