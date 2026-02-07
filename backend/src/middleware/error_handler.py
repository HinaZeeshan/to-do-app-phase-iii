"""
Global exception handlers for FastAPI.
Provides consistent error response format.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from datetime import datetime
import uuid


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions with standardized error format.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        JSONResponse with error details
    """
    error_codes = {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
        status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
    }

    error_code = error_codes.get(exc.status_code, "ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code,
                "message": exc.detail,
                "details": None,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4()),
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions with standardized error format.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSONResponse with generic error message
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": None,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4()),
            }
        },
    )
