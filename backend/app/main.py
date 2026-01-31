"""
UNTANGLE - Gaming Hub Membership Tracking System
FastAPI main application entry point.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="UNTANGLE API",
    description="Gaming Hub Membership Tracking System - Automates credit management, session logging, and real-time balance calculations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "UNTANGLE API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "UNTANGLE API - Gaming Hub Membership Tracking",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Import routers
from .routers import auth, members, purchases, sessions, dashboard

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(members.router, prefix="/api/v1/members", tags=["Members"])
app.include_router(purchases.router, prefix="/api/v1/purchases", tags=["Credits/Balance"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["Gaming Sessions"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

# Branch management router (optional - not required for MVP)
# app.include_router(branches_router, prefix="/api/v1/branches", tags=["Branches"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
