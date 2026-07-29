import uuid
from datetime import datetime
from typing import Optional
from pydantic import Field
from app.models.driver import DriverStatus
from app.schemas.base import BaseSchema


class DriverBase(BaseSchema):
    user_id: Optional[uuid.UUID] = Field(default=None, description="Linked user account ID")
    license_number: str = Field(..., min_length=3, max_length=100, description="Commercial license ID")
    phone: str = Field(..., min_length=5, max_length=50, description="Contact phone number")
    status: DriverStatus = Field(default=DriverStatus.IDLE, description="Driver status")
    assigned_vehicle_id: Optional[uuid.UUID] = Field(default=None, description="Assigned vehicle ID")
    current_lat: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    current_lng: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    rating: float = Field(default=5.0, ge=1.0, le=5.0, description="Driver rating")


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseSchema):
    user_id: Optional[uuid.UUID] = Field(default=None)
    license_number: Optional[str] = Field(default=None, min_length=3, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=5, max_length=50)
    status: Optional[DriverStatus] = Field(default=None)
    assigned_vehicle_id: Optional[uuid.UUID] = Field(default=None)
    current_lat: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    current_lng: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)


class DriverResponse(DriverBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
