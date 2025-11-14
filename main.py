# app/main.py
from fastapi import FastAPI
from db.database import init_db
from  api.routes import router

app = FastAPI(title="Activity Analytics API")

# Create tables
init_db()

# Include the single router containing all endpoints
app.include_router(router)


