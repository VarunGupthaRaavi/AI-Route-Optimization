import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import logger


class TimingMiddleware(BaseHTTPMiddleware):
    """
    ASGI Middleware that measures request processing duration, adds 'X-Process-Time' header,
    and logs request execution metrics.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        process_time_ms = (time.perf_counter() - start_time) * 1000
        process_time_str = f"{process_time_ms:.2f}ms"

        response.headers["X-Process-Time"] = process_time_str

        # Suppress logging health check polling endpoints to reduce noise
        if not request.url.path.endswith("/health"):
            request_id = getattr(request.state, "request_id", "N/A")
            logger.info(
                f"HTTP {request.method} {request.url.path} -> Status {response.status_code} in {process_time_str} [req_id={request_id}]"
            )

        return response
