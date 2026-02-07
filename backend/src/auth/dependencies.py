"""
JWT authentication dependencies for FastAPI.
Provides JWT verification and user ID extraction.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from src.config import settings

security = HTTPBearer()


async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify JWT token and return claims.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        dict: JWT payload claims

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    token_data: dict = Depends(verify_jwt),
) -> str:
    """
    Extract user_id from verified JWT claims.

    Args:
        token_data: Verified JWT payload

    Returns:
        str: User ID from JWT claims

    Raises:
        HTTPException: 401 if user_id missing from token
    """
    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user_id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
