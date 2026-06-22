from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from src.models.chat import ChatMessage, ChatRequest, ChatResponse, ChatSession
from src.services.chat_service import process_chat, get_messages, get_sessions, create_session

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message and get agent response"""

    try:
        return await process_chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[ChatSession])
async def list_sessions(electricity_id: str = Query(..., description="User's electricity ID")):
    """List chat sessions for user"""

    return await get_sessions(electricity_id)


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_session_messages(session_id: str, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Get paginated messages for a session"""

    return await get_messages(session_id, limit, offset)

@router.post("/sessions", response_model=ChatSession)
async def start_session(
    electricity_id: str = Query(..., description="User's electricity ID"),
    title: Optional[str] = Query(None, description="Optional session title")
):
    """Create a new chat session"""

    return await create_session(electricity_id, title)