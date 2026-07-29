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

        # 1. HTTP Strict Transport Security (HSTS) - Enforce HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # 2. Prevent Clickjacking Attacks
        response.headers["X-Frame-Options"] = "DENY"

        # 3. Prevent MIME-type Sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 4. Cross-Site Scripting (XSS) Protection Filter
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 5. Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 6. Content Security Policy (CSP)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:;"

        return response
