from pydantic import BaseModel


#create a payload visit class with url, atributtes in database
class VisitPayload(BaseModel):
    target_url: str
    traffic_type: str
    ai_provider: str = "Unknown"
    user_agent: str
    referrer: str = ""
    ip_hash: str = ""