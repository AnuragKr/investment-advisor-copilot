"""User data schema definitions for validation and API documentation."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str = Field(..., min_length=1, description="User's name")
    email_id: EmailStr = Field(..., description="User's email address")
    mobile_no: str = Field(None, description="User's phone number")
    address: str = Field(..., min_length=1, description="Primary address")
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=1, description="State or province")
    postal_code: str = Field(..., min_length=1, description="Postal or ZIP code")
    country: str = Field(..., min_length=1, description="Country name")
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Schema for user creation requests."""
    name: str = Field(..., min_length=1, description="User's name")
    email_id: EmailStr = Field(..., description="User's email address")
    mobile_no: str = Field(None, description="User's phone number")
    address: str = Field(..., min_length=1, description="Primary address")
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=1, description="State or province")
    postal_code: str = Field(..., min_length=1, description="Postal or ZIP code")
    country: str = Field(..., min_length=1, description="Country name")
    password: str = Field(..., min_length=6, max_length=72, description="User's password")
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for user update requests."""
    name: str = Field(..., min_length=1, description="User's name")
    email_id: EmailStr = Field(..., description="User's email address")
    mobile_no: str = Field(None, description="User's phone number")
    address: str = Field(..., min_length=1, description="Primary address")
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=1, description="State or province")
    postal_code: str = Field(..., min_length=1, description="Postal or ZIP code")
    country: str = Field(..., min_length=1, description="Country name")
    password: str = Field(..., min_length=6, max_length=72, description="User's password")
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    """Schema for user data responses."""
    user_id: int = Field(..., description="Unique user identifier")

    class Config:
        from_attributes = True
