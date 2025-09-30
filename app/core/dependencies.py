"""
FastAPI Dependency Injection Configuration Module

This module defines all the dependency injection functions and type annotations
used throughout the application. It provides a centralized way to manage
dependencies like database sessions and service instances.

Dependencies are automatically injected by FastAPI and provide:
- Database session management
- Service layer instantiation
- Proper resource cleanup
- Type safety through annotations
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.user import UserService
from app.core.security import oauth2_scheme
from app.utils.security import decode_access_token
from fastapi import HTTPException,status
from app.models.user import User
from sqlalchemy import select
from app.core.redis import is_jti_blacklisted
# Type annotation for database session dependency
# This provides type hints for IDE support and runtime validation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_service(session: SessionDep) -> UserService:
    """
    Dependency function to create and inject UserService instances.
    
    This function creates a new UserService instance for each request,
    ensuring proper isolation and resource management.
    
    Args:
        session (SessionDep): Database session dependency
        
    Returns:
        UserService: Configured user service instance
        
    Note:
        Each request gets a fresh service instance with its own database session.
        This ensures thread safety and proper resource cleanup.
    """
    return UserService(session)




# Type annotation for UserService dependency injection
# This allows FastAPI to automatically inject the service into route handlers
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

# Access token data dep
async def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    data = decode_access_token(token)

    if data is None or await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    return data


# Logged In User
async def get_current_user(
    token_data: Annotated[dict, Depends(get_access_token)],
    session: SessionDep,
) -> User:
    result = await session.execute(select(User).where(User.user_id == token_data["user"]["id"]))
    user_model = result.scalar_one_or_none()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return user_model

async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

async def get_current_customer(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer privileges required",
        )
    return current_user

CurrentUserDep = Annotated[User, Depends(get_current_user)]

CurrentAdminDep = Annotated[User, Depends(get_current_admin)]

CurrentCustomerDep = Annotated[User, Depends(get_current_customer)]