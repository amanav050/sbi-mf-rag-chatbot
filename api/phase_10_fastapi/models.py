from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    session_id: str = Field(default="default")

class ChatResponse(BaseModel):
    answer: str
    source_url: str
    scraped_date: str
    session_id: str
    is_refusal: bool = False
