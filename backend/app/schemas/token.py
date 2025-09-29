from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: Optional[Dict[str, Any]] = None


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    user_role: Optional[str] = None


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: Optional[str] = None  # Subject (user ID)
    email: Optional[str] = None
    user_role: Optional[str] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None  # Token type (access/refresh)


class RefreshToken(BaseModel):
    """Schema for refresh token."""
    refresh_token: str


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: str


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class EmailVerification(BaseModel):
    """Schema for email verification."""
    token: str


class UserActivation(BaseModel):
    """Schema for user activation."""
    user_id: UUID
    is_active: bool
