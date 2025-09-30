from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    user_role: UserRole = UserRole.CITIZEN
    language_preference: str = Field(default="en", max_length=10)
    organization: Optional[str] = Field(None, max_length=100)
    verification_id: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    language_preference: Optional[str] = Field(None, max_length=10)
    organization: Optional[str] = Field(None, max_length=100)
    profile_picture_url: Optional[str] = Field(None, max_length=512)
    verification_id: Optional[str] = Field(None, max_length=100)
    is_verified_volunteer: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user data in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_verified: bool
    is_active: bool
    profile_picture_url: Optional[str] = None
    verification_id: Optional[str] = None
    is_verified_volunteer: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class User(UserInDB):
    """Schema for user data returned by API."""
    pass


class UserResponse(BaseModel):
    """Schema for user response (public data only)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: EmailStr
    full_name: str
    user_role: UserRole
    is_verified: bool
    is_active: bool
    profile_picture_url: Optional[str] = None
    organization: Optional[str] = None
    verification_id: Optional[str] = None
    is_verified_volunteer: bool
    created_at: datetime


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserPasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
