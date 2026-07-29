import uuid
from typing import AsyncGenerator, Dict, Any, List, Callable
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings, get_settings
from app.core.database import get_async_db
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.repositories.user import UserRepository

# Bearer Token Scheme for FastAPI OpenAPI Swagger documentation
security_bearer = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency returning an asynchronous SQLAlchemy database session.
    Delegates to core get_async_db context generator.
    """
    async for session in get_async_db():
        yield session


def get_app_settings() -> Settings:
    """
    Dependency injecting project application settings.
    """
    return get_settings()


async def get_current_user_claims(
    auth: HTTPAuthorizationCredentials = Depends(security_bearer)
) -> Dict[str, Any]:
    """
    Dependency validating the JWT Bearer authentication token and returning token payload claims.
    Raises AuthenticationException (HTTP 401) on invalid or missing tokens.
    """
    if not auth or not auth.credentials:
        raise AuthenticationException("Authorization header with Bearer token is missing.")

    try:
        payload = decode_token(auth.credentials)
        token_type = payload.get("type")
        if token_type != "access":
            raise AuthenticationException("Invalid token type. Expected access token.")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Token claim payload missing subject identifier.")
            
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("JWT Access token has expired. Please refresh your session.")
    except jwt.PyJWTError:
        raise AuthenticationException("Could not validate JWT credentials signature.")


async def get_current_user(
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency loading the active User database entity matching the authenticated JWT token subject.
    """
    user_id_str = claims.get("sub")
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise AuthenticationException("Invalid user identifier in token payload.")

    repo = UserRepository(session=db)
    user = await repo.get_by_id(user_id)

    if not user:
        raise AuthenticationException("Authenticated user account no longer exists.")

    if not user.is_active:
        raise AuthenticationException("Authenticated user account has been disabled.")

    return user


def require_roles(*allowed_roles: UserRole) -> Callable[..., User]:
    """
    Dependency Factory for Role-Based Access Control (RBAC) authorization.
    Restricts endpoint execution to users possessing one of the specified allowed roles.
    ADMIN role possesses superuser authorization across all endpoints.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_val = current_user.role.value if isinstance(current_user.role, UserRole) else str(current_user.role)
        allowed_vals = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]
        
        # ADMIN role possesses superuser authorization across all endpoints
        if user_role_val != UserRole.ADMIN.value and user_role_val not in allowed_vals:
            raise AuthorizationException(
                f"Access forbidden: Required role in {allowed_vals}, but user holds role '{user_role_val}'."
            )
        return current_user

    # pyrefly: ignore [bad-return]
    return role_checker
