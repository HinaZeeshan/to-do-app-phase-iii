"""
Rate limiting middleware for authentication endpoints.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import FastAPI


# Initialize limiter with remote address as key
limiter = Limiter(key_func=get_remote_address)


def add_rate_limiting(app: FastAPI):
    """
    Add rate limiting to the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(Exception, _rate_limit_exceeded_handler)