import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, Enum as SQLEnum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class DeliveryStatus(str, Enum):
    """
    Delivery package lifecycle status enumeration.
    """
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class DeliveryPriority(str, Enum):
    """
    Delivery dispatch priority classification.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Delivery(BaseModel):
    """
    SQLAlchemy 2.0 Delivery Entity Model.
    Represents package orders, pickup and drop-off coordinates, payload specs, and delivery status.
    """
    __tablename__ = "deliveries"

    tracking_number: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False, doc="Unique shipment tracking identifier"
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Associated customer ID"
    )
    pickup_address: Mapped[str] = mapped_column(
        Text, nullable=False, doc="Origin pickup address"
    )
    delivery_address: Mapped[str] = mapped_column(
        Text, nullable=False, doc="Destination delivery address"
    )
    pickup_lat: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Origin latitude coordinate"
    )
    pickup_lng: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Origin longitude coordinate"
    )
    delivery_lat: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Destination latitude coordinate"
    )
    delivery_lng: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Destination longitude coordinate"
    )
    weight_kg: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Package weight in kilograms"
    )
    volume_m3: Mapped[float] = mapped_column(
        Float, default=0.1, nullable=False, doc="Package volume in cubic meters"
    )
    status: Mapped[DeliveryStatus] = mapped_column(
        SQLEnum(DeliveryStatus, name="deliverystatus", native_enum=False, length=50),
        default=DeliveryStatus.PENDING,
        nullable=False,
        index=True,
        doc="Current package delivery lifecycle status"
    )
    priority: Mapped[DeliveryPriority] = mapped_column(
        SQLEnum(DeliveryPriority, name="deliverypriority", native_enum=False, length=50),
        default=DeliveryPriority.MEDIUM,
        nullable=False,
        index=True,
        doc="Dispatch priority tier"
    )
    scheduled_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="Target scheduled delivery window timestamp"
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="UTC timestamp when package was successfully delivered"
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, doc="Special handling instructions or delivery notes"
    )

    def __repr__(self) -> str:
        return f"<Delivery(id={self.id}, tracking='{self.tracking_number}', status='{self.status}')>"
