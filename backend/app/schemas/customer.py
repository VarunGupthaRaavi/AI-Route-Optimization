import uuid
from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
from app.schemas.base import BaseSchema


class CustomerBase(BaseSchema):
    name: str = Field(..., min_length=2, max_length=255, description="Customer contact name")
    company_name: Optional[str] = Field(default=None, max_length=255, description="Corporate company name")
    email: EmailStr = Field(..., description="Contact email address")
    phone: str = Field(..., min_length=5, max_length=50, description="Phone number")
    address: str = Field(..., min_length=5, description="Physical delivery address")
    latitude: Optional[float] = Field(default=41.8781, ge=-90.0, le=90.0, description="Geographic latitude")
    longitude: Optional[float] = Field(default=-87.6298, ge=-180.0, le=180.0, description="Geographic longitude")
    notes: Optional[str] = Field(default=None, description="Account notes or instructions")


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseSchema):
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    company_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None)
    phone: Optional[str] = Field(default=None, min_length=5, max_length=50)
    address: Optional[str] = Field(default=None, min_length=5)
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    notes: Optional[str] = Field(default=None)


class CustomerResponse(CustomerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
