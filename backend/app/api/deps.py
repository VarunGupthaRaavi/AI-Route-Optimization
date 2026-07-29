from typing import AsyncGenerator, Dict, Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings, get_settings
from app.core.database import get_async_db
from app.core.exceptions import AuthenticationException
from app.core.security import decode_token

# Bearer Token Scheme for FastAPI OpenAPI documentation
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
