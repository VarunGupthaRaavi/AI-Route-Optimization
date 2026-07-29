import uuid
from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
from app.models.user import UserRole
from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    """
    Base User Schema shared across request and response contracts.
    """
    email: EmailStr = Field(..., description="User primary email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")


class UserCreate(UserBase):
    """
    Schema for User Registration request payload.
    """
    password: str = Field(..., min_length=8, max_length=128, description="Plaintext account password")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="Target enterprise authorization role")


class UserUpdate(BaseSchema):
    """
    Schema for updating user details.
    """
    email: Optional[EmailStr] = Field(default=None, description="Updated user email address")
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100, description="Updated user full name")
    password: Optional[str] = Field(default=None, min_length=8, max_length=128, description="Updated plaintext password")
    role: Optional[UserRole] = Field(default=None, description="Updated enterprise role")
    is_active: Optional[bool] = Field(default=None, description="Updated activation status")


class UserLogin(BaseSchema):
    """
    Schema for User Login request payload.
    """
    email: EmailStr = Field(..., description="User login email address")
    password: str = Field(..., description="Plaintext account password")


class UserResponse(UserBase):
    """
    Schema for User profile API response serialization.
    """
    id: uuid.UUID = Field(..., description="User unique primary identifier")
    role: UserRole = Field(..., description="Assigned enterprise authorization role")
    is_active: bool = Field(..., description="Account active indicator")
    is_verified: bool = Field(..., description="Email verification indicator")
    last_login_at: Optional[datetime] = Field(default=None, description="UTC timestamp of last login")
    created_at: datetime = Field(..., description="UTC timestamp of entity creation")
    updated_at: datetime = Field(..., description="UTC timestamp of last modification")


class Token(BaseSchema):
    """
    Schema for JWT Authentication Token pair response payload.
    """
    access_token: str = Field(..., description="Signed JWT Access Token (short-lived)")
    refresh_token: str = Field(..., description="Signed JWT Refresh Token (long-lived)")
    token_type: str = Field(default="bearer", description="Token authentication scheme")
    expires_in: int = Field(..., description="Access token expiration duration in seconds")
    user: UserResponse = Field(..., description="Authenticated user profile details")


class TokenData(BaseSchema):
    """
    Internal Schema representing decoded JWT token payload claims.
    """
    sub: Optional[str] = Field(default=None, description="Subject identifier (user UUID string)")
    role: Optional[str] = Field(default=None, description="Token user role claim")
    type: Optional[str] = Field(default=None, description="Token type (access or refresh)")
