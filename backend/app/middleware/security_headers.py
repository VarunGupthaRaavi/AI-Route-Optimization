from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Production Security Headers Middleware.
    Enforces HSTS, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, and Content-Security-Policy.
    """
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response: Response = await call_next(request)

        # 1. HTTP Strict Transport Security (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # 2. Prevent Clickjacking Attacks
        response.headers["X-Frame-Options"] = "DENY"

        # 3. Prevent MIME-type Sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 4. Cross-Site Scripting (XSS) Protection Filter
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 5. Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 6. Content Security Policy (CSP) - Allow local and remote connect sources
        response.headers["Content-Security-Policy"] = "default-src 'self' http: https: data: 'unsafe-inline' 'unsafe-eval'; connect-src 'self' http: https: wss: ws:;"

        return response
