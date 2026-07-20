from .database import get_connection, init_db
from datetime import datetime, timezone
from fastapi import FastApi, Request
from pydantic import BaseModel


app = FastAPI(title="AI Traffic Tracker", version="0.1.0")


#startup event
@app.on_event("startup")
def startup():
    init_db()
    #create a payload visit class with url, atributtes in database
    class VisitPayload(BaseModel):
        target_url: str
        traffic_type: str
        ai_provider: str = "Unknown"
        user_agent: str
        referrer: str = ""
        ip_hash: str = ""

#post method to add a new track in page
@app.post("/track")
def track_visit(payload: VisitPayload):
    conn = get_connection()
    conn.execute("""
        INSERT INTO visits
        (timestamp,target_url,traffic_type,ai_provider,user_agent,referrer,ip_hash)
        VALUES (?,?,?,?,?,?,?)""",(
            datetime.now(timezone.utc).isoformat(),
            payload.target_url,
            payload.traffic_type,
            payload.ai_provider,
            payload.user_agent,
            payload.referrer,
            payload.ip_hash,
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}
    



