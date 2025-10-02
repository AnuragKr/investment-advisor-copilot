"""
Investment Advisor REST API Main Application Module

This module serves as the entry point for the FastAPI application.
It configures the application, includes all API routers, and sets up
documentation endpoints.
"""

from fastapi import FastAPI
import logging
from scalar_fastapi import get_scalar_api_reference
from app.config import project_settings
from app.api.v1.user import router as user_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.agents import router as agents_router


# Configure application-wide logging
# Sets up structured logging with timestamp, logger name, and log level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    
    This function initializes the FastAPI app with all necessary configurations
    including title, description, version, and API documentation endpoints.
    
    Returns:
        FastAPI: Configured FastAPI application instance
        
    Note:
        - OpenAPI documentation is available at /docs (Swagger UI)
        - ReDoc documentation is available at /redoc
        - Custom Scalar documentation is available at /scalar
    """
    
    # Initialize FastAPI application with metadata and configuration
    app = FastAPI(
        title=project_settings.PROJECT_NAME,
        description="Production-grade Investment Advisor API with comprehensive user and portfolio management",
        version=project_settings.VERSION,
        openapi_url=f"{project_settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Register API routers for different resource endpoints
    # Each router handles a specific domain (users, portfolio, agents, etc.)
    app.include_router(user_router, prefix="/api/v1")
    app.include_router(portfolio_router, prefix="/api/v1")
    app.include_router(agents_router, prefix="/api/v1")
    
    logger.info("FastAPI application created successfully with all routers registered")
    return app


# Create the global application instance
# This instance is used by the ASGI server (e.g., uvicorn)
app = create_application()


@app.get("/")
async def root():
    return {"message": "Investment Advisor API is running"}


@app.get("/scalar", include_in_schema=False)
async def get_scalar_docs():
    """
    Serve Scalar API documentation.
    
    This endpoint provides an alternative API documentation interface
    using Scalar, which offers enhanced features compared to standard OpenAPI docs.
    
    Returns:
        HTML: Scalar documentation page
        
    Note:
        This endpoint is excluded from the OpenAPI schema as it's
        primarily for documentation purposes.
    """
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API Documentation",
    )