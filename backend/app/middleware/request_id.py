import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    ASGI Middleware that generates or propagates a unique Request ID header ('X-Request-ID')
    for distributed request tracing across system logs and services.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract existing Request ID from incoming request headers or generate a new UUID4
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store Request ID on ASGI request state for access in endpoints & exception handlers
        request.state.request_id = request_id

        # Process the request lifecycle
        response = await call_next(request)

        # Inject Request ID into outgoing HTTP response headers
        response.headers["X-Request-ID"] = request_id
        return response
