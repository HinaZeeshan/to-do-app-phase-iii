"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..database import get_db
from ..services.auth_service import AuthService
from ..schemas.auth import SignupRequest, SignupResponse, LoginRequest, LoginResponse, LogoutResponse, RefreshTokenRequest, RefreshTokenResponse


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api", tags=["authentication"])


@router.post("/auth/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # 5 signup attempts per minute per IP
async def signup(
    request: Request,
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account.

    Args:
        request: FastAPI request object
        signup_data: Signup request with email and password
        db: Database session dependency

    Returns:
        SignupResponse with user_id, email, and JWT token

    Raises:
        HTTPException 400: Invalid input (weak password, invalid email)
        HTTPException 409: Email already registered
    """
    service = AuthService(db, request)
    user, token, refresh_token = await service.signup(signup_data)

    return SignupResponse(
        user_id=user.id,
        email=user.email,
        token=token,
        refresh_token=refresh_token
    )


@router.post("/auth/login", response_model=LoginResponse)
@limiter.limit("5/minute")  # 5 login attempts per minute per IP
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate existing user.

    Args:
        request: FastAPI request object
        login_data: Login request with email and password
        db: Database session dependency

    Returns:
        LoginResponse with user_id, email, and JWT token

    Raises:
        HTTPException 401: Invalid credentials
        HTTPException 429: Too many failed login attempts
    """
    service = AuthService(db, request)
    user, token, refresh_token = await service.login(login_data)

    return LoginResponse(
        user_id=user.id,
        email=user.email,
        token=token,
        refresh_token=refresh_token
    )


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    End user session.

    Args:
        request: FastAPI request object
        db: Database session dependency

    Returns:
        LogoutResponse with success message

    Notes:
        - This is a client-side logout (JWT remains valid until expiration)
        - For immediate invalidation, JWT secret rotation is required
    """
    # Log logout event
    service = AuthService(db, request)
    # In a real implementation, this would log the logout event
    # For now, we'll just return a success message
    return LogoutResponse()


@router.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    """
    service = AuthService(db, request)
    access_token, refresh_token = await service.refresh_access_token(refresh_data.refresh_token)

    return RefreshTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )