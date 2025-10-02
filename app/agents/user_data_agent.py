"""
User Data Agent

This module provides a dedicated agent for user data access and management.
It serves as a centralized point for all user-related data operations.
"""

import logging
import asyncio
import json
import concurrent.futures
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.tools import tool
from decimal import Decimal

from .base import BaseAgent, AgentConfig
from app.config import agents_settings as config
from app.core.dependencies import PortfolioServiceDep, CurrentUserDep

logger = logging.getLogger(__name__)


class UserDataAgent(BaseAgent):
    """Dedicated agent for user data access and management."""

    def __init__(self, portfolio_service: PortfolioServiceDep, current_user: CurrentUserDep):
        self.portfolio_service = portfolio_service
        self.current_user = current_user
        
        agent_config = AgentConfig(
            name="User Data Agent",
            description="Agent for centralized portfolio data access and management",
            model_name="gpt-4o-mini",
            temperature=0.0,
            max_iterations=2,
            system_message="You are a user data agent specialized in providing access to portfolio data and analysis.",
            openai_api_key=config.OPENAI_API_KEY
        )
        super().__init__(agent_config)

    def _initialize_tools(self) -> List:
        """Initialize user data access tools."""
        return [
            self._create_get_portfolio_data_tool(),
            self._create_get_portfolio_summary_tool()
        ]

    def _get_system_message(self) -> str:
        """Get the system message for portfolio data access."""
        user_id = self.current_user.user_id if self.current_user else "unknown"
        return f"""You are a user data agent specialized in providing access to portfolio data and analysis.

Current user ID: {user_id}

Your capabilities:
- Retrieve portfolio holdings and summaries
- Provide comprehensive portfolio data for analysis
- Filter portfolio data by various criteria

Available tools:
- get_portfolio_data(): Get portfolio holdings with optional filters (symbol, asset_class, sector, active_only)
- get_portfolio_summary(): Get portfolio summary statistics

Guidelines:
- Always provide accurate and up-to-date portfolio data
- Handle requests efficiently and securely
- Return data in structured JSON format when possible
- Maintain user privacy and data security
- Provide clear error messages when data is not available

When other agents request portfolio data:
1. Retrieve the requested data using appropriate tools
2. Format the data for easy consumption
3. Include relevant metadata and context
4. Handle errors gracefully with informative messages"""


    def _create_get_portfolio_data_tool(self):
        """Create tool to get portfolio data with filters."""
        
        @tool
        async def get_portfolio_data(
            symbol: Optional[str] = None,
            asset_class: Optional[str] = None,
            sector: Optional[str] = None,
            active_only: bool = False
        ) -> str:
            """Get portfolio holdings for the current user with optional filters.
            
            Args:
                symbol: Filter by specific ticker symbol (e.g., "AAPL", "MSFT")
                asset_class: Filter by asset class (e.g., "Equity", "Bond")
                sector: Filter by sector (e.g., "Technology", "Healthcare")
                active_only: If True, only return non-sold holdings
            
            Returns:
                JSON string containing filtered portfolio holdings
            """
            try:
                # Use the existing portfolio service directly (now async)
                portfolios = await self.portfolio_service.list_portfolios(
                    user_id=self.current_user.user_id,
                    skip=0,
                    limit=100
                )
                
                # Convert to dict format and apply filters
                portfolio_data = [p.model_dump() for p in portfolios]
                
                # Apply filters efficiently
                if symbol:
                    portfolio_data = [p for p in portfolio_data if p.get("symbol", "").upper() == symbol.upper()]
                if asset_class:
                    portfolio_data = [p for p in portfolio_data if p.get("asset_class", "").lower() == asset_class.lower()]
                if sector:
                    portfolio_data = [p for p in portfolio_data if p.get("sector", "").lower() == sector.lower()]
                if active_only:
                    portfolio_data = [p for p in portfolio_data if p.get("sell_date") is None]
                
                return json.dumps(portfolio_data, default=str) if portfolio_data else "No data found."
                
            except Exception as e:
                logger.error(f"Error getting portfolio data: {e}")
                return f"Error retrieving data: {str(e)}"
        
        return get_portfolio_data

    def _create_get_portfolio_summary_tool(self):
        """Create tool to get portfolio summary."""
        
        @tool
        async def get_portfolio_summary() -> str:
            """Get a summary of the user's portfolio including total value, holdings count, and allocations.
            
            Returns:
                JSON string containing portfolio summary statistics
            """
            try:
                # Use the existing portfolio service directly (now async)
                portfolios = await self.portfolio_service.list_portfolios(
                    user_id=self.current_user.user_id,
                    skip=0,
                    limit=100
                )
                
                # Filter for active portfolios only
                active_portfolios = [p.model_dump() for p in portfolios if p.sell_date is None]
                
                if not active_portfolios:
                    return json.dumps({"total_holdings": 0, "total_value": 0, "message": "No portfolio data found."})

                total_value = Decimal(0)
                sectors = {}
                asset_classes = {}
                top_holdings = []

                for holding in active_portfolios:
                    quantity = Decimal(holding.get("quantity", 0))
                    purchase_price = Decimal(str(holding.get("purchase_price", 0)))
                    value = quantity * purchase_price
                    total_value += value

                    # Aggregate by sector and asset class
                    sector = holding.get("sector", "Unknown")
                    sectors[sector] = sectors.get(sector, Decimal(0)) + value

                    asset_class = holding.get("asset_class", "Unknown")
                    asset_classes[asset_class] = asset_classes.get(asset_class, Decimal(0)) + value

                    top_holdings.append({
                        "symbol": holding.get("symbol"),
                        "security_name": holding.get("security_name"),
                        "value": float(value),
                        "percentage": 0.0
                    })

                # Calculate percentages and sort top holdings
                for h in top_holdings:
                    h["percentage"] = float((Decimal(h["value"]) / total_value * 100).quantize(Decimal("0.01"))) if total_value else 0

                top_holdings = sorted(top_holdings, key=lambda x: x["value"], reverse=True)[:5]

                result = {
                    "total_holdings": len(active_portfolios),
                    "total_value": float(total_value),
                    "sectors": {s: float(v) for s, v in sectors.items()},
                    "asset_classes": {ac: float(v) for ac, v in asset_classes.items()},
                    "top_holdings": top_holdings
                }
                
                return json.dumps(result, default=str)
                
            except Exception as e:
                logger.error(f"Error getting portfolio summary: {e}")
                return f"Error retrieving data: {str(e)}"
        
        return get_portfolio_summary





    # Async helper methods for inter-agent communication
    async def _get_portfolio_data_async(
        self, 
        symbol: Optional[str] = None,
        asset_class: Optional[str] = None,
        sector: Optional[str] = None,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get portfolio data asynchronously with optional filters."""
        try:
            portfolios = await self.portfolio_service.list_portfolios(
                user_id=self.current_user.user_id,
                skip=0,
                limit=100
            )
            
            # Convert to dict format and apply filters
            portfolio_data = [p.model_dump() for p in portfolios]
            
            # Apply filters efficiently
            if symbol:
                portfolio_data = [p for p in portfolio_data if p.get("symbol", "").upper() == symbol.upper()]
            if asset_class:
                portfolio_data = [p for p in portfolio_data if p.get("asset_class", "").lower() == asset_class.lower()]
            if sector:
                portfolio_data = [p for p in portfolio_data if p.get("sector", "").lower() == sector.lower()]
            if active_only:
                portfolio_data = [p for p in portfolio_data if p.get("sell_date") is None]
            
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error getting portfolio data: {e}")
            return []

    async def _get_portfolio_summary_async(self) -> Dict[str, Any]:
        """Get portfolio summary asynchronously."""
        try:
            portfolios = await self.portfolio_service.list_portfolios(
                user_id=self.current_user.user_id,
                skip=0,
                limit=100
            )
            
            # Filter for active portfolios only
            active_portfolios = [p.model_dump() for p in portfolios if p.sell_date is None]
            
            if not active_portfolios:
                return {"total_holdings": 0, "total_value": 0, "message": "No portfolio data found."}

            total_value = Decimal(0)
            sectors = {}
            asset_classes = {}
            top_holdings = []

            for holding in active_portfolios:
                quantity = Decimal(holding.get("quantity", 0))
                purchase_price = Decimal(str(holding.get("purchase_price", 0)))
                value = quantity * purchase_price
                total_value += value

                # Aggregate by sector and asset class
                sector = holding.get("sector", "Unknown")
                sectors[sector] = sectors.get(sector, Decimal(0)) + value

                asset_class = holding.get("asset_class", "Unknown")
                asset_classes[asset_class] = asset_classes.get(asset_class, Decimal(0)) + value

                top_holdings.append({
                    "symbol": holding.get("symbol"),
                    "security_name": holding.get("security_name"),
                    "value": float(value),
                    "percentage": 0.0
                })

            # Calculate percentages and sort top holdings
            for h in top_holdings:
                h["percentage"] = float((Decimal(h["value"]) / total_value * 100).quantize(Decimal("0.01"))) if total_value else 0

            top_holdings = sorted(top_holdings, key=lambda x: x["value"], reverse=True)[:5]

            return {
                "total_holdings": len(active_portfolios),
                "total_value": float(total_value),
                "sectors": {s: float(v) for s, v in sectors.items()},
                "asset_classes": {ac: float(v) for ac, v in asset_classes.items()},
                "top_holdings": top_holdings
            }
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {"error": str(e)}

    # Inter-agent communication methods
    async def get_user_data_for_analysis(self, data_type: str = "portfolio") -> Dict[str, Any]:
        """Get portfolio data for analysis by other agents."""
        try:
            if data_type == "portfolio":
                return {
                    "portfolio_data": await self._get_portfolio_data_async(),
                    "portfolio_summary": await self._get_portfolio_summary_async(),
                    "active_portfolios": await self._get_portfolio_data_async(active_only=True)
                }
            elif data_type == "all":
                return {
                    "portfolio_data": await self._get_portfolio_data_async(),
                    "portfolio_summary": await self._get_portfolio_summary_async(),
                    "active_portfolios": await self._get_portfolio_data_async(active_only=True)
                }
            else:
                return {"error": f"Unknown data type: {data_type}. Only 'portfolio' and 'all' are supported."}
        except Exception as e:
            logger.error(f"Error getting portfolio data for analysis: {e}")
            return {"error": str(e)}
    
    def get_user_context(self) -> Dict[str, Any]:
        """Get user context information for debugging."""
        return {
            "user_id": self.current_user.user_id if self.current_user else None,
            "has_portfolio_service": self.portfolio_service is not None,
            "agent_name": self.name,
            "tools_count": len(self.tools)
        }

