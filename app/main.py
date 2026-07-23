from .database import get_connection, init_db
from datetime import datetime, timezone
#fast api imports
from fastapi import FastAPI, Depends, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
#models imports
from .models import VisitPayload
#services imports
from .services import classify_ua, classify_referrer, verify_api_key, get_stats, paginate_rows
#pathlib import Path
from pathlib import Path
#slow api imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import os
#load dotenv file
from dotenv import load_dotenv


load_dotenv()
#api url
API_URL = os.getenv("API_URL", "http://localhost:5000")


app = FastAPI(title="AI Traffic Tracker", version="0.1.0")

#this cors is to allow al origins to access, is not secure to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

#startup event
@app.on_event("startup")
def startup():
    init_db()


#limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter



#post method to add a new track in page
@app.post("/track")
@limiter.limit("30/minute") # Limit to 30 requests per minute per IP
def track_visit(request:Request, payload: VisitPayload, _: str = Depends(verify_api_key)):
    
    #first we classify the user agent and referrer
    ua_result = classify_ua(payload.user_agent)

    if(ua_result):
        traffic_type = "crawler"
        ai_provider = ua_result["operator"]
    else:
        ref_result = classify_referrer(payload.referrer)
        if(ref_result):
            traffic_type = "referral"
            ai_provider = ref_result
        else:
            traffic_type = "unknown"
            ai_provider = "unknown" 
    
    conn = get_connection()
    conn.execute("""
        INSERT INTO visits
        (timestamp, target_url, traffic_type, ai_provider, user_agent, referrer)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (
            datetime.now(timezone.utc).isoformat(),
            payload.target_url,
            traffic_type,      
            ai_provider,       
            payload.user_agent,
            payload.referrer,
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}

#get method test, is not to production bc is not secure, is only for test and development
@app.get("/visits")
@limiter.limit("60/minute") # Limit to 60 requests per minute per IP
def get_visits(request: Request, _: str = Depends(verify_api_key), page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    return paginate_rows(page=page, limit=limit)


#method to give a tracker.js to a page, it dont need api key, its public, but the track method and get visits method need api key to be used, this is for security reasons.
#this method dont need limiter because is public.
@app.get("/tracker.js")
def get_tracker_js():
    js_path = Path("app/tracker.js")
    js_content = js_path.read_text()
    js_content = js_content.replace("{{API_URL}}", API_URL)
    return Response(content=js_content, media_type="application/javascript")

#method to give a stats of visits, this method need api key to be used, this is for security reasons.
@app.get("/stats")
@limiter.limit("60/minute") # Limit to 10 requests per minute per IP
def get_stats_endpoint(request: Request, _: str = Depends(verify_api_key)):
    stats = get_stats()
    return stats

