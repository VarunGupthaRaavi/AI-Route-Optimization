import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db_session
from app.models.route import RouteStatus
from app.models.user import User
from app.schemas.base import PaginatedResponse, ResponseModel
from app.schemas.route import DriverAllocationRequest, RouteOptimizeRequest, RouteResponse, RouteUpdate
from app.services.route import RouteService

router = APIRouter()


@router.get(
    "",
    response_model=ResponseModel[PaginatedResponse[RouteResponse]],
    status_code=status.HTTP_200_OK,
    summary="List route plans with pagination and status filtering"
)
async def list_routes(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[RouteStatus] = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[PaginatedResponse[RouteResponse]]:
    request_id = getattr(request.state, "request_id", None)
    service = RouteService(session=db)
    filters = {"status": status_filter} if status_filter else None
    paginated = await service.get_paginated(page=page, page_size=page_size, filters=filters)
    paginated.items = [RouteResponse.model_validate(r) for r in paginated.items]
    return ResponseModel(success=True, data=paginated, message="Routes retrieved successfully.", request_id=request_id)


@router.post(
    "/optimize",
    response_model=ResponseModel[RouteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="AI Route Optimization: Generate optimal multi-stop logistics route"
)
async def optimize_route(
    req: RouteOptimizeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[RouteResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = RouteService(session=db)
    route_response = await service.optimize_route(req)
    return ResponseModel(success=True, data=route_response, message="Route optimization completed successfully.", request_id=request_id)


@router.get(
    "/{route_id}",
    response_model=ResponseModel[RouteResponse],
    status_code=status.HTTP_200_OK,
    summary="Get route plan details and ordered stops"
)
async def get_route(
    route_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[RouteResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = RouteService(session=db)
    route_response = await service.get_route_details(route_id)
    return ResponseModel(success=True, data=route_response, message="Route details retrieved successfully.", request_id=request_id)


@router.post(
    "/{route_id}/allocate-driver",
    response_model=ResponseModel[RouteResponse],
    status_code=status.HTTP_200_OK,
    summary="Allocate driver and vehicle to route"
)
async def allocate_driver(
    route_id: uuid.UUID,
    alloc_req: DriverAllocationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[RouteResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = RouteService(session=db)
    route_response = await service.allocate_driver(route_id, driver_id=alloc_req.driver_id, vehicle_id=alloc_req.vehicle_id)
    return ResponseModel(success=True, data=route_response, message="Driver and vehicle allocated to route.", request_id=request_id)


@router.delete(
    "/{route_id}",
    response_model=ResponseModel[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete a route plan"
)
async def delete_route(
    route_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[bool]:
    request_id = getattr(request.state, "request_id", None)
    service = RouteService(session=db)
    success = await service.delete(route_id, soft=True)
    return ResponseModel(success=True, data=success, message="Route deleted successfully.", request_id=request_id)
