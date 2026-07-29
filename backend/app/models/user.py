from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class UserRole(str, Enum):
    """
    Enterprise Role-Based Access Control (RBAC) Enumeration for RouteAI.
    """
    ADMIN = "ADMIN"
    DISPATCHER = "DISPATCHER"
    DRIVER = "DRIVER"
    CUSTOMER = "CUSTOMER"


class User(BaseModel):
    """
    SQLAlchemy 2.0 User Domain Entity Model.
    Represents authenticated platform accounts across system roles.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="Unique user login email address"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt salted password digest"
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="User first and last name"
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="userrole", native_enum=True),
        default=UserRole.CUSTOMER,
        nullable=False,
        index=True,
        doc="Enterprise security authorization role"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        doc="Account activation status indicator"
    )
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        doc="Email verification status indicator"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="UTC timestamp of last successful user login"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
