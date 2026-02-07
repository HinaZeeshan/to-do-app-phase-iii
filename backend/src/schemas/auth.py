"""
Authentication request/response schemas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID


class SignupRequest(BaseModel):
    """Request schema for user signup."""
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

    @validator("email")
    def validate_email(cls, v):
        """Validate email format."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @validator("password")
    def validate_password(cls, v):
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class SignupResponse(BaseModel):
    """Response schema for successful signup."""
    user_id: UUID
    email: str
    token: str
    refresh_token: str


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)

    @validator("email")
    def validate_email(cls, v):
        """Validate email format."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()


class LoginResponse(BaseModel):
    """Response schema for successful login."""
    user_id: UUID
    email: str
    token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token."""
    refresh_token: str = Field(..., min_length=1)


class RefreshTokenResponse(BaseModel):
    """Response schema for successful token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    """Response schema for successful logout."""
    message: str = "Logged out successfully"