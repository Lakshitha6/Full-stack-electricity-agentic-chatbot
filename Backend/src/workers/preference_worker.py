import redis
from rq import Worker, Queue

from src.services.preference_service import extract_preferences_from_chat, update_user_preferences
from src.utils.config_loader import get_env

# Connect to Redis
REDIS_URL = get_env("REDIS_URL", "redis://localhost:6379/0")
conn = redis.from_url(REDIS_URL)
queue = Queue("preferences", connection=conn)


def sync_preferences_task(electricity_id: str, session_id: str):
    """
    Worker function to extract and update user preferences based on chat history (runs in background) .
    """

    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_async_sync_preferences(electricity_id, session_id))
    finally:
        loop.close()

async def _async_sync_preferences(electricity_id: str, session_id: str):
    """ Asynchronous helper function to perform the preference extraction and update."""

    from src.services.preference_service import sync_preferences_after_chat

    await sync_preferences_after_chat(electricity_id, session_id)