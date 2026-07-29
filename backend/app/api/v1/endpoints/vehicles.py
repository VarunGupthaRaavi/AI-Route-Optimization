import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.models.vehicle import VehicleStatus
from app.schemas.base import PaginatedResponse, ResponseModel
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate
from app.services.vehicle import VehicleService

router = APIRouter()


@router.get(
    "",
    response_model=ResponseModel[PaginatedResponse[VehicleResponse]],
    status_code=status.HTTP_200_OK,
    summary="List fleet vehicles with pagination and status filtering"
)
async def list_vehicles(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[VehicleStatus] = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[PaginatedResponse[VehicleResponse]]:
    request_id = getattr(request.state, "request_id", None)
    service = VehicleService(session=db)
    filters = {"status": status_filter} if status_filter else None
    paginated = await service.get_paginated(page=page, page_size=page_size, filters=filters)
    paginated.items = [VehicleResponse.model_validate(i) for i in paginated.items]
    return ResponseModel(success=True, data=paginated, message="Vehicles retrieved successfully.", request_id=request_id)


@router.post(
    "",
    response_model=ResponseModel[VehicleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fleet vehicle"
)
async def create_vehicle(
    obj_in: VehicleCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[VehicleResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = VehicleService(session=db)
    vehicle = await service.create(obj_in)
    return ResponseModel(success=True, data=VehicleResponse.model_validate(vehicle), message="Vehicle created successfully.", request_id=request_id)


@router.get(
    "/{vehicle_id}",
    response_model=ResponseModel[VehicleResponse],
    status_code=status.HTTP_200_OK,
    summary="Get vehicle details by ID"
)
async def get_vehicle(
    vehicle_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[VehicleResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = VehicleService(session=db)
    vehicle = await service.get_by_id(vehicle_id)
    return ResponseModel(success=True, data=VehicleResponse.model_validate(vehicle), message="Vehicle retrieved successfully.", request_id=request_id)


@router.put(
    "/{vehicle_id}",
    response_model=ResponseModel[VehicleResponse],
    status_code=status.HTTP_200_OK,
    summary="Update vehicle details"
)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    obj_in: VehicleUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[VehicleResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = VehicleService(session=db)
    vehicle = await service.update(vehicle_id, obj_in)
    return ResponseModel(success=True, data=VehicleResponse.model_validate(vehicle), message="Vehicle updated successfully.", request_id=request_id)


@router.delete(
    "/{vehicle_id}",
    response_model=ResponseModel[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete a vehicle from fleet"
)
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[bool]:
    request_id = getattr(request.state, "request_id", None)
    service = VehicleService(session=db)
    success = await service.delete(vehicle_id, soft=True)
    return ResponseModel(success=True, data=success, message="Vehicle deleted successfully.", request_id=request_id)
