from datetime import datetime
import uuid
from typing import List, Optional
import hashlib

from src.agents.chat_agent import agent
from src.agents.memory_manager import create_or_get_session, save_chat_message
from src.models.chat import ChatRequest, ChatResponse, ChatMessage, ChatSession
from src.db.client import SupabaseDB
from src.utils.config_loader import load_yaml
from src.services import cache_service

config = load_yaml("db.yaml")["supabase"]

async def process_chat(request: ChatRequest) -> ChatResponse:

    cached = cache_service.get_cached_response(request.electricity_id, request.message)

    if cached:
        cached_msg_id = f"cached-{hashlib.md5(request.message.encode()).hexdigest()[:8]}"

        save_chat_message(request.session_id or "cached", "user", request.message, {"message_id": cached_msg_id})
        save_chat_message(request.session_id or "cached", "assistant", cached["response"], {
            "message_id": cached_msg_id,
            "sql_used": cached["metadata"].get("sql"),
            "error": cached["metadata"].get("error"),
            "cache_hit": True
        })
        
        return ChatResponse(
            session_id=request.session_id or "cached",
            message_id=cached_msg_id,
            response=cached["response"],
            timestamp=datetime.utcnow(),
            metadata={**cached["metadata"], "cache_hit": True}
        )

    session_id = request.session_id or create_or_get_session(request.electricity_id, force_new=True)

    # Save user message
    user_msg_id = str(uuid.uuid4())
    save_chat_message(session_id, "user", request.message, {"message_id": user_msg_id})

    # Run Agent
    initial_state = {
        "electricity_id": request.electricity_id,
        "user_message": request.message,
        "session_id": session_id,
        "memory_context": {},
        "generated_sql": None,
        "sql_result": None,
        "final_response": "",
        "error": None
    }

    result = await agent.ainvoke(initial_state, config={"configurable": {"thread_id": session_id}})

    # Save assistant response
    bot_msg_id = str(uuid.uuid4())
    save_chat_message(session_id, "assistant", result["final_response"], {
        "message_id": bot_msg_id,
        "sql_used": result.get("generated_sql"),
        "error": result.get("error")
    })

    # Cached the result
    cache_service.set_cached_response(
        request.electricity_id,
        request.message,
        result["final_response"],
        {"sql": result.get("generated_sql"), "error": result.get("error")}
    )

    from src.workers.preference_worker import sync_preferences_task, queue
    queue.enqueue(sync_preferences_task, request.electricity_id, session_id, job_timeout=300)

    return ChatResponse(
        session_id=session_id,
        message_id=bot_msg_id,
        response=result["final_response"],
        timestamp=datetime.utcnow(),
        metadata={"sql": result.get("generated_sql"), "error": result.get("error")}
    )


async def get_sessions(electricity_id: str) -> List[ChatSession]:
    res = SupabaseDB.table(config["table_chat_sessions"]).select("*").eq("electricity_id", electricity_id).order("started_at", desc=True).execute()
    return [ChatSession(**s) for s in res.data] if res.data else []

async def get_messages(session_id: str, limit: int, offset: int) -> List[ChatMessage]:
    res = SupabaseDB.table(config["table_chat_messages"]).select("*").eq("session_id", session_id).order("timestamp", desc=False).range(offset, offset + limit - 1).execute()
    return [ChatMessage(**m) for m in res.data] if res.data else []

async def create_session(electricity_id: str, title: Optional[str] = None) -> ChatSession:
    session_id = create_or_get_session(electricity_id, title, force_new=True)
    res = SupabaseDB.table(config["table_chat_sessions"]).select("*").eq("session_id", session_id).execute()
    return ChatSession(**res.data[0])