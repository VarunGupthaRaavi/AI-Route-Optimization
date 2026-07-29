from typing import Any, Dict
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db_session, require_roles
from app.models.user import User, UserRole
from app.schemas.base import ResponseModel
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=ResponseModel[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Registers a new platform user with hashed password and assigns an enterprise authorization role."
)
async def register(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> ResponseModel[UserResponse]:
    """
    User Registration Endpoint.
    """
    request_id = getattr(request.state, "request_id", None)
    auth_service = AuthService(session=db)
    user_response = await auth_service.register_user(user_in)

    return ResponseModel(
        success=True,
        data=user_response,
        message="User account registered successfully.",
        request_id=request_id
    )


@router.post(
    "/login",
    response_model=ResponseModel[Token],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT tokens",
    description="Validates email and password credentials, returning signed JWT Access and Refresh tokens."
)
async def login(
    login_in: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> ResponseModel[Token]:
    """
    User Authentication & Token Issuance Endpoint.
    """
    request_id = getattr(request.state, "request_id", None)
    auth_service = AuthService(session=db)
    token_response = await auth_service.authenticate_user(login_in)

    return ResponseModel(
        success=True,
        data=token_response,
        message="Authentication successful.",
        request_id=request_id
    )


@router.get(
    "/me",
    response_model=ResponseModel[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user profile",
    description="Returns profile attributes of the currently authenticated user based on JWT Bearer token."
)
async def get_me(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> ResponseModel[UserResponse]:
    """
    Authenticated User Profile Endpoint.
    """
    request_id = getattr(request.state, "request_id", None)
    user_response = UserResponse.model_validate(current_user)

    return ResponseModel(
        success=True,
        data=user_response,
        message="Current user profile retrieved successfully.",
        request_id=request_id
    )


@router.get(
    "/admin-only",
    response_model=ResponseModel[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Role-Based Access Control (RBAC) Admin Verification",
    description="Restricted test endpoint accessible exclusively by users holding the ADMIN role."
)
async def admin_only_endpoint(
    request: Request,
    admin_user: User = Depends(require_roles(UserRole.ADMIN))
) -> ResponseModel[Dict[str, Any]]:
    """
    RBAC Protected Verification Endpoint.
    """
    request_id = getattr(request.state, "request_id", None)
    return ResponseModel(
        success=True,
        data={
            "admin_user_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "role": admin_user.role.value,
            "access_granted": True
        },
        message="Access granted to ADMIN role restricted resource.",
        request_id=request_id
    )
