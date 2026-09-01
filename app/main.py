from .database import get_connection, init_db
from datetime import datetime, timezone
#fast api imports
from fastapi import FastAPI, Depends, Query
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
#models imports
from .models import VisitPayload, LoginPayload
#services imports
from .services import (
    classify_ua, classify_referrer, verify_api_key, verify_access,
    get_stats, paginate_rows, create_session, destroy_session, session_valid,
    SESSION_TTL,
)
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
API_KEY = os.getenv("API_KEY", "")


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
@app.post("/api/track")
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
@app.get("/api/visits")
@limiter.limit("60/minute") # Limit to 60 requests per minute per IP
def get_visits(request: Request, _: str = Depends(verify_access), page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    return paginate_rows(page=page, limit=limit)


#method to give a tracker.js to a page, it dont need api key, its public, but the track method and get visits method need api key to be used, this is for security reasons.
#this method dont need limiter because is public.
@app.get("/api/tracker.js")
def get_tracker_js():
    js_path = Path(__file__).parent / "tracker.js"
    js_content = js_path.read_text()
    js_content = js_content.replace("{{API_URL}}", API_URL)
    # the script is public but /api/track needs the key; injected here so each
    # self-hosted deployment sends its own API_KEY from .env
    js_content = js_content.replace("{{API_KEY}}", API_KEY)
    return Response(content=js_content, media_type="application/javascript")

#method to give a stats of visits, this method need api key to be used, this is for security reasons.
@app.get("/api/stats")
@limiter.limit("60/minute") # Limit to 10 requests per minute per IP
def get_stats_endpoint(request: Request, _: str = Depends(verify_access)):
    stats = get_stats()
    return stats


#login endpoint: validates the api key and exchanges it for an httpOnly session cookie
@app.post("/api/login")
@limiter.limit("10/minute")
def login(request: Request, response: Response, payload: LoginPayload):
    if payload.api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    token = create_session()
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=int(SESSION_TTL.total_seconds()),
        secure=False,  # internal http-only deployment; set True behind HTTPS
    )
    return {"status": "ok"}


#logout endpoint: destroys the session and clears the cookie
@app.post("/api/logout")
def logout(request: Request, response: Response):
    destroy_session(request.cookies.get("session"))
    response.delete_cookie("session")
    return {"status": "ok"}


#auth status endpoint: tells the frontend whether a session is valid
@app.get("/api/auth/status")
def auth_status(request: Request):
    return {"authenticated": session_valid(request.cookies.get("session"))}


# serve the built dashboard (single port 5000)
_dashboard_dist = Path(__file__).parent.parent / "dashboard" / "dist"
if _dashboard_dist.exists():
    app.mount("/", StaticFiles(directory=_dashboard_dist, html=True), name="dashboard")
else:
    print("WARNING: dashboard/dist not found, run `npm run build` inside /dashboard")

