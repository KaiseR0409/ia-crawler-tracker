import json 
from .database import get_connection
from pathlib import Path
from fastapi import HTTPException, Header
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

AI_REFERRERS = {
    "chatgpt.com": "ChatGPT",
    "openai.com": "OpenAI",
    "perplexity.ai": "Perplexity",
    "claude.ai": "Anthropic",
}


#load crawlers once time and store them in a set for fast lookup
CRAWLERS_FILE = Path(__file__).parent / "ai_crawlers.json"


#function to load crawlers from json file
def load_crawlers():
    if CRAWLERS_FILE.exists():
        with open(CRAWLERS_FILE, "r") as f:
            return json.load(f)
        
#construct a new dictionary with lower case keys for fast lookup
#{"gptbot": "OpenAI GPT Bot", "bard": "Google Bard", ...}
def build_index(crawlers):
    return {
        c["user_agent_token"].lower(): c for c in crawlers
    }
#variable to save index of crawlers
INDEX = build_index(load_crawlers())

#a function to class by name,operator
def classify_ua(user_agent:str) -> dict | None :
    ua_lower = user_agent.lower()
    for token, info in INDEX.items():
        if token in ua_lower:
            return {"name": info["name"], "operator": info["operator"]}
    return None

#a function to classify referrers
def classify_referrer(referrer: str) -> str | None:
    for domain, provider in AI_REFERRERS.items():
        if domain in referrer.lower():
            return provider
    return None

#api key verification function
def verify_api_key(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

#a function to endpoint stats, this function objective is to return the number of visits in the database
#and the number of visits per traffic type, and the number of visits per ai provider.
def get_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as total FROM visits").fetchone()["total"]
    
    by_type = conn.execute("""
        SELECT traffic_type, COUNT(*) as count 
        FROM visits GROUP BY traffic_type
    """).fetchall()
    
    by_provider = conn.execute("""
        SELECT ai_provider, COUNT(*) as count 
        FROM visits GROUP BY ai_provider ORDER BY count DESC
    """).fetchall()
    
    recent = conn.execute("""
        SELECT COUNT(*) as count FROM visits
        WHERE timestamp >= datetime('now', '-1 day')
    """).fetchone()["count"]
    conn.close()

    return {
        "total": total,
        "by_type": [dict(row) for row in by_type],
        "by_provider": [dict(row) for row in by_provider],
        "recent_24h": recent
    }

#function to paginate rows 
def paginate_rows(page: int = 1, limit: int = 10):
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as total FROM visits").fetchone()["total"] #select total number of rows in visits table
    offset = (page - 1) * limit # Calculate the offset for the LIMIT clause
    cursor = conn.execute(
        "SELECT timestamp, target_url, traffic_type, ai_provider, user_agent, referrer "
        "FROM visits ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    visits = [dict(row) for row in cursor.fetchall()] # Convert each row to a dictionary
    conn.close()

    pages = (total + limit -1 ) // limit # Calculate total number of pages

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "visits": visits
    }