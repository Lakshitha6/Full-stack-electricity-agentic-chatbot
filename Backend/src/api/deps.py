from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.utils.jwt_utils import verify_access_token
from src.services.auth_service import get_user_by_id

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    
    """
    Dependency: Validate JWT and return user data.
    Use this in route handlers that require authentication.
    """
    
    token = credentials.credentials
    payload = verify_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    electricity_id = payload.get("sub")
    if not electricity_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await get_user_by_id(electricity_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user