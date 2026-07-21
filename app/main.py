from .database import get_connection, init_db
from datetime import datetime, timezone
from fastapi import FastAPI
from .models import VisitPayload



app = FastAPI(title="AI Traffic Tracker", version="0.1.0")

#startup event
@app.on_event("startup")
def startup():
    init_db()

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

#get method test, is not to production bc is not secure, is only for test and development
@app.get("/visits")
def get_visits():
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM visits ORDER BY timestamp DESC")
    visits = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"visits": visits}




