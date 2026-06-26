import logging

from fastapi import APIRouter, HTTPException, Response, Depends

from src.models import UserRegister, UserLogin, UserResponse, LoginResponse
from src.services import auth_service, register_user, get_user_by_id
from src.api.deps import get_current_user
from src.services.auth_service import logout_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister):
    try:
        electricity_id = await register_user(data)
        user = await get_user_by_id(electricity_id)

        return user

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(data: UserLogin):
    """Login with electricity ID and receive JWT token"""

    try:
        return await auth_service.login_user(data.electricity_id)

    except HTTPException:
        raise


@router.get("download-id/{nic}")
async def download_id(nic: str):

    # find user by NIC and stream ID as .txt

    from src.db import SupabaseDB
    from src.utils import load_yaml

    config = load_yaml("db.yaml")["supabase"]
    
    res = SupabaseDB.table(config["table_users"]).select("electricity_id").eq("nic_number", nic).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="NIC not found")
    
    electricity_id = res.data[0]["electricity_id"]
    content = f"Your Electricity Platform ID:\n{electricity_id}\n\nUse this to log in."
    
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={nic}_id.txt"}
    )


# Endpoint for get current user profile
@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile (requires valid JWT)"""
    return {
        "electricity_id": current_user.electricity_id,
        "name": current_user.name,
        "phone_number": current_user.phone_number,
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user: end all active chat sessions.
    """

    try:
        await logout_user(current_user.electricity_id)
        return {"message": "Logged out successfully"}
    
    except Exception as e:
        logging.warning(f"Session cleanup failed during logout: {e}")
        return {"message": "Logged out (session cleanup skipped)"}