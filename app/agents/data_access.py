"""
Data Access Layer for Agents

This module provides tools for agents to access user data from the database.
"""

import logging, asyncio, json
import concurrent.futures
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.tools import tool

from app.core.dependencies import PortfolioServiceDep, CurrentUserDep
from app.schemas.portfolio import PortfolioResponse

logger = logging.getLogger(__name__)


class DataAccessLayer:
    """Data access layer for agents to interact with user data."""
    
    def __init__(self, portfolio_service, current_user):
        self.portfolio_service = portfolio_service
        self.current_user = current_user
    
    async def get_user_portfolios(self) -> List[Dict[str, Any]]:
        """Get all portfolios for the current user."""
        try:
            portfolios = await self.portfolio_service.list_portfolios(
                user_id=self.current_user.user_id,
                skip=0,
                limit=100  # Get all portfolios
            )
            
            # Convert to dict format for easier processing
            portfolio_data = []
            for portfolio in portfolios:
                portfolio_data.append({
                    "portfolio_id": portfolio.portfolio_id,
                    "symbol": portfolio.symbol,
                    "security_name": portfolio.security_name,
                    "asset_class": portfolio.asset_class,
                    "sector": portfolio.sector,
                    "quantity": portfolio.quantity,
                    "purchase_date": portfolio.purchase_date,
                    "purchase_price": float(portfolio.purchase_price),
                    "sell_date": portfolio.sell_date,
                    "sell_price": float(portfolio.sell_price) if portfolio.sell_price else None,
                    "is_active": portfolio.sell_date is None
                })
            
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error fetching user portfolios: {e}")
            return []
    
    async def get_portfolio_by_id(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific portfolio by ID."""
        try:
            portfolio = await self.portfolio_service.get_portfolio(
                user_id=self.current_user.user_id,
                portfolio_id=portfolio_id
            )
            
            return {
                "portfolio_id": portfolio.portfolio_id,
                "symbol": portfolio.symbol,
                "security_name": portfolio.security_name,
                "asset_class": portfolio.asset_class,
                "sector": portfolio.sector,
                "quantity": portfolio.quantity,
                "purchase_date": portfolio.purchase_date,
                "purchase_price": float(portfolio.purchase_price),
                "sell_date": portfolio.sell_date,
                "sell_price": float(portfolio.sell_price) if portfolio.sell_price else None,
                "is_active": portfolio.sell_date is None
            }
            
        except Exception as e:
            logger.error(f"Error fetching portfolio {portfolio_id}: {e}")
            return None
    
    async def get_active_portfolios(self) -> List[Dict[str, Any]]:
        """Get only active (non-sold) portfolios."""
        portfolios = await self.get_user_portfolios()
        return [p for p in portfolios if p["is_active"]]
    
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get a summary of the user's portfolio."""
        portfolios = await self.get_active_portfolios()
        
        if not portfolios:
            return {
                "total_holdings": 0,
                "total_value": 0.0,
                "sectors": {},
                "asset_classes": {},
                "top_holdings": []
            }
        
        # Calculate summary statistics
        total_holdings = len(portfolios)
        total_value = sum(p["quantity"] * p["purchase_price"] for p in portfolios)
        
        # Sector breakdown
        sectors = {}
        for portfolio in portfolios:
            sector = portfolio["sector"]
            value = portfolio["quantity"] * portfolio["purchase_price"]
            sectors[sector] = sectors.get(sector, 0) + value
        
        # Asset class breakdown
        asset_classes = {}
        for portfolio in portfolios:
            asset_class = portfolio["asset_class"]
            value = portfolio["quantity"] * portfolio["purchase_price"]
            asset_classes[asset_class] = asset_classes.get(asset_class, 0) + value
        
        # Top holdings by value
        holdings_by_value = sorted(
            portfolios,
            key=lambda p: p["quantity"] * p["purchase_price"],
            reverse=True
        )
        top_holdings = [
            {
                "symbol": p["symbol"],
                "security_name": p["security_name"],
                "value": p["quantity"] * p["purchase_price"],
                "percentage": (p["quantity"] * p["purchase_price"] / total_value) * 100
            }
            for p in holdings_by_value[:10]  # Top 10
        ]
        
        return {
            "total_holdings": total_holdings,
            "total_value": total_value,
            "sectors": sectors,
            "asset_classes": asset_classes,
            "top_holdings": top_holdings
        }


def create_portfolio_tools(data_access: DataAccessLayer) -> List:
    """Create tools for portfolio data access."""
    
    @tool
    def get_user_portfolio_data() -> str:
        """Get all portfolio data for the current user.
        
        Returns:
            JSON string containing all user portfolio holdings
        """
        try:
            # Check if we're in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a task
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, data_access.get_user_portfolios())
                    portfolios = future.result()
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                portfolios = asyncio.run(data_access.get_user_portfolios())
            
            if not portfolios:
                return "No portfolio data found for this user."
            
            return json.dumps(portfolios, default=str)
            
        except Exception as e:
            logger.error(f"Error in get_user_portfolio_data: {e}")
            return f"Error retrieving portfolio data: {str(e)}"
    
    @tool
    def get_portfolio_summary() -> str:
        """Get a summary of the user's portfolio.
        
        Returns:
            JSON string containing portfolio summary statistics
        """
        try:
            # Check if we're in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a task
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, data_access.get_portfolio_summary())
                    summary = future.result()
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                summary = asyncio.run(data_access.get_portfolio_summary())
            
            return json.dumps(summary, default=str)
            
        except Exception as e:
            logger.error(f"Error in get_portfolio_summary: {e}")
            return f"Error retrieving portfolio summary: {str(e)}"
    
    @tool
    def get_active_portfolios() -> str:
        """Get only active (non-sold) portfolio holdings.
        
        Returns:
            JSON string containing active portfolio holdings
        """
        try:
            # Check if we're in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a task
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, data_access.get_active_portfolios())
                    portfolios = future.result()
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                portfolios = asyncio.run(data_access.get_active_portfolios())
            
            if not portfolios:
                return "No active portfolio holdings found for this user."
            
            return json.dumps(portfolios, default=str)
            
        except Exception as e:
            logger.error(f"Error in get_active_portfolios: {e}")
            return f"Error retrieving active portfolios: {str(e)}"
    
    @tool
    def get_portfolio_by_symbol(symbol: str) -> str:
        """Get portfolio data for a specific stock symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., AAPL, MSFT)
            
        Returns:
            JSON string containing portfolio data for the symbol
        """
        try:
            # Check if we're in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a task
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, data_access.get_active_portfolios())
                    portfolios = future.result()
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                portfolios = asyncio.run(data_access.get_active_portfolios())
            
            matching_portfolios = [p for p in portfolios if p["symbol"].upper() == symbol.upper()]
            
            if not matching_portfolios:
                return f"No portfolio holdings found for symbol {symbol}."
            
            return json.dumps(matching_portfolios, default=str)
            
        except Exception as e:
            logger.error(f"Error in get_portfolio_by_symbol: {e}")
            return f"Error retrieving portfolio data for {symbol}: {str(e)}"
    
    return [
        get_user_portfolio_data,
        get_portfolio_summary,
        get_active_portfolios,
        get_portfolio_by_symbol
    ]
