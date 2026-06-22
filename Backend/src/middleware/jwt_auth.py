import os
from dotenv import load_dotenv
load_dotenv()

import jwt
from fastapi import Request, HTTPException, status

from src.utils.config_loader import get_env

JWT_SECRET = get_env("JWT_SECRET", "secret_key")
JWT_ALGORITHM = get_env("JWT_ALGORITHM", "HS256")
APP_ENV = os.getenv("APP_ENV", "development")

async def jwt_auth_middleware(request: Request, call_next):
    """Extract JWT from Authorization header"""

    # Skip auth for health checks and auth endpoints
    skip_paths = ["/health", "/ready", "/metrics", "/api/v1/auth/register", "/api/v1/auth/login"]
    if request.url.path in skip_paths or APP_ENV == "testing":
        return await call_next(request)
    
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authorization header"
        )

    token = auth_header.split(" ")[1] # Get the token part - split "Bearer abc.xyz.123" into ["Bearer", "abc.xyz.123"] 


    # Decode the JWT token and store electricity_id in request state for later use in endpoints
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        electricity_id = payload.get("electricity_id")

        if not electricity_id or not electricity_id.startswith("ELEC-"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing electricity_id"
            )
        
        from src.db.client import SupabaseDB

        # Attach the electricity_id to the request state
        request.state.electricity_id = electricity_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return await call_next(request)