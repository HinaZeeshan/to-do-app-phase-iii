"""
Request/response logging middleware.
"""

import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Configure logger
logger = logging.getLogger("api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        """
        Log request details before processing and response details after.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        # Record start time
        start_time = time.time()

        # Get request ID from request state (set by RequestIDMiddleware)
        request_id = getattr(request.state, "request_id", "unknown")

        # Log incoming request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {process_time:.3f}s"
            )

            # Add processing time header
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            # Calculate processing time
            process_time = time.time() - start_time

            # Log error
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Error: {str(e)} - "
                f"Duration: {process_time:.3f}s",
                exc_info=True
            )

            # Re-raise to let error handlers deal with it
            raise
