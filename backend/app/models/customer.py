from typing import Optional
from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Customer(BaseModel):
    """
    SQLAlchemy 2.0 Customer Entity Model.
    Stores client shipping accounts, delivery locations, and contact details.
    """
    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, doc="Customer primary contact name"
    )
    company_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True, doc="Customer corporate company name"
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, doc="Customer email address"
    )
    phone: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="Customer phone number"
    )
    address: Mapped[str] = mapped_column(
        Text, nullable=False, doc="Physical delivery address"
    )
    latitude: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Geographic latitude coordinate"
    )
    longitude: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Geographic longitude coordinate"
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, doc="Special delivery instructions or account notes"
    )

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name='{self.name}', company='{self.company_name}')>"
