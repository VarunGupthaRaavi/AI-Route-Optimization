import uuid
from datetime import datetime
from typing import Optional
from pydantic import Field
from app.models.delivery import DeliveryPriority, DeliveryStatus
from app.schemas.base import BaseSchema


class DeliveryBase(BaseSchema):
    tracking_number: Optional[str] = Field(default=None, description="Auto-generated or custom tracking number")
    customer_id: uuid.UUID = Field(..., description="Customer ID")
    pickup_address: str = Field(..., min_length=5, description="Pickup address")
    delivery_address: str = Field(..., min_length=5, description="Delivery address")
    pickup_lat: float = Field(..., ge=-90.0, le=90.0)
    pickup_lng: float = Field(..., ge=-180.0, le=180.0)
    delivery_lat: float = Field(..., ge=-90.0, le=90.0)
    delivery_lng: float = Field(..., ge=-180.0, le=180.0)
    weight_kg: float = Field(..., gt=0.0, description="Package weight in kg")
    volume_m3: float = Field(default=0.1, gt=0.0, description="Package volume in m3")
    status: DeliveryStatus = Field(default=DeliveryStatus.PENDING, description="Delivery status")
    priority: DeliveryPriority = Field(default=DeliveryPriority.MEDIUM, description="Priority level")
    scheduled_date: Optional[datetime] = Field(default=None, description="Scheduled delivery timestamp")
    notes: Optional[str] = Field(default=None, description="Special delivery instructions")


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseSchema):
    pickup_address: Optional[str] = Field(default=None, min_length=5)
    delivery_address: Optional[str] = Field(default=None, min_length=5)
    pickup_lat: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    pickup_lng: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    delivery_lat: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    delivery_lng: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    weight_kg: Optional[float] = Field(default=None, gt=0.0)
    volume_m3: Optional[float] = Field(default=None, gt=0.0)
    status: Optional[DeliveryStatus] = Field(default=None)
    priority: Optional[DeliveryPriority] = Field(default=None)
    scheduled_date: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class DeliveryScheduleRequest(BaseSchema):
    scheduled_date: datetime = Field(..., description="Target delivery date and time")


class DeliveryResponse(DeliveryBase):
    id: uuid.UUID
    tracking_number: str
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
