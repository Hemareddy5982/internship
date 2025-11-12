from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
import json
from pydantic.generics import GenericModel

# ------------------------
# Request Schemas
# ------------------------
class TrackActivityRequest(BaseModel):
    user_id: str = Field(..., example="user_123")
    event_type: str = Field(..., example="page_view")
    page: Optional[str] = Field(None, example="/home")
    payload: Optional[dict] = Field(None, example={"action": "click"})
    timestamp: Optional[datetime] = Field(None)


# ------------------------
# Response Schemas
# ------------------------
class ActivityResponse(BaseModel):
    id: int
    user_id: str
    event_type: str
    page: Optional[str]
    payload: Optional[dict]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

    # Fix: handle ORM object or dict
    @model_validator(mode="before")
    def parse_payload(cls, values):
        if isinstance(values, dict):
            payload = values.get("payload")
        else:  # ORM object
            payload = getattr(values, "payload", None)

        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = None

        # Update values
        if isinstance(values, dict):
            values["payload"] = payload
        else:
            values.payload = payload
        return values


# ------------------------
# Analytics Schemas
# ------------------------
class SummaryResponse(BaseModel):
    total_activities: int
    unique_users: int
    by_event_type: dict
    top_pages: List[dict]


class TrendPoint(BaseModel):
    date: str
    count: int


class TrendsResponse(BaseModel):
    trends: List[TrendPoint]


# ------------------------
# Dashboard Schemas
# ------------------------
class DashboardOverview(BaseModel):
    total_activities: int
    active_users_last_15m: int
    recent_activities: List[ActivityResponse]
    top_pages: List[dict]


# ------------------------
# Generic Pagination Schema
# ------------------------
T = TypeVar("T")

class PaginatedResponse(GenericModel, Generic[T]):
    """
    Generic pagination response model.
    Can be reused for any data type, e.g. PaginatedResponse[ActivityResponse]
    """
    page: int = Field(..., example=1)
    limit: int = Field(..., example=20)
    total: int = Field(..., example=150)
    items: List[T]

class PaginatedTrendsResponse(BaseModel):
    items: List[TrendPoint]
    total: int
    page: int
    limit: int
