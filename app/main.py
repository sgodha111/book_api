"""FastAPI application initialization and setup."""

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models.database import close_db, init_db
from app.routers import authors, books, publishers


def setup_logging(log_level: str) -> None:
    """Configure structured JSON logging."""

    class JSONFormatter(logging.Formatter):
        """Custom formatter for JSON logging."""

        def format(self, record: logging.LogRecord) -> str:
            """Format log record as JSON."""
            log_data = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
            }

            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)

            return json.dumps(log_data)

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure root logger
    root_logger.setLevel(getattr(logging, log_level))

    # Console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Suppress noisy libraries
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan."""
    logger = logging.getLogger(__name__)

    # Startup
    logger.info("Starting up application")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    # Setup logging
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    # Create app
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        lifespan=lifespan,
        openapi_url="/api/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors."""
        logger.warning(f"Validation error for {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle 404 errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        """Health check endpoint with database status."""
        try:
            from app.models.database import get_db

            db = await get_db()
            await db.client.admin.command("ping")
            return {
                "status": "healthy",
                "environment": settings.environment,
                "database": "connected",
            }
        except Exception as e:
            return {
                "status": "degraded",
                "environment": settings.environment,
                "database": "disconnected",
                "error": str(e),
            }

    @app.get("/", tags=["root"])
    async def root() -> dict:
        """Root endpoint."""
        return {
            "message": "Welcome to FastAPI MongoDB CRUD API",
            "version": settings.api_version,
            "docs": "/docs",
            "health": "/health",
            "endpoints": {
                "books": "/api/v1/books",
                "authors": "/api/v1/authors",
                "publishers": "/api/v1/publishers",
            },
        }

    # Include routers
    app.include_router(
        books.router,
        prefix="/api/v1",
        responses={404: {"description": "Not found"}},
    )
    app.include_router(
        authors.router,
        prefix="/api/v1",
        responses={404: {"description": "Not found"}},
    )
    app.include_router(
        publishers.router,
        prefix="/api/v1",
        responses={404: {"description": "Not found"}},
    )

    logger.info(
        "Application initialized with routes",
        extra={
            "environment": settings.environment,
            "api_version": settings.api_version,
        },
    )

    return app


# Application instance
app = create_app()
