from math import ceil
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic Asynchronous Repository Pattern Implementation using SQLAlchemy 2.0.
    Provides standard CRUD, pagination, count, and soft-deletion operations.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        """
        Initializes the repository with target SQLAlchemy model class and active async session.
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Retrieves a single record by primary key identifier. Excludes soft-deleted entities if supported.
        """
        # pyrefly: ignore [missing-attribute]
        query = select(self.model).where(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Retrieves multiple records with optional offset, limit, and simple equality filtering.
        """
        query = select(self.model)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)

        if filters:
            for attr, val in filters.items():
                if hasattr(self.model, attr) and val is not None:
                    query = query.where(getattr(self.model, attr) == val)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ModelType], int, int]:
        """
        Retrieves paginated records returning (items, total_count, total_pages).
        """
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        skip = (page - 1) * page_size

        total = await self.count(filters=filters)
        items = await self.get_multi(skip=skip, limit=page_size, filters=filters)
        total_pages = ceil(total / page_size) if total > 0 else 0

        return items, total, total_pages

    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Creates and persists a new domain entity instance from a schema or dictionary.
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)

        db_obj = self.model(**create_data)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Updates an existing model instance attributes from schema or dictionary.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any, soft: bool = True) -> bool:
        """
        Deletes a record by identifier. Performs soft-delete by default if model supports it.
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False

        if soft and hasattr(db_obj, "is_deleted"):
            # pyrefly: ignore [missing-attribute]
            db_obj.is_deleted = True
            self.session.add(db_obj)
        else:
            await self.session.delete(db_obj)

        await self.session.flush()
        return True

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Returns total count of records matching criteria.
        """
        query = select(func.count()).select_from(self.model)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)

        if filters:
            for attr, val in filters.items():
                if hasattr(self.model, attr) and val is not None:
                    query = query.where(getattr(self.model, attr) == val)

        result = await self.session.execute(query)
        return result.scalar_one() or 0

    async def exists(self, id: Any) -> bool:
        """
        Checks if a record with given primary key exists.
        """
        # pyrefly: ignore [missing-attribute]
        query = select(self.model.id).where(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        result = await self.session.execute(query)
        return result.first() is not None
