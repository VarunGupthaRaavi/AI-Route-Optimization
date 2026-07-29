import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.schemas.base import PaginatedResponse, ResponseModel
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer import CustomerService

router = APIRouter()


@router.get(
    "",
    response_model=ResponseModel[PaginatedResponse[CustomerResponse]],
    status_code=status.HTTP_200_OK,
    summary="List customers with pagination and filtering"
)
async def list_customers(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: Optional[str] = Query(default=None, description="Search term for name, company, or email"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[PaginatedResponse[CustomerResponse]]:
    request_id = getattr(request.state, "request_id", None)
    service = CustomerService(session=db)
    paginated = await service.get_paginated(page=page, page_size=page_size)
    
    # If search filter query parameter is present, search specifically
    if q:
        items, total, total_pages = await service.customer_repo.search_customers(query_str=q, page=page, page_size=page_size)
        paginated = PaginatedResponse(
            items=[CustomerResponse.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    else:
        paginated.items = [CustomerResponse.model_validate(i) for i in paginated.items]

    return ResponseModel(success=True, data=paginated, message="Customers retrieved successfully.", request_id=request_id)


@router.post(
    "",
    response_model=ResponseModel[CustomerResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer account"
)
async def create_customer(
    obj_in: CustomerCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[CustomerResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = CustomerService(session=db)
    customer = await service.create(obj_in)
    return ResponseModel(success=True, data=CustomerResponse.model_validate(customer), message="Customer created successfully.", request_id=request_id)


@router.get(
    "/{customer_id}",
    response_model=ResponseModel[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="Get customer details by ID"
)
async def get_customer(
    customer_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[CustomerResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = CustomerService(session=db)
    customer = await service.get_by_id(customer_id)
    return ResponseModel(success=True, data=CustomerResponse.model_validate(customer), message="Customer retrieved successfully.", request_id=request_id)


@router.put(
    "/{customer_id}",
    response_model=ResponseModel[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="Update customer details"
)
async def update_customer(
    customer_id: uuid.UUID,
    obj_in: CustomerUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[CustomerResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = CustomerService(session=db)
    customer = await service.update(customer_id, obj_in)
    return ResponseModel(success=True, data=CustomerResponse.model_validate(customer), message="Customer updated successfully.", request_id=request_id)


@router.delete(
    "/{customer_id}",
    response_model=ResponseModel[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete a customer account"
)
async def delete_customer(
    customer_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[bool]:
    request_id = getattr(request.state, "request_id", None)
    service = CustomerService(session=db)
    success = await service.delete(customer_id, soft=True)
    return ResponseModel(success=True, data=success, message="Customer deleted successfully.", request_id=request_id)
