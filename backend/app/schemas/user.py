from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# Schema for Creating New User (Registration)
# ─────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    """
    Data required to register a new user
    """
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., min_length=6, max_length=100, example="password123")


# ─────────────────────────────────────────────────────────────
# Schema for User Login
# ─────────────────────────────────────────────────────────────
class UserLogin(BaseModel):
    """
    Data required to login
    """
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., example="password123")


# ─────────────────────────────────────────────────────────────
# Schema for Updating User
# ─────────────────────────────────────────────────────────────
class UserUpdate(BaseModel):
    """
    Data that can be updated (all fields optional)
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


# ─────────────────────────────────────────────────────────────
# Schema for User Response (What we send back to client)
# ─────────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    """
    User data sent back to client (NO PASSWORD!)
    """
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────
# Schema for Token Response (After Login)
# ─────────────────────────────────────────────────────────────
class Token(BaseModel):
    """
    JWT Token response after successful login
    """
    access_token: str
    token_type: str = "bearer"


# ─────────────────────────────────────────────────────────────
# Schema for Token Data (What's inside JWT)
# ─────────────────────────────────────────────────────────────
class TokenData(BaseModel):
    """
    Data stored inside JWT token
    """
    user_id: Optional[int] = None
    email: Optional[str] = None