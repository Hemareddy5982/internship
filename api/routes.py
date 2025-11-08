# app/routes/routes.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from db.database import get_db
from schemas.schemas import (
    TrackActivityRequest,
    ActivityResponse,
    SummaryResponse,
    TrendsResponse,
    DashboardOverview,
)
from services import (
   activity_service,
    analytics_service,
    dashboard_service,
    health_service, 
)

router = APIRouter()


# Health
@router.get("/health", tags=["Health Check"])
def health_check():
    return health_service.health_check()


# Activity: track
@router.post("/activity/track", response_model=ActivityResponse, status_code=201, tags=["Activity"])
def track_activity(payload: TrackActivityRequest, db: Session = Depends(get_db)):
    activity = activity_service.track_activity(db, payload)
    return activity


# Activity: get user history
@router.get("/activity/user/{user_id}", response_model=list[ActivityResponse], tags=["Activity"])
def get_user_activity(user_id: str, limit: int = Query(200, ge=1, le=2000), db: Session = Depends(get_db)):
    return activity_service.get_user_activities(db, user_id, limit=limit)


# Analytics: summary
@router.get("/analytics/summary", response_model=SummaryResponse, tags=["Analytics"])
def analytics_summary(db: Session = Depends(get_db)):
    return analytics_service.get_summary(db)


# Analytics: trends
@router.get("/analytics/trends", response_model=TrendsResponse, tags=["Analytics"])
def analytics_trends(days: int = Query(14, ge=1, le=90), db: Session = Depends(get_db)):
    return analytics_service.get_trends(db, days=days)


# Dashboard overview
@router.get("/dashboard/overview", response_model=DashboardOverview, tags=["Dashboard"])
def dashboard_overview(recent_limit: int = Query(20, ge=1, le=200), db: Session = Depends(get_db)):
    return dashboard_service.get_overview(db, recent_limit=recent_limit)
