import hashlib
from http import client
import json
import logging
from typing import Optional, Dict, Any
import re

import redis

from src.utils.config_loader import get_env


logger = logging.getLogger(__name__)

REDIS_URL = get_env("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(get_env("CHAT_CACHE_TTL", "600"))


_redis_client: Optional[redis.Redis] = None

def get_redis_client() -> Optional[redis.Redis]:
    """ Redis client with fallback and auto recovery if redis down unexpectedly """

    global _redis_client

    if _redis_client is None:
        try:
            client = redis.from_url(REDIS_URL, decode_responses=True)
            client.ping()
            _redis_client = client
            logger.info("Redis cache connected")

        except Exception as e:
            logger.warning(f"Redis cache unavailable (fallback to no-cache): {e}")
            _redis_client = None

    return _redis_client


def _normalize_question(question: str) -> str:
    """Strip whitespace, lowercase, remove punctuation for consistent keys"""
    return re.sub(r'[^\w\s]', '', question.strip().lower())


def get_cache_key(electricity_id: str, question: str) -> str:
    normalized = _normalize_question(question)
    question_hash = hashlib.md5(normalized.encode()).hexdigest()[:8]
    return f"chat_cache:{electricity_id}:{question_hash}"

def get_cached_response(electricity_id: str, question: str) -> Optional[Dict[str, Any]]:
    """Returns cached {response, metadata} or None"""

    client = get_redis_client()

    if not client:
        return None
    
    key = get_cache_key(electricity_id, question)

    try:
        data = client.get(key)

        if data:
            logger.info(f"Cache HIT: {key}")
            return json.loads(data)
        logger.debug(f"Cache MISS: {key}")
        return None
    
    except Exception as e:
        logger.error(f"Cache read failed: {e}")
        return None
    

def set_cached_response(electricity_id: str, question: str, response: str, metadata: Dict) -> None:
    """Cache the LLM response + SQL metadata"""
    client = get_redis_client()
    if not client:
        return
    
    key = get_cache_key(electricity_id, question)
    payload = {"response": response, "metadata": metadata}

    try:
        client.setex(key, CACHE_TTL, json.dumps(payload))
        logger.info(f"Cached response: {key} (TTL={CACHE_TTL}s)")

    except Exception as e:
        logger.error(f"Cache write failed: {e}")