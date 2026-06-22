import time
from collections import defaultdict, deque
from typing import Dict

from fastapi import Request

class TokenBucket:
    def __init__(self, rate: float = 10, capacity: float = 10):
        self.rate = rate
        self.capacity = capacity
        self.buckets : Dict[str, deque] = defaultdict(deque)

    def allow_request(self, user_id: str) -> bool:
        """Return True if request is allowed, False if rate limited"""

        now = time.time()
        window_start = now - 60

        # Clean old timestamps
        bucket = self.buckets[user_id]

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) < self.rate:
            bucket.append(now)
            return True

        return False
    
rate_limiter = TokenBucket(rate=10, capacity=10)

async def rate_limit_chat(request: Request, call_next):

    """Middleware:  Enforce rate limits on chat endpoints"""

    # Only apply to chat message endpoint
    if "/api/v1/chat/message" not in request.url.path:
        return await call_next(request)
    
    # Extract electricity_id
    electricity_id = request.query_params.get("electricity_id") or \
                    (await request.json() if request.method == "POST" else {}).get("electricity_id")
    
    if not electricity_id:
        return await call_next(request)
    
    # Check rate limit
    if not rate_limiter.allow_request(electricity_id):

        from fastapi.responses import JSONResponse

        raise JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please wait before sending more messages."}
        )
    
    return await call_next(request)