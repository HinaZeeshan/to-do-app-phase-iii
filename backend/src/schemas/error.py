"""
Error response schemas for API.
Provides consistent error format across all endpoints.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ErrorDetail(BaseModel):
    """Error details in response."""

    code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime
    request_id: str


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: ErrorDetail

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid or expired token",
                    "details": None,
                    "timestamp": "2026-01-14T12:00:00Z",
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                }
            }
        }
