"""
Request ID middleware for FastAPI.
Adds unique UUID to each request for tracing.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request."""

    async def dispatch(self, request: Request, call_next):
        """
        Add request_id to request state and response headers.

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint

        Returns:
            Response with X-Request-ID header
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
