from typing import Optional, Dict, List
from datetime import datetime
import uuid

from src.db.client import SupabaseDB
from src.utils.config_loader import load_yaml


config = load_yaml("db.yaml")["supabase"]
memory_config = load_yaml("memory.yaml")


def end_session(session_id: str) -> bool:
    """Mark session as ended with timestamp"""
    try:
        SupabaseDB.table(config["table_chat_sessions"]).update({
            "is_active": False,
            "ended_at": datetime.utcnow().isoformat()
        }).eq("session_id", session_id).execute()
        return True
    except Exception as e:
        print(f"Failed to end session {session_id}: {e}")
        return False


def get_memory_context(electricity_id: str, session_id: Optional[str] = None) -> Dict:
    """Retrieve combined memory context for agent"""

    context = {}

    # long term memory( user preferences )
    prefs = SupabaseDB.table(config["table_user_preferences"]).select("*").eq("electricity_id",electricity_id).execute()

    if prefs.data:
        context.update(prefs.data[0])

        # Remove embeddings vector from context , because it's not needed for prompt
        context.pop("preference_vec", None)


    # Medium term memory (recent chat history)
    if session_id:
        recent = SupabaseDB.table(config["table_chat_messages"]).select("role,content").eq("session_id", session_id).order("timestamp", desc=True).limit(memory_config["tiers"]["medium_term"]["summary_turns"]).execute()

        if recent.data:
            context["recent_conversation"] = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in reversed(recent.data)
            ]

    return context


def save_chat_message(session_id: str, role: str, content: str, metadata: dict = None):

    """Save a message to chat_messages table"""

    SupabaseDB.table(config["table_chat_messages"]).insert({
        "session_id": session_id,
        "role": role,
        "content": content,
        "metadata": metadata or {}
    }).execute()


def create_or_get_session(electricity_id: str, title: Optional[str] = None, force_new: bool = False) -> str:

    """Create new session. If force_new=True, end the previous active session first."""

    if force_new:
        # End previous active session for particular user
        res = SupabaseDB.table(config["table_chat_sessions"]).select("session_id").eq(
            "electricity_id", electricity_id
        ).eq("is_active", True).execute()
        
        if res.data:
            for old_session in res.data:
                end_session(old_session["session_id"])
    
    # Create new session
    session_id = str(uuid.uuid4())
    session_title = title or f"Chat {datetime.now().strftime('%m/%d/%Y')}"
    
    SupabaseDB.table(config["table_chat_sessions"]).insert({
        "session_id": session_id,
        "electricity_id": electricity_id,
        "title": session_title,
        "started_at": datetime.utcnow().isoformat(),
        "is_active": True
    }).execute()
    
    return session_id