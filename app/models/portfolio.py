"""Portfolio database model for investment holdings."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class Portfolio(SQLModel, table=True):
    """Portfolio database model for investment holdings."""
    
    # Table configuration
    __tablename__ = "portfolios"
    __table_args__ = {'schema': 'investment_db'}
    
    # Primary key - auto-generated unique identifier
    portfolio_id: Optional[int] = Field(
        default=None, 
        primary_key=True, 
        description="Unique portfolio identifier"
    )
    
    # Foreign key to users table
    user_id: int = Field(
        ..., 
        nullable=False, 
        description="Reference to the associated user ID",
        foreign_key="investment_db.users.user_id"
    )
    
    # Security information fields
    symbol: str = Field(
        ..., 
        nullable=False, 
        description="Stock or security ticker symbol"
    )
    
    security_name: str = Field(
        ..., 
        nullable=False, 
        description="Full name of the security"
    )
    
    asset_class: str = Field(
        ..., 
        nullable=False, 
        description="Type of asset (e.g., Equity, Bond, ETF)"
    )

    sector: str = Field(
        ..., 
        nullable=False, 
        description="Type of sector (e.g., Technology, Healthcare, Financials)"
    )
    
    # Transaction quantity
    quantity: int = Field(
        ..., 
        nullable=False, 
        description="Number of units purchased"
    )
    
    # Transaction dates
    purchase_date: Optional[datetime] = Field(
        default=None, 
        description="Date when the asset was purchased"
    )
    
    sell_date: Optional[datetime] = Field(
        default=None, 
        description="Date when the asset was sold (if applicable)"
    )
    
    # Financial data with precision
    purchase_price: Decimal = Field(
        ..., 
        nullable=False, 
        max_digits=10, 
        decimal_places=4,
        description="Purchase price per unit"
    )
    
    sell_price: Optional[Decimal] = Field(
        default=None, 
        max_digits=10, 
        decimal_places=4,
        description="Sell price per unit (if sold)"
    )
    
    class Config:
        from_attributes = True
