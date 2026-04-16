from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ============ TOKEN ============

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    username: Optional[str] = None


# ============ USER ============

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: str = "vendedor"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
