# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from db.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False)
    payload = Column(Text, nullable=True)  # JSON stored as string
    page = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

