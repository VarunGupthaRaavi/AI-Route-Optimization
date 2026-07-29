from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.repositories.base import BaseRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository(BaseRepository[Customer, CustomerCreate, CustomerUpdate]):
    """
    Data repository for Customer entities.
    """
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Customer, session=session)

    async def search_customers(
        self,
        query_str: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Customer], int, int]:
        """
        Searches customer records by name, company, or email with pagination.
        """
        stmt = select(Customer).where(Customer.is_deleted == False)
        if query_str:
            q = f"%{query_str.strip()}%"
            stmt = stmt.where(
                (Customer.name.ilike(q)) |
                (Customer.company_name.ilike(q)) |
                (Customer.email.ilike(q))
            )
        
        # Calculate totals and paginated items
        items, total, total_pages = await self.get_paginated(
            page=page,
            page_size=page_size,
            filters=None
        )
        return items, total, total_pages
