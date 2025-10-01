from pydantic import BaseModel, Field, EmailStr, condecimal
from typing import Optional
from datetime import datetime


class PortfolioBase(BaseModel):
    user_id: int = Field(..., description="Reference to the associated user ID")
    symbol: str = Field(..., min_length=1, description="Stock or security ticker symbol")
    security_name: str = Field(..., min_length=1, description="Full name of the security")
    asset_class: str = Field(..., min_length=1, description="Type of asset (e.g., Equity, Bond, ETF)")
    sector: str = Field(..., min_length=1, description="Type of sector (e.g., Technology, Healthcare, Financials)")
    quantity: int = Field(..., gt=0, description="Number of units purchased")
    purchase_date: Optional[datetime] = Field(None, description="Date when the asset was purchased")
    sell_date: Optional[datetime] = Field(None, description="Date when the asset was sold (if applicable)")
    purchase_price: condecimal(max_digits=10, decimal_places=4) = Field(..., description="Purchase price per unit")
    sell_price: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="Sell price per unit (if sold)")
    
    class Config:
        from_attributes = True


class PortfolioCreate(BaseModel):
    """Schema for portfolio creation requests (user_id is set from authenticated user)."""
    symbol: str = Field(..., min_length=1, description="Stock or security ticker symbol")
    security_name: str = Field(..., min_length=1, description="Full name of the security")
    asset_class: str = Field(..., min_length=1, description="Type of asset (e.g., Equity, Bond, ETF)")
    sector: str = Field(..., min_length=1, description="Type of sector (e.g., Technology, Healthcare, Financials)")
    quantity: int = Field(..., gt=0, description="Number of units purchased")
    purchase_date: Optional[datetime] = Field(None, description="Date when the asset was purchased")
    purchase_price: condecimal(max_digits=10, decimal_places=4) = Field(..., description="Purchase price per unit")
    
    class Config:
        from_attributes = True


class PortfolioUpdate(BaseModel):
    """Schema for portfolio update requests."""
    symbol: Optional[str] = Field(None, min_length=1, description="Stock or security ticker symbol")
    security_name: Optional[str] = Field(None, min_length=1, description="Full name of the security")
    asset_class: Optional[str] = Field(None, min_length=1, description="Type of asset (e.g., Equity, Bond, ETF)")
    sector: Optional[str] = Field(None, min_length=1, description="Type of sector (e.g., Technology, Healthcare, Financials)")
    quantity: Optional[int] = Field(None, gt=0, description="Number of units purchased")
    purchase_date: Optional[datetime] = Field(None, description="Date when the asset was purchased")
    sell_date: Optional[datetime] = Field(None, description="Date when the asset was sold (if applicable)")
    purchase_price: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="Purchase price per unit")
    sell_price: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="Sell price per unit (if sold)")
    
    class Config:
        from_attributes = True

class PortfolioResponse(PortfolioBase):
    """Schema for portfolio data responses."""
    portfolio_id: int = Field(..., description="Unique portfolio identifier")

    class Config:
        from_attributes = True


class PortfolioFilter(BaseModel):
    """Schema for portfolio search and filtering criteria."""
    search: Optional[str] = Field(None, description="Search term for symbol and security name fields")
    asset_class: Optional[str] = Field(None, description="Filter by asset class")