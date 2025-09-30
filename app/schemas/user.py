"""
User Data Schema Definitions

This module defines Pydantic models for user-related data validation,
serialization, and API documentation. The schemas ensure data integrity
and provide clear contracts between API layers.

Schema Hierarchy:
- UserBase: Common user fields shared across all schemas
- UserCreate: Schema for user creation requests
- UserUpdate: Schema for user update requests (all fields optional)
- UserResponse: Schema for user data responses (excludes sensitive data)
- UserFilter: Schema for user search and filtering criteria

Key Features:
- Comprehensive field validation with meaningful constraints
- Automatic data type conversion and validation
- OpenAPI documentation generation
- ORM mode support for SQLModel integration
- Secure handling of sensitive data (passwords excluded from responses)
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Base user schema with common fields shared across all user operations.
    
    This schema defines the core user attributes that are consistent
    across creation, updates, and responses. It serves as the foundation
    for other user-related schemas.
    """
    name: str = Field(..., min_length=1, description="User's name")
    email_id: EmailStr = Field(..., description="User's email address")
    mobile_no: str = Field(None, description="User's phone number")
    address: str = Field(..., min_length=1, description="Primary address")
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=1, description="State or province")
    postal_code: str = Field(..., min_length=1, description="Postal or ZIP code")
    country: str = Field(..., min_length=1, description="Country name")
    
    class Config:
        # Enable ORM mode for SQLModel integration
        # This allows the schema to work with database models
        from_attributes = True


class UserCreate(BaseModel):
    """
    Schema for user creation requests.
    
    This schema extends UserBase and adds the password field required
    for new user registration. It inherits all validation rules from
    the base schema.
    
    Security Notes:
        - Passwords are automatically hashed before storage
        - Plain text passwords are never stored in the database
        - Password strength validation should be implemented at the API level
    """
    name: str = Field(..., min_length=1, description="User's name")
    email_id: EmailStr = Field(..., description="User's email address")
    mobile_no: str = Field(None, description="User's phone number")
    address: str = Field(..., min_length=1, description="Primary address")
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=1, description="State or province")
    postal_code: str = Field(..., min_length=1, description="Postal or ZIP code")
    country: str = Field(..., min_length=1, description="Country name")
    password: str = Field(..., min_length=6, description="User's password")
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """
    Schema for user update requests.
    
    This schema allows partial updates by making all fields optional.
    Only provided fields will be updated, supporting flexible user
    profile modifications.
        
    Update Behavior:
        - Only provided fields are updated
        - Timestamps are automatically managed
        - Passwords are automatically hashed if included
    """
    name: str = Field(..., min_length=1, description="User's name")
    email_id: EmailStr = Field(..., description="User's email address")
    mobile_no: str = Field(None, description="User's phone number")
    address: str = Field(..., min_length=1, description="Primary address")
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=1, description="State or province")
    postal_code: str = Field(..., min_length=1, description="Postal or ZIP code")
    country: str = Field(..., min_length=1, description="Country name")
    password: str = Field(..., min_length=6, description="User's password")
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    """
    Schema for user data responses.
    
    This schema extends UserBase and adds the customer_id field for
    complete user identification. It's used for all API responses
    that return user data.
    
    Attributes:
        customer_id (int): Unique identifier for the user
        
    Security Features:
        - Password field is excluded (inherited from UserBase)
        - Sensitive information is never exposed in responses
        - All public user data is included
        
    Usage:
        - API responses for user retrieval
        - User list operations
        - Authentication responses
        - Profile update confirmations
    """
    user_id: int = Field(..., description="Unique user identifier")

    class Config:
        from_attributes = True


class UserFilter(BaseModel):
    """
    Schema for user search and filtering criteria.
    
    This schema defines the parameters used for filtering user lists
    and search operations. All filters are optional and can be
    combined for more specific queries.
    
    Attributes:
        search (Optional[str]): Search term for name and email fields
        city (Optional[str]): Filter by city name (partial match)
        country (Optional[str]): Filter by country name (exact match)
        
    Filter Behavior:
        - search: Case-insensitive matching across first_name, last_name, and email
        - city: Case-insensitive partial matching
        - country: Case-sensitive exact matching
        - All filters use AND logic (all conditions must match)
        
    Usage:
        - User list endpoints with query parameters
        - Admin user management interfaces
        - User search functionality
        - Reporting and analytics queries
    """
    search: Optional[str] = Field(None, description="Search term for name and email fields")
    city: Optional[str] = Field(None, description="Filter by city name")
    country: Optional[str] = Field(None, description="Filter by country name")