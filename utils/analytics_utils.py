# app/utils/analytics_utils.py
import json

def parse_payload_text(payload_text: str):
    if payload_text is None:
        return None
    if isinstance(payload_text, dict):
        return payload_text
    try:
        return json.loads(payload_text)
    except Exception:
        return {"raw": payload_text}
