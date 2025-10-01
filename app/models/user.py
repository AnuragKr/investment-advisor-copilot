"""User database model for investment advisor application."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """User database model for investment advisor accounts."""
    
    # Table configuration
    __tablename__ = "users"
    __table_args__ = {'schema': 'investment_db'}
    
    # Primary key - auto-generated unique identifier
    user_id: Optional[int] = Field(
        default=None, 
        primary_key=True, 
        description="Unique user identifier"
    )
    
    # Personal information fields
    name: str = Field(
        ..., 
        nullable=False, 
        description="User's first/given name"
    )
    
    # Authentication and contact fields
    email_id: str = Field(
        ..., 
        nullable=False, 
        unique=True, 
        description="User's email address (unique)"
    )
    mobile_no: Optional[str] = Field(
        default=None, 
        description="User's phone number"
    )
    
    # Security and access control
    password: str = Field(
        ..., 
        nullable=False, 
        description="Hashed user password (never stored in plain text)"
    )
    
    # Address information fields
    address: str = Field(
        ..., 
        nullable=False, 
        description="Primary address line"
    )
    city: str = Field(
        ..., 
        nullable=False, 
        description="City name"
    )
    state: str = Field(
        ..., 
        nullable=False, 
        description="State or province name"
    )
    postal_code: str = Field(
        ..., 
        nullable=False, 
        description="Postal or ZIP code"
    )
    country: str = Field(
        ..., 
        nullable=False, 
        description="Country name"
    )
    
    # System audit fields
    created_at: Optional[datetime] = Field(
        default=None, 
        nullable=False, 
        description="Account creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None, 
        nullable=False, 
        description="Last update timestamp"
    )
    
    class Config:
        from_attributes = True