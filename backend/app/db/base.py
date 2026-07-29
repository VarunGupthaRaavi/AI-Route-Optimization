"""
Central SQLAlchemy Metadata Registry for Alembic Schema Autogeneration.
Imports all models so Base.metadata is fully populated.
"""
from app.models.base import Base  # noqa

# Future model imports will be registered here for Alembic auto-discovery
