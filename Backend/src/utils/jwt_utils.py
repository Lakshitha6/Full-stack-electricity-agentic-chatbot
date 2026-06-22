from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from src.utils.config_loader import get_jwt_settings

JWT_SETTINGS = get_jwt_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:

    """Create a JWT access token with the given data and expiration time."""

    to_encode = data.copy()
    
    # Set expiry
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_SETTINGS["access_token_expire_minutes"])
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    # Encode token
    encoded_jwt = jwt.encode(
        to_encode, 
        JWT_SETTINGS["secret_key"], 
        algorithm=JWT_SETTINGS["algorithm"]
    )
    return encoded_jwt


def verify_access_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT access token"""
    
    try:
        payload = jwt.decode(
            token, 
            JWT_SETTINGS["secret_key"], 
            algorithms=[JWT_SETTINGS["algorithm"]]
        )
        return payload
    except JWTError:
        return None