from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel
from app.core.exceptions import EntityNotFoundException
from app.models.base import Base
from app.repositories.base import BaseRepository
from app.schemas.base import PaginatedResponse

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic Abstract Business Service Layer encapsulating data access repositories.
    Translates repository outputs into business contracts and handles entity validation.
    """

    def __init__(self, repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]) -> None:
        """
        Initializes service with an injected concrete repository implementation.
        """
        self.repository = repository

    async def get_by_id(self, id: Any) -> ModelType:
        """
        Retrieves an entity by ID or raises EntityNotFoundException.
        """
        entity = await self.repository.get_by_id(id)
        if not entity:
            raise EntityNotFoundException(
                entity_name=self.repository.model.__name__,
                entity_id=id
            )
        return entity

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Retrieves multiple entities.
        """
        return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> PaginatedResponse[Any]:
        """
        Retrieves paginated entities wrapped in a standardized Pydantic PaginatedResponse envelope.
        """
        items, total, total_pages = await self.repository.get_paginated(
            page=page,
            page_size=page_size,
            filters=filters
        )
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )

    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Executes business creation workflow.
        """
        return await self.repository.create(obj_in)

    async def update(
        self,
        id: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Executes business update workflow after ensuring target entity exists.
        """
        entity = await self.get_by_id(id)
        return await self.repository.update(entity, obj_in)

    async def delete(self, id: Any, soft: bool = True) -> bool:
        """
        Executes entity deletion. Raises EntityNotFoundException if missing.
        """
        entity = await self.get_by_id(id)
        # pyrefly: ignore [missing-attribute]
        return await self.repository.delete(entity.id, soft=soft)
