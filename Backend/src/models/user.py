from pydantic import BaseModel, Field
from typing import Optional

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    phone_number: str = Field(..., pattern=r"^\+?[0-9\s\-]{7,15}$")
    nic_number: str = Field(..., min_length=5, max_length=20)

class UserLogin(BaseModel):
    electricity_id: str = Field(..., pattern=r"^ELEC-\d{6}$")

class UserResponse(BaseModel):
    electricity_id: str
    name: str
    phone_number: str
    nic_number: str
    created_at: str

class AuthError(BaseModel):
    detail: str
    code: str

class LoginResponse(BaseModel):
    token: str
    token_type: str
    user: dict