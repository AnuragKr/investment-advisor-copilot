"""
User API Controller Module

This module defines the REST API endpoints for user management operations.
It handles HTTP requests, input validation, error handling, and response
formatting for all user-related operations.

The controller layer is responsible for:
- HTTP request/response handling
- Input validation and sanitization
- Error handling and HTTP status codes
- Response formatting and serialization
- API documentation through OpenAPI schemas

API Endpoints:
- GET /users/{user_id} - Retrieve user by ID
- GET /users/ - List users with filtering and pagination
- POST /users/ - Create new user
- PUT /users/{user_id} - Update existing user
- DELETE /users/{user_id} - Delete user
- GET /users/email/{email} - Retrieve user by email
"""

from fastapi import APIRouter, HTTPException, Depends
from app.core.dependencies import UserServiceDep,CurrentUserDep,get_access_token
from app.schemas import UserCreate, UserUpdate, UserResponse, UserFilter
from app.exceptions import UserNotFoundError, DatabaseError, UserAlreadyExistsError
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.core.redis import add_jti_to_blacklist

# Create router instance for user endpoints
# All routes in this module will be prefixed with /users
router = APIRouter(prefix="/users", tags=["users"])




### Login the user
@router.post("/login")
async def login_user(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserServiceDep,
):
    try:
        access_token = await service.authenticate_user(request_form.username, request_form.password)
        return {
            "access_token": access_token,
            "type": "jwt",
        }
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to provide access token at this time")

#Logout a user
@router.get("/logout")
async def logout_user(token_data: Annotated[dict, Depends(get_access_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return {"message": "Successfully logged out"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(service: UserServiceDep, user_id: int):
    """
    Retrieve a user by their unique identifier.
    Args:
        service (UserServiceDep): Injected user service dependency
        user_id (int): Unique identifier of the user to retrieve 
    Returns:
        UserResponse: User data without sensitive information
    """
    try:
        db_user = await service.get_user(user_id)
        return db_user
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve user at this time")


@router.get("/", response_model=list[UserResponse])
async def list_users(
    service: UserServiceDep, 
    skip: int = 0, 
    limit: int = 10,
    search: str = None,
    city: str = None,
    country: str = None
):
    """
    Retrieve a filtered and paginated list of users.
    Args:
        service (UserServiceDep): Injected user service dependency
        skip (int): Number of records to skip for pagination (default: 0)
        limit (int): Maximum number of records to return (default: 10, max: 100)
        search (str, optional): Search term for name and email fields
        city (str, optional): Filter by city name (partial match)
        country (str, optional): Filter by country name (exact match)
    Returns:
        list[UserResponse]: List of users matching the criteria
    """
    try:
        # Create filter object from query parameters
        filters = UserFilter(
            search=search,
            city=city,
            country=country
        )
        
        return await service.list_users(skip=skip, limit=limit, filters=filters)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve users at this time")


@router.post("/", response_model=UserResponse)
async def create_user(service: UserServiceDep, user: UserCreate):
    """
    Create a new user account.
    Args:
        service (UserServiceDep): Injected user service dependency
        user (UserCreate): User creation data from request body 
    Returns:
        UserResponse: Created user data (excluding password) 
    Raises:
        HTTPException: 
            - 409: User with email already exists
            - 422: Validation error in request data
            - 500: Internal server error
    """
    try:
        return await service.create_user(user)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to create user at this time")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(service: UserServiceDep, user_id: int, user: UserUpdate):
    """
    Update an existing user account.
    Args:
        service (UserServiceDep): Injected user service dependency
        user_id (int): Unique identifier of the user to update
        user (UserUpdate): User update data from request body    
    Returns:
        UserResponse: Updated user data (excluding password)
    """
    try:
        return await service.update_user(user_id, user)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to update user at this time")


@router.delete("/{user_id}")
async def delete_user(service: UserServiceDep, user_id: int):
    """
    Delete a user account from the system.
    Args:
        service (UserServiceDep): Injected user service dependency
        user_id (int): Unique identifier of the user to delete
    Returns:
        dict: Success message confirming deletion
    """
    try:
        await service.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to delete user at this time")


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(service: UserServiceDep, email: str):
    """
    Retrieve a user by their email address.
    Args:
        service (UserServiceDep): Injected user service dependency
        email (str): Email address of the user to retrieve
    Returns:
        UserResponse: User data (excluding password)
    """
    try:
        db_user = await service.get_user_by_email(email)
        return db_user
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve user at this time")