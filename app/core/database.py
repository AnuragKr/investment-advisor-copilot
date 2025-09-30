"""
Database Configuration and Connection Management Module

This module handles all database-related operations including:
- Database engine creation and configuration
- Connection pooling and session management
- Table creation and schema management
- Database health checks and monitoring

The module uses SQLAlchemy with async support for optimal performance
and SQLModel for simplified model definitions.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel
import logging

from app.config import db_settings

# Configure logging for database operations
logger = logging.getLogger(__name__)

# Base class for all models - uses SQLModel for enhanced functionality
# SQLModel combines the best of SQLAlchemy and Pydantic
Base = SQLModel

# Create async database engine with connection pooling
# The engine manages the connection pool and provides async database access
engine = create_async_engine(
    # Database connection URL with asyncpg driver for PostgreSQL
    url=db_settings.get_database_url,
    # Enable SQL query logging for debugging and monitoring
    echo=True,
    # Connection pool configuration for optimal performance
    pool_size=db_settings.DATABASE_POOL_SIZE,
    max_overflow=db_settings.DATABASE_MAX_OVERFLOW,
    # Connection timeout and retry settings
    pool_timeout=30,
    pool_recycle=3600,
)


async def get_session() -> AsyncSession:
    """
    Dependency function to provide database sessions.
    
    This function creates and yields database sessions for use in FastAPI
    dependency injection. Each request gets a fresh session that is
    automatically closed after use.
    
    Yields:
        AsyncSession: Database session for the current request
        
    Note:
        This function is designed to be used as a FastAPI dependency.
        The session is automatically managed and cleaned up.
    """
    # Create session factory with async support
    async_session = sessionmaker(
        bind=engine, 
        class_=AsyncSession, 
        expire_on_commit=False,  # Keep objects accessible after commit
    )

    # Create and yield session, ensuring proper cleanup
    async with async_session() as session:
        yield session


async def check_db() -> None:
    """
    Check database connectivity and health.
    
    This function performs a simple health check by executing a basic
    SQL query to verify the database is accessible and responding.
    
    Raises:
        Exception: If database connection fails
        
    Note:
        This function is useful for startup checks and health monitoring.
    """
    async for session in get_session():
        try:
            # Execute a simple query to test connectivity
            await session.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            print("Database connected")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            print(db_settings.get_database_url)
            print("Database NOT connected:", e)
            raise