import jwt
from datetime import datetime, timedelta

from fastapi import HTTPException
from src.db.client import SupabaseDB
from src.utils.id_generator import generate_electricity_id
from src.utils.config_loader import get_env, load_yaml
from src.models.user import UserRegister, UserResponse
from src.utils.jwt_utils import create_access_token
from src.agents.memory_manager import end_session

config = load_yaml("db.yaml")["supabase"]
JWT_SECRET = get_env("JWT_SECRET", "dev-secret-change-in-prod")
JWT_EXPIRY_HOURS = get_env("JWT_EXPIRY_HOURS", 24)

async def register_user(data: UserRegister) -> str:

    # Check NIC is already exists 
    existing_nic = SupabaseDB.table(config["table_users"]).select("electricity_id").eq("nic_number", data.nic_number).execute()

    if existing_nic.data:
        raise HTTPException(status_code=409, detail="NIC number already registered")
    
    max_retries = config.get("retry_attempts", 3)
    electricity_id = None

    for _ in range(max_retries):
        candidate = generate_electricity_id()
        exists = SupabaseDB.table(config["table_users"]).select("electricity_id").eq("electricity_id", candidate).execute()
        if not exists.data:
            electricity_id = candidate
            break
    
    if not electricity_id:
        raise HTTPException(status_code=500, detail="Failed to generate unique ID")

    insert_data = {
        "electricity_id": electricity_id,
        "name": data.name,
        "phone_number": data.phone_number,
        "nic_number": data.nic_number
    }
    
    res = SupabaseDB.table(config["table_users"]).insert(insert_data).execute()

    if not res.data:
        raise HTTPException(status_code=500, detail="Database insertion failed")
    
    return electricity_id


async def get_user_by_id(electricity_id: str) -> UserResponse:
    res =  SupabaseDB.table(config["table_users"]).select("*").eq("electricity_id", electricity_id).execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
        
    return UserResponse(**res.data[0])


def generate_jwt(electricity_id: str) -> str:

    """Generate JWT for authenticated user
    
        Args:
            electricity_id (str): The unique electricity ID of the user to include in the JWT payload

        Returns:
            str: A JWT token string that includes the electricity_id and an expiration time

        The JWT payload includes:
            - `electricity_id`: The unique identifier for the user
            - `exp`: The expiration time of the token, set to current time + JWT_EXPIRY_HOURS
            - `iat`: The issued at time, set to the current time
    """


    payload = {
        "electricity_id": electricity_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.utcnow()
    }

    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


async def login_user(electricity_id: str) -> dict:

    """Authenticate user and return JWT token along with user info
    
        Args:
            electricity_id (str)
        
        Returns:
            dict: A dictionary containing user information and JWT token details:
                - `user`: A UserResponse object with the user's details
                - `access_token`: The JWT token string for authentication
                - `token_type`: The type of the token, typically "bearer"
    """

    user = await get_user_by_id(electricity_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Electricity ID")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.electricity_id},
        expires_delta=timedelta(minutes=1440)
    )

    return {
        "token": access_token,
        "token_type": "bearer",
        "user": {
            "electricity_id": user.electricity_id,
            "name": user.name,
            "phone_number": user.phone_number,
        }
    }


async def logout_user(electricity_id:str):
    """End all active sessions for user on logout"""

    try:
        # Find all active sessions
        res = SupabaseDB.table(config["table_chat_sessions"]).select("session_id").eq(
            "electricity_id", electricity_id
        ).eq("is_active", True).execute()
        
        if not res.data:
            return 0
        
        # End them all in one batch update
        session_ids = [s["session_id"] for s in res.data]
        SupabaseDB.table(config["table_chat_sessions"]).update({
            "is_active": False,
            "ended_at": datetime.utcnow().isoformat()
        }).in_("session_id", session_ids).execute()
        
        return len(session_ids)
    except Exception as e:
        print(f"Failed to end sessions for {electricity_id}: {e}")
        return 0