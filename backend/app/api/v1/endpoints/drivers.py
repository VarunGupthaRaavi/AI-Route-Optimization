import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db_session
from app.models.driver import DriverStatus
from app.models.user import User
from app.schemas.base import PaginatedResponse, ResponseModel
from app.schemas.driver import DriverCreate, DriverResponse, DriverUpdate
from app.services.driver import DriverService

router = APIRouter()


@router.get(
    "",
    response_model=ResponseModel[PaginatedResponse[DriverResponse]],
    status_code=status.HTTP_200_OK,
    summary="List fleet drivers with pagination and status filtering"
)
async def list_drivers(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[DriverStatus] = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[PaginatedResponse[DriverResponse]]:
    request_id = getattr(request.state, "request_id", None)
    service = DriverService(session=db)
    filters = {"status": status_filter} if status_filter else None
    paginated = await service.get_paginated(page=page, page_size=page_size, filters=filters)
    paginated.items = [DriverResponse.model_validate(i) for i in paginated.items]
    return ResponseModel(success=True, data=paginated, message="Drivers retrieved successfully.", request_id=request_id)


@router.post(
    "",
    response_model=ResponseModel[DriverResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new fleet driver"
)
async def create_driver(
    obj_in: DriverCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[DriverResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = DriverService(session=db)
    driver = await service.create(obj_in)
    return ResponseModel(success=True, data=DriverResponse.model_validate(driver), message="Driver registered successfully.", request_id=request_id)


@router.get(
    "/{driver_id}",
    response_model=ResponseModel[DriverResponse],
    status_code=status.HTTP_200_OK,
    summary="Get driver details by ID"
)
async def get_driver(
    driver_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[DriverResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = DriverService(session=db)
    driver = await service.get_by_id(driver_id)
    return ResponseModel(success=True, data=DriverResponse.model_validate(driver), message="Driver retrieved successfully.", request_id=request_id)


@router.put(
    "/{driver_id}",
    response_model=ResponseModel[DriverResponse],
    status_code=status.HTTP_200_OK,
    summary="Update driver details"
)
async def update_driver(
    driver_id: uuid.UUID,
    obj_in: DriverUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[DriverResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = DriverService(session=db)
    driver = await service.update(driver_id, obj_in)
    return ResponseModel(success=True, data=DriverResponse.model_validate(driver), message="Driver updated successfully.", request_id=request_id)


@router.delete(
    "/{driver_id}",
    response_model=ResponseModel[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete a driver profile"
)
async def delete_driver(
    driver_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[bool]:
    request_id = getattr(request.state, "request_id", None)
    service = DriverService(session=db)
    success = await service.delete(driver_id, soft=True)
    return ResponseModel(success=True, data=success, message="Driver deleted successfully.", request_id=request_id)
