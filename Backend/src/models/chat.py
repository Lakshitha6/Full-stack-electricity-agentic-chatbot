from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    electricity_id: str = Field(..., pattern=r"^ELEC-\d{6}$")
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)

class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None

class ChatSession(BaseModel):
    session_id: str
    electricity_id: str
    title: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    is_active: bool

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    response: str
    timestamp: datetime
    metadata: Optional[dict] = None  # confidence, tool calls, etc.