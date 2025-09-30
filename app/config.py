"""
Application Configuration Module

This module manages all application configuration settings using Pydantic BaseSettings.
It handles environment variables, database connections, security settings, and project metadata.

Configuration is loaded from environment variables and .env files with proper validation
and type checking through Pydantic.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


# Base configuration settings applied to all configuration classes
# This ensures consistent behavior across different setting categories
_base_config = SettingsConfigDict(
    env_file="./.env",           # Load from .env file in project root
    env_ignore_empty=True,       # Ignore empty environment variables
    extra="ignore",              # Ignore extra fields not defined in the model
    env_file_encoding="utf-8"    # Ensure proper encoding for international characters
)


class ProjectSettings(BaseSettings):
    """
    Project-level configuration settings.
    
    These settings define the application metadata, API structure, and operational
    parameters that are not environment-specific.
    
    Attributes:
        PROJECT_NAME (str): Human-readable name of the project
        VERSION (str): Semantic version of the application
        API_V1_STR (str): Base path for API v1 endpoints
        DEBUG (bool): Debug mode flag for development/testing
    """
    PROJECT_NAME: str = "E-commerce API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False


class DatabaseSettings(BaseSettings):
    """
    Database connection and configuration settings.
    
    This class manages all database-related configuration including connection
    parameters, connection pooling, and authentication details.
    
    Attributes:
        DATABASE_SERVER (str): Database server hostname or IP address
        DATABASE_PORT (int): Database server port number
        DATABASE_USER (str): Database username for authentication
        DATABASE_PASSWORD (str): Database password for authentication
        DATABASE_NAME (str): Name of the target database
        DATABASE_POOL_SIZE (int): Maximum number of connections in the pool
        DATABASE_MAX_OVERFLOW (int): Maximum number of connections that can overflow
    
    Note:
        All database settings are required and must be provided via environment
        variables or .env file for security reasons.
    """
    DATABASE_SERVER: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_POOL_SIZE: int
    DATABASE_MAX_OVERFLOW: int

    REDIS_HOST: str
    REDIS_PORT: int
    
    # Apply base configuration settings
    model_config = _base_config
    
    @property
    def get_database_url(self) -> str:
        """
        Generate the complete database connection URL.
        
        This property constructs the full database connection string including
        proper URL encoding of special characters in the password.
        
        Returns:
            str: Complete PostgreSQL connection URL with asyncpg driver
            
        Example:
            postgresql+asyncpg://username:encoded_password@localhost:5432/dbname
        """
        # URL-encode the password to handle special characters like @, #, %, etc.
        # This prevents connection string parsing errors
        encoded_password = quote_plus(self.DATABASE_PASSWORD)
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{encoded_password}@{self.DATABASE_SERVER}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def get_redis_url(self, db: int) -> str:
        """
        Generate the complete redis connection URL.
        
        This property constructs the full redis connection string.
        
        Returns:
            str: Complete REDIS connection URL with redis driver
        """
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"


class SecuritySettings(BaseSettings):
    """
    Security and authentication configuration settings.
    
    This class manages JWT token configuration and other security-related
    parameters required for user authentication and authorization.
    
    Attributes:
        JWT_SECRET (str): Secret key for JWT token signing and verification
        JWT_ALGORITHM (str): Algorithm used for JWT token signing (e.g., HS256)
    
    Note:
        JWT_SECRET should be a strong, randomly generated string and kept secure.
        Never commit the actual secret to version control.
    """
    JWT_SECRET: str
    JWT_ALGORITHM: str

    # Apply base configuration settings
    model_config = _base_config


# Initialize configuration instances
# These instances will load settings from environment variables and .env files
db_settings = DatabaseSettings()
security_settings = SecuritySettings()
project_settings = ProjectSettings()