from pydantic import BaseModel


#create a payload visit class with url, atributtes in database
class VisitPayload(BaseModel):
    target_url: str
    user_agent: str
    referrer: str = ""


class LoginPayload(BaseModel):
    api_key: str