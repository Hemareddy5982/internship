# app/main.py
from fastapi import FastAPI
from db.database import init_db
from  api.routes import router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Activity Analytics API")

# ---- CORS SETTINGS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],        # Allow all HTTP methods (GET, POST, PUT, DELETE...)
    allow_headers=["*"],        # Allow all headers
)

# Create tables
init_db()

# Include the single router containing all endpoints
app.include_router(router)


