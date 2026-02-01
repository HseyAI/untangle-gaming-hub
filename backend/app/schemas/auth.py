"""
Pydantic schemas for authentication.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: Optional[str] = Field(default="staff", pattern="^(admin|manager|staff)$")


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    full_name: Optional[str]
    role: str
    branch_id: Optional[str]
    is_active: bool
    is_verified: bool
    oauth_provider: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Schema for password change."""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class GoogleOAuthCallback(BaseModel):
    """Schema for Google OAuth callback."""
    code: str
    state: Optional[str] = None
