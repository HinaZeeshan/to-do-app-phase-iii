"""
FastAPI application initialization.
Configures CORS, middleware, and error handlers.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from sqlalchemy import text

from src.config import settings
from src.database import engine
from src.middleware.request_id import RequestIDMiddleware
from src.middleware.logging import LoggingMiddleware
from src.middleware.rate_limit import add_rate_limiting
from src.middleware.error_handler import http_exception_handler, generic_exception_handler
from src.routers import tasks
from src.routers.auth import router as auth_router
from src.routers.chat import router as chat_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Todo Backend API",
    description="Secure RESTful API for multi-user task management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)



# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
add_rate_limiting(app)

# Register exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register routers
app.include_router(tasks.router)
app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Todo Backend API",
        "version": "1.0.0",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    Verifies database connectivity on application startup.
    """
    logger.info("Starting up Todo Backend API...")
    logger.info(f"Environment: {settings.environment}")

    # Verify database connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        raise

    logger.info("Todo Backend API started successfully")
