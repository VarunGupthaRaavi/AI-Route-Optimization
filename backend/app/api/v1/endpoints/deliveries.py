import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db_session
from app.models.delivery import DeliveryPriority, DeliveryStatus
from app.models.user import User
from app.schemas.base import PaginatedResponse, ResponseModel
from app.schemas.delivery import DeliveryCreate, DeliveryResponse, DeliveryScheduleRequest, DeliveryUpdate
from app.services.delivery import DeliveryService

router = APIRouter()


@router.get(
    "",
    response_model=ResponseModel[PaginatedResponse[DeliveryResponse]],
    status_code=status.HTTP_200_OK,
    summary="List delivery orders with pagination and filtering"
)
async def list_deliveries(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[DeliveryStatus] = Query(default=None, alias="status"),
    priority_filter: Optional[DeliveryPriority] = Query(default=None, alias="priority"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[PaginatedResponse[DeliveryResponse]]:
    request_id = getattr(request.state, "request_id", None)
    service = DeliveryService(session=db)
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    if priority_filter:
        filters["priority"] = priority_filter

    paginated = await service.get_paginated(page=page, page_size=page_size, filters=filters if filters else None)
    paginated.items = [DeliveryResponse.model_validate(i) for i in paginated.items]
    return ResponseModel(success=True, data=paginated, message="Deliveries retrieved successfully.", request_id=request_id)


@router.post(
    "",
    response_model=ResponseModel[DeliveryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new delivery order"
)
async def create_delivery(
    obj_in: DeliveryCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[DeliveryResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = DeliveryService(session=db)
    delivery = await service.create(obj_in)
    return ResponseModel(success=True, data=DeliveryResponse.model_validate(delivery), message="Delivery created successfully.", request_id=request_id)


@router.get(
    "/{delivery_id}",
    response_model=ResponseModel[DeliveryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get delivery details by ID"
)
async def get_delivery(
    delivery_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[DeliveryResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = DeliveryService(session=db)
    delivery = await service.get_by_id(delivery_id)
    return ResponseModel(success=True, data=DeliveryResponse.model_validate(delivery), message="Delivery retrieved successfully.", request_id=request_id)


@router.put(
    "/{delivery_id}",
    response_model=ResponseModel[DeliveryResponse],
    status_code=status.HTTP_200_OK,
    summary="Update delivery details"
)
async def update_delivery(
    delivery_id: uuid.UUID,
    obj_in: DeliveryUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[DeliveryResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = DeliveryService(session=db)
    delivery = await service.update(delivery_id, obj_in)
    return ResponseModel(success=True, data=DeliveryResponse.model_validate(delivery), message="Delivery updated successfully.", request_id=request_id)


@router.post(
    "/{delivery_id}/schedule",
    response_model=ResponseModel[DeliveryResponse],
    status_code=status.HTTP_200_OK,
    summary="Schedule delivery time window"
)
async def schedule_delivery(
    delivery_id: uuid.UUID,
    sched_req: DeliveryScheduleRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[DeliveryResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = DeliveryService(session=db)
    delivery = await service.schedule_delivery(delivery_id, sched_req.scheduled_date)
    return ResponseModel(success=True, data=DeliveryResponse.model_validate(delivery), message="Delivery scheduled successfully.", request_id=request_id)


@router.delete(
    "/{delivery_id}",
    response_model=ResponseModel[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete a delivery order"
)
async def delete_delivery(
    delivery_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[bool]:
    request_id = getattr(request.state, "request_id", None)
    service = DeliveryService(session=db)
    success = await service.delete(delivery_id, soft=True)
    return ResponseModel(success=True, data=success, message="Delivery deleted successfully.", request_id=request_id)
