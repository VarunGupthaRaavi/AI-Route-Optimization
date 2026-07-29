from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger


class AppException(Exception):
    """
    Base domain exception for all RouteAI application business failures.
    """
    def __init__(
        self,
        message: str = "An unexpected application error occurred.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class EntityNotFoundException(AppException):
    """
    Raised when a requested domain entity (user, route, vehicle, etc.) is missing.
    """
    def __init__(
        self,
        entity_name: str = "Entity",
        entity_id: Any = None,
        message: Optional[str] = None
    ) -> None:
        msg = message or f"{entity_name} with identifier '{entity_id}' was not found."
        super().__init__(
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ENTITY_NOT_FOUND",
            details={"entity_name": entity_name, "entity_id": str(entity_id) if entity_id else None}
        )


class DatabaseException(AppException):
    """
    Raised when a database operational error occurs.
    """
    def __init__(self, message: str = "A database operation failed.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR"
        )


class ValidationException(AppException):
    """
    Raised when domain business rules input validation fails.
    """
    def __init__(self, message: str = "Domain validation failed.", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            error_code="BUSINESS_VALIDATION_ERROR",
            details=details
        )


class AuthenticationException(AppException):
    """
    Raised when user authentication credentials are invalid or expired.
    """
    def __init__(self, message: str = "Authentication failed. Invalid or expired token.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHENTICATED"
        )


class AuthorizationException(AppException):
    """
    Raised when an authenticated user lacks required RBAC role permissions.
    """
    def __init__(self, message: str = "Access denied. Insufficient permissions for this action.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )


def build_error_payload(
    status_code: int,
    error_code: str,
    message: str,
    request_id: str = "",
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Utility producing a uniform error JSON structure across all API responses.
    """
    return {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "status_code": status_code,
            "request_id": request_id
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers custom exception handlers on the FastAPI application instance.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "")
        logger.warning(
            f"AppException [{exc.error_code}] on {request.method} {request.url.path}: {exc.message}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_payload(
                status_code=exc.status_code,
                error_code=exc.error_code,
                message=exc.message,
                request_id=request_id,
                details=exc.details
            )
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "")
        error_code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "NOT_FOUND"
        elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
            error_code = "UNAUTHORIZED"

        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_payload(
                status_code=exc.status_code,
                error_code=error_code,
                message=str(exc.detail),
                request_id=request_id
            )
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "")
        formatted_errors = []
        for err in exc.errors():
            loc_parts = [str(x) for x in err.get("loc", []) if str(x) not in ("body", "query", "path")]
            loc = " -> ".join(loc_parts)
            msg = err.get("msg", "invalid value")
            formatted_errors.append(f"[{loc}]: {msg}" if loc else msg)
        
        error_summary = "; ".join(formatted_errors) if formatted_errors else "Input validation failed for requested endpoint."
        logger.warning(f"Request validation error on {request.method} {request.url.path}: {error_summary}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=build_error_payload(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                error_code="REQUEST_VALIDATION_ERROR",
                message=f"Validation failed: {error_summary}",
                request_id=request_id,
                details={"errors": exc.errors()}
            )
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "")
        logger.error(
            f"Unhandled internal server exception on {request.method} {request.url.path}: {str(exc)}",
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=build_error_payload(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred. Please try again later.",
                request_id=request_id
            )
        )
