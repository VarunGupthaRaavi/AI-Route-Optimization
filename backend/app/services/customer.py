from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.base import BaseService


class CustomerService(BaseService[Customer, CustomerCreate, CustomerUpdate]):
    """
    Business logic service for Customer operations.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.customer_repo = CustomerRepository(session=session)
        super().__init__(repository=self.customer_repo)
