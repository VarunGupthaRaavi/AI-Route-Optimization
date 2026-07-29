from math import ceil
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic Abstract Repository Pattern implementation delivering standardized CRUD data access.
    """
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Retrieves a single record by its primary key ID.
        Filter out soft-deleted records if applicable.
        """
        # pyrefly: ignore [missing-attribute]
        query = select(self.model).where(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            # pyrefly: ignore [missing-attribute]
            query = query.where(self.model.is_deleted == False)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def exists(self, id: Any) -> bool:
        """
        Checks whether a non-deleted record exists matching the primary key ID.
        """
        entity = await self.get_by_id(id)
        return entity is not None

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Retrieves multiple records with optional pagination offsets and dictionary filtering.
        """
        query = select(self.model)
        if hasattr(self.model, "is_deleted"):
            # pyrefly: ignore [missing-attribute]
            query = query.where(self.model.is_deleted == False)

        if filters:
            for attr, value in filters.items():
                if hasattr(self.model, attr) and value is not None:
                    query = query.where(getattr(self.model, attr) == value)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Counts total active non-deleted records matching optional filter criteria.
        """
        # pyrefly: ignore [missing-attribute]
        query = select(func.count(self.model.id))
        if hasattr(self.model, "is_deleted"):
            # pyrefly: ignore [missing-attribute]
            query = query.where(self.model.is_deleted == False)

        if filters:
            for attr, value in filters.items():
                if hasattr(self.model, attr) and value is not None:
                    query = query.where(getattr(self.model, attr) == value)

        result = await self.session.execute(query)
        return result.scalar_one() or 0

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[ModelType], int, int]:
        """
        Retrieves paginated items along with total record count and total pages calculation.
        """
        page = max(1, page)
        page_size = max(1, page_size)
        skip = (page - 1) * page_size

        total = await self.count(filters=filters)
        items = await self.get_multi(skip=skip, limit=page_size, filters=filters)
        total_pages = ceil(total / page_size) if total > 0 else 0

        return items, total, total_pages

    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any], ModelType]) -> ModelType:
        """
        Creates and persists a new domain entity instance from a model instance, schema, or dictionary.
        """
        if isinstance(obj_in, self.model):
            db_obj = obj_in
        elif isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        elif hasattr(obj_in, "model_dump"):
            create_data = obj_in.model_dump(exclude_unset=True)
            db_obj = self.model(**create_data)
        else:
            db_obj = obj_in

        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        # pyrefly: ignore [bad-return]
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any], ModelType]
    ) -> ModelType:
        """
        Updates an existing model instance attributes from model instance, schema, or dictionary.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        elif hasattr(obj_in, "model_dump"):
            update_data = obj_in.model_dump(exclude_unset=True)
        elif hasattr(obj_in, "to_dict"):
            update_data = obj_in.to_dict()
        else:
            update_data = {k: v for k, v in obj_in.__dict__.items() if not k.startswith('_')}

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
