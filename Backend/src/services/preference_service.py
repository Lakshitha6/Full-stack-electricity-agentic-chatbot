import json
import logging
from typing import List, Dict
from src.db.client import SupabaseDB
from src.utils.config_loader import load_yaml
from src.utils.llm_router import llm_router

logger = logging.getLogger(__name__)


async def extract_preferences_from_chat(electricity_id: str, recent_messages: List[Dict]) -> Dict:
    """  
    Analyze recent chat messages to extract user preferences.
    Returns dict with: preferred_language, response_detail_level, common_queries
    """

    if not recent_messages:
        return {}
    
    # Format messages
    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in recent_messages[-10:]])

    prompt = f"""
            Analyze this user's conversation about electricity billing and extract preferences:
            
            Conversation:
            {conversation}
            
            Output JSON with these fields ONLY:
            {{
            "preferred_language": "en" or "es" or "fr" etc. (infer from user messages),
            "response_detail_level": "concise" or "detailed" (based on question complexity),
            "common_queries": ["list", "of", "frequent", "topics"] (max 5),
            "payment_behavior": "early" or "on-time" or "late" (if inferable)
            }}
            
            If unsure, use defaults: language="en", detail="concise", common_queries=[]
        """
    
    try:
        response = await llm_router.chat_completion(prompt=prompt, system_prompt="You are a preference extraction specialist. Output ONLY valid JSON.")

        import re

        # Robust JSON extraction: find the first { and last }
        json_start = response.find('{')
        json_end = response.rfind('}')
        
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = response[json_start:json_end + 1]
            try:
                preferences = json.loads(json_str)
                logger.info(f"Extracted preferences for {electricity_id}: {preferences}")
                return preferences
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}. JSON string: {json_str}")
                return {}
        else:
            logger.warning(f"No JSON found in preference extraction response: {response[:100]}")
            return {}
        
    except Exception as e:
        logger.error(f"Preference extraction failed: {e}")
        return {}
    

async def update_user_preferences(electricity_id: str, preferences: Dict):
    """Upsert preferences to Supabase (creates or updates)"""

    if not preferences:
        return
    
    config = load_yaml("db.yaml")["supabase"]

    # Prepare update data (only include non-null values)
    update_data = {k: v for k, v in preferences.items() if v is not None}
    update_data["updated_at"] = "now()"
    
    # Upsert: insert or update on conflict
    result = SupabaseDB.table(config["table_user_preferences"]).upsert(
        {"electricity_id": electricity_id, **update_data},
        on_conflict="electricity_id"
    ).execute()

    logger.info(f"Preferences updated for {electricity_id}: {result.data}")
    return result.data


async def sync_preferences_after_chat(electricity_id: str, session_id: str):
    """
    Background task: After a chat session, extract preferences and update long-term memory.
    Call this at the end of process_chat() in chat_service.py
    """

    config = load_yaml("db.yaml")["supabase"]

    # Fetch recent messages for this session
    messages = SupabaseDB.table(config["table_chat_messages"]).select(
        "role,content,session_id"
    ).in_("session_id", [
        session_id,
    ]).order("timestamp", desc=True).limit(20).execute()


    if not messages.data:
        logger.info(f"No messages found for session {session_id}, skipping preference sync.")
        return
    
    # Extract preferences from recent messages
    preferences = await extract_preferences_from_chat(electricity_id, messages.data)

    # Update preferences in Supabase
    if preferences:
        await update_user_preferences(electricity_id, preferences)
    else:
        logger.info(f"No preferences extracted for {electricity_id} from session {session_id}.")