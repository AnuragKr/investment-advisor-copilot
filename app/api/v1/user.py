"""User API endpoints for management operations."""

from fastapi import APIRouter, HTTPException, Depends
from app.core.dependencies import UserServiceDep,CurrentUserDep,get_access_token
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.exceptions import UserNotFoundError, DatabaseError, UserAlreadyExistsError
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.core.redis import add_jti_to_blacklist

router = APIRouter(prefix="/users", tags=["users"])

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

@router.get("/logout")
async def logout_user(token_data: Annotated[dict, Depends(get_access_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return {"message": "Successfully logged out"}


@router.get("/", response_model=UserResponse)
async def get_user(service: UserServiceDep, user: CurrentUserDep):
    """Retrieve a user by ID."""
    try:
        db_user = await service.get_user(user.user_id)
        return db_user
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve user at this time")


@router.post("/", response_model=UserResponse)
async def create_user(service: UserServiceDep, user: UserCreate):
    """Create a new user account."""
    try:
        return await service.create_user(user)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to create user at this time")


@router.put("/", response_model=UserResponse)
async def update_user(service: UserServiceDep,  user: CurrentUserDep, body: UserUpdate):
    """Update an existing user account."""
    try:
        return await service.update_user(user.user_id, body)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to update user at this time")


@router.delete("/")
async def delete_user(service: UserServiceDep, user: CurrentUserDep):
    """Delete a user account from the system."""
    try:
        await service.delete_user(user.user_id)
        return {"message": "User deleted successfully"}
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to delete user at this time")