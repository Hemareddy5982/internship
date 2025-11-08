# app/services/health_service.py
from datetime import datetime

def health_check():
    return {
        "status": "ok",
        "message": "namma app is ok 😊",
        "time": datetime.utcnow().isoformat() + "Z"
    }
