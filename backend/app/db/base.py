"""
Central SQLAlchemy Metadata Registry for Alembic Schema Autogeneration.
Imports all models so Base.metadata is fully populated.
"""
from app.models.base import Base  # noqa
from app.models.user import User, UserRole  # noqa

__all__ = ["Base", "User", "UserRole"]
